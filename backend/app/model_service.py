from pathlib import Path
import warnings
import joblib
import numpy as np
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parents[2] / "model" / "land_acquisition_random_forest.joblib"

warnings.filterwarnings("ignore", category=UserWarning)

model = joblib.load(MODEL_PATH)
preprocessor = model.named_steps["preprocessor"]
classifier = model.named_steps["classifier"]

CATEGORICAL_FEATURES = ["project_type", "state", "district"]
NUMERIC_FEATURES = [c for c in preprocessor.feature_names_in_ if c not in CATEGORICAL_FEATURES]
FEATURES = list(preprocessor.feature_names_in_)

DRIVER_LABELS = {
    "legal_disputes": "Legal disputes",
    "compensation_paid_pct": "Compensation pending",
    "pending_approvals": "Pending approvals",
    "rehabilitation_progress_pct": "Rehabilitation",
    "documentation_complete_pct": "Documentation incomplete",
    "ownership_conflicts": "Ownership conflicts",
    "inter_departmental_issues": "Inter-departmental issues",
    "stakeholder_response_days": "Stakeholder response delay",
    "possession_progress_pct": "Possession progress",
    "notifications_pending": "Pending notifications",
    "approval_days": "Approval timeline",
    "historical_delay_rate_pct": "Historical delay rate",
    "land_area_acres": "Land area",
    "affected_families": "Affected families",
    "project_type": "Project type",
    "state": "State",
    "district": "District",
}


def risk_level(prob: float) -> str:
    if prob >= 0.75:
        return "HIGH"
    if prob >= 0.50:
        return "MEDIUM"
    return "LOW"


def expected_delay(prob: float) -> str:
    if prob >= 0.85:
        return "9–12 months"
    if prob >= 0.70:
        return "6–9 months"
    if prob >= 0.50:
        return "3–6 months"
    return "0–3 months"


def recommendations(project: dict) -> list[str]:
    actions = []
    if project["legal_disputes"] > 0:
        actions.append(f"Resolve {int(project['legal_disputes'])} legal case(s) on priority")
    if project["compensation_paid_pct"] < 70:
        actions.append("Accelerate compensation processing")
    if project["pending_approvals"] > 0:
        actions.append("Escalate pending approvals")
    if project["rehabilitation_progress_pct"] < 70:
        actions.append("Increase rehabilitation monitoring")
    if project["documentation_complete_pct"] < 70:
        actions.append("Complete and verify land documentation")
    if project["ownership_conflicts"] > 0:
        actions.append("Prioritize ownership-conflict resolution")
    if project["notifications_pending"] > 0:
        actions.append("Clear pending statutory notifications")
    if project["inter_departmental_issues"] > 2:
        actions.append("Set up inter-departmental escalation review")
    if not actions:
        actions.append("Continue routine monitoring and periodic review")
    return actions[:5]


def _get_delayed_shap_values(shap_output):
    delayed_idx = list(classifier.classes_).index("Delayed")
    if isinstance(shap_output, np.ndarray) and shap_output.ndim == 3:
        return shap_output[:, :, delayed_idx]
    if isinstance(shap_output, list):
        return shap_output[delayed_idx]
    return shap_output


def _original_feature_from_transformed(name: str) -> str:
    clean = name.split("__", 1)[-1]
    for col in CATEGORICAL_FEATURES:
        if clean == col or clean.startswith(col + "_"):
            return col
    return clean


def shap_drivers(input_df: pd.DataFrame, top_n: int = 4) -> list[dict]:
    try:
        import shap
        transformed = preprocessor.transform(input_df)
        dense = transformed.toarray() if hasattr(transformed, "toarray") else transformed
        explainer = shap.TreeExplainer(classifier)
        raw = explainer.shap_values(dense)
        values = _get_delayed_shap_values(raw)[0]
        names = preprocessor.get_feature_names_out()
        aggregated = {}
        for name, value in zip(names, values):
            original = _original_feature_from_transformed(name)
            aggregated[original] = aggregated.get(original, 0.0) + float(value)

        series = pd.Series(aggregated).sort_values(key=np.abs, ascending=False)
        positive = series[series > 0].sort_values(ascending=False).head(top_n)
        if positive.empty:
            positive = series.abs().sort_values(ascending=False).head(top_n)
        total = float(positive.abs().sum())
        if total == 0:
            return []
        percentages = (positive.abs() / total * 100).round().astype(int)
        diff = 100 - int(percentages.sum())
        if len(percentages):
            percentages.iloc[0] += diff
        return [
            {
                "feature": DRIVER_LABELS.get(feature, feature),
                "key": feature,
                "contribution_pct": int(pct),
                "direction": "increases delay risk" if float(positive.loc[feature]) > 0 else "reduces delay risk",
            }
            for feature, pct in percentages.items()
        ]
    except Exception:
        # Prediction remains available even if SHAP cannot initialize in a deployment environment.
        return []


def predict(project: dict) -> dict:
    input_df = pd.DataFrame([{key: project[key] for key in FEATURES}])
    delayed_idx = list(classifier.classes_).index("Delayed")
    probability = float(model.predict_proba(input_df)[0][delayed_idx])
    return {
        "delay_probability": probability,
        "risk_level": risk_level(probability),
        "expected_delay": expected_delay(probability),
        "top_drivers": shap_drivers(input_df),
        "recommendations": recommendations(project),
    }
