# Land Acquisition Delay Prediction — FastAPI + Frontend

Production-style MVP built around the provided **Random Forest + SHAP** notebook and exported `.joblib` model.

## What is included

- FastAPI backend with `/api/predict` and `/health`
- Automatic OpenAPI docs at `/docs`
- Model loaded once at application startup
- Exact 17 model input features from the notebook
- SHAP-based project-level top drivers
- Risk level and expected-delay mapping matching the notebook
- Recommendation logic matching the notebook
- Responsive HTML/CSS/JS frontend served by FastAPI
- Sample project button for quick demos

## Project structure

```text
land_acquisition_api/
├── backend/app/
│   ├── main.py
│   ├── model_service.py
│   └── schemas.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── model/
│   └── land_acquisition_random_forest.joblib
├── requirements.txt
├── run.bat
└── README.md
```

## Run locally

### Windows

```bash
run.bat
```

### Manual

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000` for the frontend and `http://127.0.0.1:8000/docs` for Swagger UI.

## API example

`POST /api/predict`

```json
{
  "project_type": "Highway",
  "state": "Rajasthan",
  "district": "Udaipur",
  "land_area_acres": 100,
  "affected_families": 50,
  "approval_days": 120,
  "pending_approvals": 2,
  "legal_disputes": 1,
  "compensation_paid_pct": 60,
  "documentation_complete_pct": 70,
  "notifications_pending": 1,
  "ownership_conflicts": 1,
  "rehabilitation_progress_pct": 50,
  "possession_progress_pct": 40,
  "stakeholder_response_days": 20,
  "inter_departmental_issues": 3,
  "historical_delay_rate_pct": 40
}
```

## Important model note

The supplied model was serialized with **scikit-learn 1.9.0**. The requirements intentionally pin that version because scikit-learn serialization is version-sensitive.

The SHAP percentages are relative contribution scores for an individual prediction, as described in the original notebook; they are not causal percentages.

## Next production upgrades

1. Add PostgreSQL for projects and prediction history.
2. Add authentication and role-based access.
3. Add admin dashboard with district/state filters and batch scoring.
4. Add model/version metadata and prediction logging.
5. Containerize with Docker and deploy backend separately from the frontend.
