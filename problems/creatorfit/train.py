# # problems/creatorfit/train.py
# from __future__ import annotations
# from pathlib import Path
# import pandas as pd
# import numpy as np
# from lightgbm import LGBMRegressor, early_stopping, log_evaluation, reset_parameter

# # from lightgbm import LGBMRegressor, early_stopping, log_evaluation
# from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# # Local modules
# from .data_preprocessing import load_and_clean_data
# from .features import build_features
# from .modeling import build_preprocessor, group_train_val_split

# # -----------------------------
# # Project config (edit as needed)
# # -----------------------------
# PROGRAM_TEXT = """
# Odin School Data Science program: Python, SQL, statistics, machine learning,
# feature engineering, model deployment, and career coaching for analytics roles.
# """
# TARGET_GEO = "IN"
# TARGET_LANG = "English"

# RAW_FILENAME = "creator_campaign_audience.csv"
# CLEANED_FILENAME = "creator_campaign_audience.cleaned.csv"

# def repo_root() -> Path:
#     # problems/creatorfit/train.py -> up 2 -> repo root
#     return Path(__file__).resolve().parents[2]

# def dataset_path(name: str) -> Path:
#     return repo_root() / "dataset" / name

# def main():
#     # 1) Load & clean (idempotent; will re-save cleaned CSV each run)
#     df_clean, fix_report, cleaned_path = load_and_clean_data(
#         raw_filename=RAW_FILENAME,
#         cleaned_filename=CLEANED_FILENAME,
#         # rare_min_count=10,  # optionally enable to fold rare categories
#     )

#     # Optional: reload from disk to simulate downstream usage
#     df_clean = pd.read_csv(cleaned_path)

#     # 2) Build features for modeling (pre-booking features only)
#     X, y, meta = build_features(
#         df_clean=df_clean,
#         program_text=PROGRAM_TEXT,
#         target_geo=TARGET_GEO,
#         target_lang=TARGET_LANG,
#     )

#     # 3) Quick summary (sanity before training)
#     print(f"[OK] Features built. X shape: {X.shape} | y shape: {y.shape}")
#     print("[INFO] Numeric features:", meta["numeric"])
#     print("[INFO] Categorical features:", meta["categorical"])
#     print("[INFO] Target:", meta["target"])

#     # 4) (Optional) Save interim feature set for inspection/debug
#     artifacts_dir = repo_root() / "artifacts"
#     artifacts_dir.mkdir(parents=True, exist_ok=True)
#     (artifacts_dir / "X_head_preview.csv").write_text(
#         pd.concat([X.head(20), y.head(20).rename("qualified_leads")], axis=1).to_csv(index=False)
#     )
#     y.head(200).to_csv(artifacts_dir / "y_head_preview.csv", index=False, header=["qualified_leads"])
#     print(f"[OK] Previews saved in: {artifacts_dir}")

#     # -----------------------------
#     # 5) Preprocess + group-aware split (no leakage)
#     # -----------------------------
#     preprocessor = build_preprocessor(
#         categorical=meta["categorical"],
#         numeric=meta["numeric"],
#     )

#     # group by creator_id so rows from the same creator don't leak into val set
#     groups = df_clean.loc[X.index, "creator_id"].astype(str)

#     train_idx, val_idx, _, _ = group_train_val_split(
#         X=X, y=y, groups=groups, val_size=0.2, random_state=42,
#     )
#     X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
#     y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
#     print(f"[OK] Split: train={X_train.shape}, val={X_val.shape}")

#     # Fit preprocessor on TRAIN only; transform both train/val
#     preprocessor.fit(X_train)
#     Xtr = preprocessor.transform(X_train)
#     Xva = preprocessor.transform(X_val)
#     print(f"[OK] Encoded -> X_train_enc={getattr(Xtr,'shape',None)}, X_val_enc={getattr(Xva,'shape',None)}")

#     # -----------------------------
#     # 6) MODEL (Poisson recipe – no log-transform of target)
#     # -----------------------------

#     lgb = LGBMRegressor(
#         objective="poisson",
#         n_estimators=3000,        # fewer estimators since we raise learning rate
#         learning_rate=0.08,       # was 0.02 → learn faster
#         num_leaves=31,            # default; okay for tabular
#         max_depth=-1,
#         subsample=0.9,
#         colsample_bytree=0.9,
#         reg_alpha=0.0,
#         reg_lambda=1.0,
#         min_data_in_leaf=30,      # a bit more conservative
#         min_gain_to_split=0.01,   # prune tiny, noisy splits
#         random_state=42,
#     )

#     # Early stopping via callbacks (works across LightGBM versions)
#     lgb.fit(
#         Xtr, y_train,
#         eval_set=[(Xva, y_val)],
#         eval_metric="poisson",
#         callbacks=[early_stopping(200), log_evaluation(50)]
#     )

#     best_iter = getattr(lgb, "best_iteration_", None)
#     print(f"[OK] Best iteration: {best_iter}")

#     # -----------------------------
#     # 7) Predict & evaluate on ORIGINAL units
#     # -----------------------------
#     y_val_pred = lgb.predict(Xva, num_iteration=best_iter)
#     y_val_pred = np.clip(y_val_pred, a_min=0, a_max=None)  # counts can't be negative

#     y_true = y_val.values.astype(float)
#     mae = mean_absolute_error(y_true, y_val_pred)

#     try:
#         from sklearn.metrics import root_mean_squared_error
#         rmse = root_mean_squared_error(y_true, y_val_pred)   # sklearn >= 1.4
#     except ImportError:
#         from sklearn.metrics import mean_squared_error
#         rmse = np.sqrt(mean_squared_error(y_true, y_val_pred))  # older sklearn

#     mape = (np.abs(y_true - y_val_pred) / np.maximum(1.0, y_true)).mean()
#     r2 = r2_score(y_true, y_val_pred)

#     print(f"[METRICS] MAE={mae:.2f}  RMSE={rmse:.2f}  MAPE={mape:.3f}  R2={r2:.3f}")

#     # -----------------------------
#     # 8) Feature importances (top 20)
#     # -----------------------------
#     cat_names = preprocessor.named_transformers_["cat"].get_feature_names_out(meta["categorical"])
#     num_names = np.array(meta["numeric"])
#     all_names = np.concatenate([cat_names, num_names], axis=0)

#     importances = lgb.feature_importances_
#     order = np.argsort(importances)[::-1]
#     top_k = min(20, len(all_names))

#     print("\n[TOP FEATURES]")
#     for i in order[:top_k]:
#         print(f"{all_names[i]:35s}  {importances[i]}")

# if __name__ == "__main__":
#     main()


# problems/creatorfit/train.py
from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
from lightgbm import LGBMRegressor, early_stopping, log_evaluation, reset_parameter
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
TARGET_GEO = "IN"
TARGET_LANG = "English"

RAW_FILENAME = "creator_campaign_audience.csv"
CLEANED_FILENAME = "creator_campaign_audience.cleaned.csv"

def repo_root() -> Path:
    # problems/creatorfit/train.py -> up 2 -> repo root
    return Path(__file__).resolve().parents[2]

def dataset_path(name: str) -> Path:
    return repo_root() / "dataset" / name

# -----------------------------
# LR-on-Plateau callback (Option B)
# -----------------------------
# def make_plateau_lr_cb(start_lr: float = 0.08, factor: float = 0.5, patience: int = 120, min_lr: float = 0.01):
#     """
#     Reduce learning rate by `factor` if no new best for `patience` rounds.
#     Resets the patience window after each LR drop. Never goes below `min_lr`.
#     IMPORTANT: Set early_stopping patience > plateau patience,
#     otherwise training may stop before LR has a chance to decay.
#     """
#     state = {"best_iter": -1, "lr": start_lr}

#     def _cb(env):
#         # At iteration 0, set initial LR explicitly
#         if env.iteration == 0:
#             reset_parameter({"learning_rate": state["lr"]})(env)
#             return

#         # Track new best iteration from eval metric
#         if env.best_iteration is not None and env.best_iteration > state["best_iter"]:
#             state["best_iter"] = env.best_iteration

#         # Plateau detection
#         no_improve = env.iteration - state["best_iter"]
#         if no_improve >= patience and state["lr"] > min_lr:
#             new_lr = max(min_lr, state["lr"] * factor)
#             if new_lr < state["lr"]:
#                 state["lr"] = new_lr
#                 reset_parameter({"learning_rate": state["lr"]})(env)
#                 # Reset the patience window after LR drop
#                 state["best_iter"] = env.iteration

#     return _cb
# def make_plateau_lr_cb(start_lr: float = 0.08, factor: float = 0.5, patience: int = 120, min_lr: float = 0.01):
#     """
#     Reduce learning rate by `factor` if no new best for `patience` rounds.
#     """
#     state = {"best_iter": -1, "lr": start_lr}

#     def _cb(env):
#         # At iteration 0, set initial LR explicitly
#         if env.iteration == 0:
#             env.model.reset_parameter({"learning_rate": state["lr"]})
#             return

#         # Track new best iteration
#         if env.best_iteration is not None and env.best_iteration > state["best_iter"]:
#             state["best_iter"] = env.best_iteration

#         # Plateau detection
#         no_improve = env.iteration - state["best_iter"]
#         if no_improve >= patience and state["lr"] > min_lr:
#             new_lr = max(min_lr, state["lr"] * factor)
#             if new_lr < state["lr"]:
#                 state["lr"] = new_lr
#                 env.model.reset_parameter({"learning_rate": state["lr"]})
#                 state["best_iter"] = env.iteration  # reset patience window

#     return _cb
def make_plateau_lr_cb(start_lr: float = 0.08, factor: float = 0.5, patience: int = 120, min_lr: float = 0.01):
    """
    Reduce learning rate by `factor` if the best validation metric hasn't improved
    for `patience` iterations. Works across LightGBM versions by reading
    env.evaluation_result_list instead of env.best_iteration.
    """
    state = {
        "lr": start_lr,
        "best_iter": -1,
        "best_score": None,   # will store the best val metric
        "is_higher_better": None,
    }

    def _get_val_metric(env):
        """
        Returns (score, is_higher_better). Picks the first validation metric found.
        env.evaluation_result_list is a list of tuples:
          (data_name, eval_name, result, is_higher_better)
        """
        for data_name, eval_name, result, is_higher_better in env.evaluation_result_list:
            # choose a validation set (anything not named 'training' / 'train')
            if "train" not in data_name and "training" not in data_name:
                return float(result), bool(is_higher_better)
        return None, None

    def _is_better(curr, best, higher_better):
        if best is None:
            return True
        return (curr > best) if higher_better else (curr < best)

    def _cb(env):
        # iteration index (0-based inside callback); use +1 for human-friendly if needed
        iter_idx = env.iteration

        # At iteration 0, set initial LR explicitly
        if iter_idx == 0:
            # reset_parameter is available via env.model in all versions
            env.model.reset_parameter({"learning_rate": state["lr"]})
            # initialize best from the first val metric (if any)
            score, higher = _get_val_metric(env)
            if score is not None:
                state["best_score"] = score
                state["is_higher_better"] = higher
                state["best_iter"] = iter_idx
            return

        # Read current validation metric
        score, higher = _get_val_metric(env)
        if score is None:
            # No validation metric available; nothing to do
            return

        if state["is_higher_better"] is None:
            state["is_higher_better"] = higher

        # Update best?
        if _is_better(score, state["best_score"], state["is_higher_better"]):
            state["best_score"] = score
            state["best_iter"] = iter_idx
            return

        # Plateau?
        no_improve = iter_idx - state["best_iter"]
        if no_improve >= patience and state["lr"] > min_lr:
            new_lr = max(min_lr, state["lr"] * factor)
            if new_lr < state["lr"]:
                state["lr"] = new_lr
                env.model.reset_parameter({"learning_rate": state["lr"]})
                # reset patience window after LR drop
                state["best_iter"] = iter_idx

    return _cb


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
        objective="poisson",      # count-aware objective
        n_estimators=3000,
        learning_rate=0.08,       # initial LR; will be reset by callback at iter 0
        num_leaves=31,
        max_depth=-1,
        subsample=0.9,
        colsample_bytree=0.9,
        reg_alpha=0.0,
        reg_lambda=1.0,
        min_data_in_leaf=30,
        min_gain_to_split=0.01,
        random_state=42,
    )

    # Early stopping patience MUST be > plateau patience so LR can drop first
    plateau_cb = make_plateau_lr_cb(
        start_lr=0.08,
        factor=0.5,      # halve LR on plateau
        patience=120,    # plateau patience
        min_lr=0.01
    )

    lgb.fit(
        Xtr, y_train,
        eval_set=[(Xva, y_val)],
        eval_metric="poisson",
        callbacks=[
            early_stopping(300),   # ES patience ≈ 2.5x plateau patience
            log_evaluation(50),
            plateau_cb,            # Reduce LR on plateau
        ],
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

    # Version-safe RMSE
    try:
        from sklearn.metrics import root_mean_squared_error
        rmse = root_mean_squared_error(y_true, y_val_pred)   # sklearn >= 1.4
    except ImportError:
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

if __name__ == "__main__":
    main()
