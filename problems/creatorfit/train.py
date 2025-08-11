from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor, early_stopping, log_evaluation, reset_parameter

# from lightgbm import LGBMRegressor, early_stopping, log_evaluation
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# Local modules
from .data_preprocessing import load_and_clean_data
from .features import build_features
from .modeling import build_preprocessor, group_train_val_split

# -----------------------------
# Project config (edit as needed)
# -----------------------------
PROGRAM_TEXT = """
Odin School Data Science program: Python, SQL, statistics, machine learning,
feature engineering, model deployment, and career coaching for analytics roles.
"""
TARGET_GEO = "INDIA"  # Match the realistic dataset geography format
TARGET_LANG = "English"

RAW_FILENAME = "creator_campaign_audience_realistic.csv"  # Use the realistic dataset
CLEANED_FILENAME = "creator_campaign_audience_realistic.cleaned.csv"

def repo_root() -> Path:
    # problems/creatorfit/train.py -> up 2 -> repo root
    return Path(__file__).resolve().parents[2]

def dataset_path(name: str) -> Path:
    return repo_root() / "dataset" / name

def main():
    # 1) Load & clean (idempotent; will re-save cleaned CSV each run)
    df_clean, fix_report, cleaned_path = load_and_clean_data(
        raw_filename=RAW_FILENAME,
        cleaned_filename=CLEANED_FILENAME,
        # rare_min_count=10,  # optionally enable to fold rare categories
    )

    # Optional: reload from disk to simulate downstream usage
    df_clean = pd.read_csv(cleaned_path)

    # 2) Build features for modeling (pre-booking features only)
    X, y, meta = build_features(
        df_clean=df_clean,
        program_text=PROGRAM_TEXT,
        target_geo=TARGET_GEO,
        target_lang=TARGET_LANG,
    )

    # 3) Quick summary (sanity before training)
    print(f"[OK] Features built. X shape: {X.shape} | y shape: {y.shape}")
    print("[INFO] Numeric features:", meta["numeric"])
    print("[INFO] Categorical features:", meta["categorical"])
    print("[INFO] Target:", meta["target"])

    # 4) (Optional) Save interim feature set for inspection/debug
    artifacts_dir = repo_root() / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "X_head_preview.csv").write_text(
        pd.concat([X.head(20), y.head(20).rename("qualified_leads")], axis=1).to_csv(index=False)
    )
    y.head(200).to_csv(artifacts_dir / "y_head_preview.csv", index=False, header=["qualified_leads"])
    print(f"[OK] Previews saved in: {artifacts_dir}")

    # -----------------------------
    # 5) Preprocess + group-aware split (no leakage)
    # -----------------------------
    preprocessor = build_preprocessor(
        categorical=meta["categorical"],
        numeric=meta["numeric"],
    )

    # group by creator_id so rows from the same creator don't leak into val set
    groups = df_clean.loc[X.index, "creator_id"].astype(str)

    train_idx, val_idx, _, _ = group_train_val_split(
        X=X, y=y, groups=groups, val_size=0.2, random_state=42,
    )
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    print(f"[OK] Split: train={X_train.shape}, val={X_val.shape}")

    # Fit preprocessor on TRAIN only; transform both train/val
    preprocessor.fit(X_train)
    Xtr = preprocessor.transform(X_train)
    Xva = preprocessor.transform(X_val)
    print(f"[OK] Encoded -> X_train_enc={getattr(Xtr,'shape',None)}, X_val_enc={getattr(Xva,'shape',None)}")

    # -----------------------------
    # 6) MODEL (Poisson recipe – no log-transform of target)
    # -----------------------------

    lgb = LGBMRegressor(
        objective="poisson",
        n_estimators=3000,        # fewer estimators since we raise learning rate
        learning_rate=0.08,       # was 0.02 → learn faster
        num_leaves=31,            # default; okay for tabular
        max_depth=-1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=1.0,
        min_data_in_leaf=30,      # a bit more conservative
        min_gain_to_split=0.01,   # prune tiny, noisy splits
        random_state=42,
    )

    # Early stopping via callbacks (works across LightGBM versions)
    lgb.fit(
        Xtr, y_train,
        eval_set=[(Xva, y_val)],
        eval_metric="poisson",
        callbacks=[early_stopping(200), log_evaluation(50)]
    )

    best_iter = getattr(lgb, "best_iteration_", None)
    print(f"[OK] Best iteration: {best_iter}")

    # -----------------------------
    # 7) Predict & evaluate on ORIGINAL units
    # -----------------------------
    y_val_pred = lgb.predict(Xva, num_iteration=best_iter)
    y_val_pred = np.clip(y_val_pred, a_min=0, a_max=None)  # counts can't be negative

    y_true = y_val.values.astype(float)
    mae = mean_absolute_error(y_true, y_val_pred)

    try:
        from sklearn.metrics import root_mean_squared_error
        rmse = root_mean_squared_error(y_true, y_val_pred)   # sklearn >= 1.4
    except ImportError:
        from sklearn.metrics import mean_squared_error
        rmse = np.sqrt(mean_squared_error(y_true, y_val_pred))  # older sklearn

    mape = (np.abs(y_true - y_val_pred) / np.maximum(1.0, y_true)).mean()
    r2 = r2_score(y_true, y_val_pred)

    print(f"[METRICS] MAE={mae:.2f}  RMSE={rmse:.2f}  MAPE={mape:.3f}  R2={r2:.3f}")

    # -----------------------------
    # 8) Feature importances (top 20)
    # -----------------------------
    cat_names = preprocessor.named_transformers_["cat"].get_feature_names_out(meta["categorical"])
    num_names = np.array(meta["numeric"])
    all_names = np.concatenate([cat_names, num_names], axis=0)

    importances = lgb.feature_importances_
    order = np.argsort(importances)[::-1]
    top_k = min(20, len(all_names))

    print("\n[TOP FEATURES]")
    for i in order[:top_k]:
        print(f"{all_names[i]:35s}  {importances[i]}")
    
    # -----------------------------
    # 9) Save the trained model and preprocessor for production use
    # -----------------------------
    import joblib
    
    model_dir = repo_root() / "models"
    model_dir.mkdir(exist_ok=True)
    
    # Save the trained model
    model_path = model_dir / "creatorfit_lgb_model.pkl"
    joblib.dump(lgb, model_path)
    
    # Save the preprocessor (needed for new predictions)
    preprocessor_path = model_dir / "creatorfit_preprocessor.pkl"
    joblib.dump(preprocessor, preprocessor_path)
    
    # Save metadata for easy loading
    metadata = {
        "model_type": "LGBMRegressor",
        "features": meta,
        "target_geo": TARGET_GEO,
        "target_lang": TARGET_LANG,
        "program_text": PROGRAM_TEXT,
        "best_iteration": best_iter,
        "performance": {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape}
    }
    metadata_path = model_dir / "creatorfit_metadata.pkl"
    joblib.dump(metadata, metadata_path)
    
    print(f"\n[SAVED] Model saved to: {model_path}")
    print(f"[SAVED] Preprocessor saved to: {preprocessor_path}")
    print(f"[SAVED] Metadata saved to: {metadata_path}")
    print(f"[READY] Model ready for production deployment!")

if __name__ == "__main__":
    main()