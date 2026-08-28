import os
import joblib
import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


DAGSHUB_REPO_OWNER = os.environ.get("DAGSHUB_REPO_OWNER", "TON_USERNAME")
DAGSHUB_REPO_NAME = os.environ.get("DAGSHUB_REPO_NAME", "churn-prediction-pipeline")

MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_REPO_OWNER}/{DAGSHUB_REPO_NAME}.mlflow"
os.environ["MLFLOW_TRACKING_USERNAME"] = DAGSHUB_REPO_OWNER
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.environ.get("DAGSHUB_TOKEN", "TON_TOKEN")

mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("churn-prediction")



def load_data(path="data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv"):
    df = pd.read_csv(path)

    
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df = df.dropna(subset=["TotalCharges"])

    df = df.drop(columns=["customerID"])

    return df


def preprocess(df):
    df = df.copy()
    target_col = "Churn"

    
    df[target_col] = df[target_col].map({"Yes": 1, "No": 0})

    
    cat_cols = df.select_dtypes(include="object").columns
    encoders = {}
    for col in cat_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        encoders[col] = le

    X = df.drop(columns=[target_col])
    y = df[target_col]

    return X, y, encoders



def train_and_log(X_train, X_test, y_train, y_test, model, model_name, params):
    with mlflow.start_run(run_name=model_name):
        mlflow.log_params(params)

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_proba),
        }
        mlflow.log_metrics(metrics)

        cm = confusion_matrix(y_test, y_pred)
        print(f"\n=== {model_name} ===")
        print("Matrice de confusion :\n", cm)
        for k, v in metrics.items():
            print(f"{k}: {v:.4f}")

        mlflow.sklearn.log_model(model, artifact_path="model")

        return model, metrics


def main():
    df = load_data()
    X, y, encoders = preprocess(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    candidates = {
        "logistic_regression": (
            LogisticRegression(max_iter=1000, random_state=42),
            {"model_type": "LogisticRegression", "max_iter": 1000},
        ),
        "random_forest": (
            RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42),
            {"model_type": "RandomForest", "n_estimators": 200, "max_depth": 8},
        ),
    }

    best_model = None
    best_f1 = -1
    best_name = None

    for name, (model, params) in candidates.items():
        trained_model, metrics = train_and_log(
            X_train_scaled, X_test_scaled, y_train, y_test, model, name, params
        )
        if metrics["f1_score"] > best_f1:
            best_f1 = metrics["f1_score"]
            best_model = trained_model
            best_name = name

    print(f"\nMeilleur modèle : {best_name} (F1 = {best_f1:.4f})")

    
    os.makedirs("model_output", exist_ok=True)
    joblib.dump(best_model, "model_output/model.pkl")
    joblib.dump(scaler, "model_output/scaler.pkl")
    joblib.dump(encoders, "model_output/encoders.pkl")
    joblib.dump(list(X.columns), "model_output/feature_order.pkl")

    print("Fichiers sauvegardés dans model_output/")
    print("-> A versionner ensuite avec DVC (dvc add model_output/model.pkl)")


if __name__ == "__main__":
    main()