from __future__ import annotations
import os
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score, mean_absolute_percentage_error
from data_preprocessing import load_and_clean_data
from features import build_features
from modeling import group_train_val_split

PROGRAM_TYPE = "data_science"  
RAW_FILENAME = "creator_campaign_audience.csv"
CLEANED_FILENAME = "creator_campaign_audience.cleaned.csv"

def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]

def dataset_path(name: str) -> Path:
    return repo_root() / "dataset" / name

def main():
    df_clean, fix_report, cleaned_path = load_and_clean_data(
        raw_filename=RAW_FILENAME,
        cleaned_filename=CLEANED_FILENAME,
        # rare_min_count=10,  # optionally enable to fold rare categories
    )

    X, y, meta = build_features(
        df_clean=df_clean,
        program_type=PROGRAM_TYPE,
    )

    print(f"[OK] Features built. X shape: {X.shape} | y shape: {y.shape}")
    print("[INFO] Numeric features:", meta["numeric"])
    print("[INFO] Categorical features:", meta["categorical"])
    print("[INFO] Target:", meta["target"])
    
    artifacts_dir = repo_root() / "problems" / "creatorfit" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    (artifacts_dir / "X_head_preview.csv").write_text(
        pd.concat([X.head(20), y.head(20).rename("qualified_leads")], axis=1).to_csv(index=False)
    )
    y.head(200).to_csv(artifacts_dir / "y_head_preview.csv", index=False, header=["qualified_leads"])
    print(f"[OK] Previews saved in: {artifacts_dir}")

    groups = df_clean.loc[X.index, "creator_id"].astype(str)

    train_idx, val_idx, _, _ = group_train_val_split(
        X=X, y=y, groups=groups, val_size=0.2, random_state=42,
    )
    
    if 'creator_id' in X.columns:
        X = X.drop(columns=['creator_id'])
    
    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
    print(f"[OK] Split: train={X_train.shape}, val={X_val.shape}")
    print(f"[OK] Data already preprocessed - no additional encoding needed")

    model = LinearRegression()
    model.fit(X_train, y_train)
    print(f"[OK] Linear Regression trained successfully")
    print(f"[OK] Model coefficients shape: {model.coef_.shape}")
    print(f"[OK] Model intercept: {model.intercept_:.3f}")

    y_val_pred = model.predict(X_val)
    y_val_pred = np.clip(y_val_pred, a_min=0, a_max=None)

    y_true = y_val.values.astype(float)
    mae = mean_absolute_error(y_true, y_val_pred)

    try:
        from sklearn.metrics import root_mean_squared_error
        rmse = root_mean_squared_error(y_true, y_val_pred)
    except ImportError:
        from sklearn.metrics import mean_squared_error
        rmse = np.sqrt(mean_squared_error(y_true, y_val_pred))

    mape = (np.abs(y_true - y_val_pred) / np.maximum(1.0, y_true)).mean()
    r2 = r2_score(y_true, y_val_pred)

    print(f"[METRICS] MAE={mae:.2f}  RMSE={rmse:.2f}  MAPE={mape:.3f}  R2={r2:.3f}")

    import joblib
    
    default_ml_dir = Path(__file__).resolve().parent.parent / "ml"
    model_dir = Path(os.environ.get("MODEL_DIR", default_ml_dir))

    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "creatorfit_linear_model.pkl"
    joblib.dump(model, model_path)
    
    metadata = {
        "model_type": "LinearRegression",
        "features": meta,
        "program_type": PROGRAM_TYPE,
        "feature_names": list(X_train.columns),
        "performance": {"mae": mae, "rmse": rmse, "r2": r2, "mape": mape}
    }
    metadata_path = model_dir / "creatorfit_metadata.pkl"
    joblib.dump(metadata, metadata_path)
    
    print(f"\n[SAVED] Model saved to: {model_path}")
    print(f"[SAVED] Metadata saved to: {metadata_path}")
    print(f"[READY] Linear Regression model ready for production deployment!")

if __name__ == "__main__":
    main()