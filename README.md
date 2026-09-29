# FitBuddy - AI Fitness Plan Generator

FitBuddy is a FastAPI web application that creates personalized workout plans and general nutrition and recovery guidance with Google Gemini. It stores user profiles, generated plans, and feedback in a local SQLite database.

## Features

- Collects fitness goals, experience, available equipment, schedule, dietary preferences, and limitations.
- Generates a workout plan and nutrition guidance using Gemini.
- Saves plans locally and lets users submit feedback to update a plan.
- Provides a saved-users page and a health endpoint.
- Renders the interface with Jinja2 templates and local CSS.

## Project structure

```text
app/                    FastAPI routes, validation, database, and Gemini logic
templates/              FitBuddy Jinja2 pages
static/                 CSS and gym background image
.env.example            Safe environment-variable template
requirements.txt        Python dependencies
```

## Requirements

Python 3.10 or newer. From PowerShell in the project directory:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set `GEMINI_API_KEY` to a key created in Google AI Studio. Keep `.env` private; it is excluded from Git. The app uses `gemini-3.7-flash` for workout generation, with `gemini-3.5-flash-lite` as the fallback and for nutrition guidance. Model IDs can be changed with the `GEMINI_WORKOUT_MODEL`, `GEMINI_WORKOUT_FALLBACK_MODEL`, and `GEMINI_NUTRITION_MODEL` environment variables.

## Run

```powershell
uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000>. Interactive API documentation is at <http://127.0.0.1:8000/docs>.

## Routes

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Fitness profile form |
| POST | `/generate` | Validate profile and generate a plan |
| GET | `/plan/{plan_id}` | View a saved plan |
| GET | `/feedback/{plan_id}` | Show the feedback form |
| POST | `/feedback/{plan_id}` | Update a plan from feedback |
| GET | `/users` | List saved profiles and plans |
| GET | `/view-all-users` | Assignment-compatible saved-users page |
| GET | `/health` | Health status JSON |

The SQLite database is created locally as `fitbuddy.db`. Do not commit it because it can contain personal information. FitBuddy provides general wellness information, not medical advice.
