# Diabetes Lifestyle Tracker

A minimalist Streamlit web app for a single user to log sleep, meals, and workouts in line with the accompanying PRD.

## Features

- Fast forms to capture sleep, meal, and workout data tied to specific dates
- Inline editing/deleting for every entry
- Meal tracking records carbohydrates (grams) alongside time and description
- SQLite storage that initializes automatically and persists locally
- History tab with date-range and category filters plus a grouped timeline view
- Delete any sleep, meal, or workout entry directly from the History tab
- One-click CSV export for whatever slice of history you filter
- Import CSV files (matching the export format) to bulk-load history entries
- Responsive one-page layout with accessible controls

## Project Structure

```
├── app.py              # Streamlit UI and interaction flows
├── database.py         # SQLite schema + CRUD helpers
├── data/               # SQLite file lives here once created
├── requirements.txt    # Python dependencies
└── Product Requirements Document.md
```

## Getting Started

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the app**
   ```bash
   streamlit run app.py
   ```
3. Open the provided local URL (typically `http://localhost:8501`).

### Importing history from CSV

1. Use the History tab’s **Download CSV** button to learn the required column names.
2. Populate or edit that CSV externally (leave irrelevant columns blank per row).
3. In the History tab, open “Import history from CSV,” choose your file, and click **Import entries**.
4. Valid rows are inserted (sleep rows overwrite by date, meals/workouts append new entries). Any issues per row are reported inline.

### Optional: Require an Access Code

Set a passcode to gate the UI if you want a lightweight layer of privacy:

- **Environment variable** (recommended locally): `export TRACKER_ACCESS_CODE="your-secret"`
- **Streamlit Cloud / production**: add `access_code = "your-secret"` to `.streamlit/secrets.toml`

When configured, the app prompts for the code before any data is shown. Leave both settings unset to disable the gate.

#### Picking values and using secrets

1. Choose a short alphanumeric string that only you know, e.g. `highfiber2025`. Avoid passwords you reuse elsewhere because this gate is meant for light privacy, not enterprise security.
2. **Local dev**: add `export TRACKER_ACCESS_CODE="highfiber2025"` to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.) or set it for a single session with the same command before running Streamlit.
3. **Streamlit Cloud**: create a folder named `.streamlit` (if it does not exist) and a file `.streamlit/secrets.toml` with:
   ```toml
   access_code = "highfiber2025"
   ```
   Deploy the app; Streamlit automatically injects that secret.
4. **Other hosts** (Railway, Render, etc.): define the env var `TRACKER_ACCESS_CODE` in the service dashboard.
5. To rotate the code, change the value in the environment or secrets file and restart the app.

The database file (`data/tracker.db`) is created automatically on first launch and persists between sessions. To reset, delete that file.

## Notes & Future Enhancements

- Works fully offline; move the SQLite file to a cloud volume for simple backups.
- Streamlit Community Cloud or any Python host can serve the app with minimal changes.
- Post-MVP ideas from the PRD (charts, exports, notifications, Supabase) can be layered on without restructuring the codebase.
