import csv
import datetime as dt
import io
import os
from typing import Callable, Optional

import streamlit as st

import database as db


def _fmt_date(value: dt.date) -> str:
    return value.strftime("%Y-%m-%d")


def _parse_time(value: Optional[str], fallback: dt.time) -> dt.time:
    if value:
        try:
            return dt.datetime.strptime(value, "%H:%M").time()
        except ValueError:
            pass
    return fallback


def _time_to_str(value: dt.time) -> str:
    return value.strftime("%H:%M")


def _rerun() -> None:
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()


def _render_history_item(text: str, button_key: str, on_delete: Callable[[], None]) -> None:
    info_col, delete_col = st.columns([6, 1])
    info_col.write(text)
    if delete_col.button("Delete", key=button_key):
        on_delete()
        st.warning("Entry deleted.")
        _rerun()


def _delete_history_entry(category: str, row: dict) -> None:
    normalized = category.lower()
    if normalized == "sleep":
        db.delete_sleep_log(row["log_date"])
    elif normalized == "meals":
        db.delete_meal(row["id"])
    elif normalized == "workouts":
        db.delete_workout(row["id"])


def _history_to_csv(rows: list[dict]) -> bytes:
    """Serialize historical records to CSV for download."""
    if not rows:
        return b""
    fieldnames = sorted({key for row in rows for key in row.keys()})
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8")


def _get_access_code() -> Optional[str]:
    code = os.environ.get("TRACKER_ACCESS_CODE")
    if not code:
        try:
            code = st.secrets.get("access_code")  # type: ignore[attr-defined]
        except Exception:
            code = None
    if code:
        code = code.strip()
    return code or None


def _enforce_access_gate() -> None:
    """Prompt for an access code if one has been configured."""
    access_code = _get_access_code()
    if not access_code:
        return
    if st.session_state.get("is_authorized"):
        return

    with st.form("access_gate"):
        st.subheader("Enter Access Code")
        user_code = st.text_input("Passcode", type="password")
        submitted = st.form_submit_button("Unlock")

    if submitted:
        if user_code == access_code:
            st.session_state["is_authorized"] = True
            st.success("Access granted.")
            _rerun()
        else:
            st.error("Incorrect code. Try again.")

    st.stop()


st.set_page_config(
    page_title="Diabetes Lifestyle Tracker",
    page_icon="🩺",
    layout="wide",
)

db.init_db()

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600&family=IBM+Plex+Sans:wght@300;400;500&display=swap');
        html, body, [class*="css"]  {
            font-family: 'IBM Plex Sans', sans-serif;
            background: radial-gradient(circle at top, #f3fbff 0%, #f2f6f8 40%, #e4edf0 100%);
        }
        h1, h2, h3, h4 {
            font-family: 'Space Grotesk', sans-serif;
            letter-spacing: -0.02em;
        }
        .section-card {
            background: rgba(255, 255, 255, 0.85);
            padding: 1.5rem;
            border-radius: 18px;
            border: 1px solid rgba(86, 152, 195, 0.25);
            box-shadow: 0 25px 45px rgba(15, 40, 65, 0.08);
        }
        .stButton>button, .stForm button {
            border-radius: 999px;
            padding: 0.6rem 1.4rem;
            font-weight: 600;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Diabetes Lifestyle Tracker")
st.caption("Log sleep, meals, and workouts in under two minutes.")

_enforce_access_gate()

tab_sleep, tab_meals, tab_workouts, tab_history = st.tabs([
    "Sleep",
    "Meals",
    "Workouts",
    "History",
])


def _default_date() -> dt.date:
    return st.session_state.get("selected_date", dt.date.today())


def _store_date(value: dt.date) -> None:
    st.session_state["selected_date"] = value


with tab_sleep:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Sleep Tracking")
    selected_date = st.date_input("Log date", value=_default_date())
    _store_date(selected_date)
    existing = db.get_sleep_log(_fmt_date(selected_date))
    wake_default = _parse_time(existing.get("wake_time") if existing else None, dt.time(7, 0))
    sleep_default = _parse_time(existing.get("sleep_time") if existing else None, dt.time(23, 0))
    with st.form("sleep_form"):
        wake_time = st.time_input("Wake-up time", value=wake_default, step=dt.timedelta(minutes=5))
        sleep_time = st.time_input("Sleep time", value=sleep_default, step=dt.timedelta(minutes=5))
        submitted = st.form_submit_button("Save Sleep Log")
        if submitted:
            db.upsert_sleep_log(_fmt_date(selected_date), _time_to_str(wake_time), _time_to_str(sleep_time))
            st.success("Sleep entry saved.")
            _rerun()
    st.markdown("</div>", unsafe_allow_html=True)


with tab_meals:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Meals")
    with st.form("new_meal"):
        meal_date = st.date_input("Meal date", value=_default_date(), key="meal_date")
        meal_name = st.text_input("Meal description", placeholder="Breakfast, smoothie, etc.")
        meal_time = st.time_input("Meal time", value=dt.datetime.now().time().replace(second=0, microsecond=0))
        carbs_grams = st.number_input("Carbohydrates (g)", min_value=0, max_value=400, value=0, step=1)
        submit_meal = st.form_submit_button("Add Meal")
        if submit_meal:
            if not meal_name.strip():
                st.error("Meal description is required.")
            else:
                db.add_meal(_fmt_date(meal_date), meal_name.strip(), _time_to_str(meal_time), int(carbs_grams))
                st.success("Meal saved.")
                _rerun()
    st.markdown("</div>", unsafe_allow_html=True)


with tab_workouts:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Workouts")
    with st.form("new_workout"):
        workout_date = st.date_input("Workout date", value=_default_date(), key="workout_date")
        workout_name = st.text_input("Workout name", placeholder="Yoga, run, HIIT...")
        start_time = st.time_input("Start time", value=dt.time(7, 0))
        duration = st.number_input("Duration (minutes)", min_value=5, max_value=300, value=30)
        submit_workout = st.form_submit_button("Add Workout")
        if submit_workout:
            if not workout_name.strip():
                st.error("Workout name is required.")
            else:
                db.add_workout(
                    _fmt_date(workout_date),
                    workout_name.strip(),
                    _time_to_str(start_time),
                    int(duration),
                )
                st.success("Workout saved.")
                _rerun()
    st.markdown("</div>", unsafe_allow_html=True)


with tab_history:
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("History")
    default_range = (
        dt.date.today() - dt.timedelta(days=6),
        dt.date.today(),
    )
    range_input = st.date_input("Date range", default_range, key="history_range")
    if isinstance(range_input, (list, tuple)) and len(range_input) == 2:
        start_date, end_date = range_input
    else:
        start_date, end_date = default_range
    category = st.selectbox("Filter by category", ("All", "Sleep", "Meals", "Workouts"))
    normalized_category = category.lower()
    st.markdown("---")

    history = db.get_history(normalized_category, _fmt_date(start_date), _fmt_date(end_date))
    if not history:
        st.info("No entries in this range.")
    else:
        csv_payload = _history_to_csv(history)
        st.download_button(
            "Download CSV",
            data=csv_payload,
            file_name=f"history_{_fmt_date(start_date)}_{_fmt_date(end_date)}.csv",
            mime="text/csv",
        )
        if normalized_category == "sleep":
            for entry in history:
                text = (
                    f"🛌 {entry['log_date']}: asleep at {entry['sleep_time']} · wake at {entry['wake_time']}"
                )
                _render_history_item(
                    text,
                    f"hist_sleep_{entry['id']}",
                    lambda row=entry: _delete_history_entry("sleep", row),
                )
        elif normalized_category == "meals":
            for entry in history:
                carbs = entry.get("carbs_grams")
                carb_text = f" ({carbs} g carbs)" if carbs is not None else ""
                text = (
                    f"🍽️ {entry['log_date']}: {entry['meal_name']} at {entry['meal_time']}{carb_text}"
                )
                _render_history_item(
                    text,
                    f"hist_meal_{entry['id']}",
                    lambda row=entry: _delete_history_entry("meals", row),
                )
        elif normalized_category == "workouts":
            for entry in history:
                text = (
                    f"💪 {entry['log_date']}: {entry['workout_name']} at {entry['start_time']} ({entry['duration_minutes']} min)"
                )
                _render_history_item(
                    text,
                    f"hist_workout_{entry['id']}",
                    lambda row=entry: _delete_history_entry("workouts", row),
                )
        else:
            grouped = {}
            for row in history:
                grouped.setdefault(row["log_date"], []).append(row)
            for log_date, rows in grouped.items():
                st.markdown(f"### {log_date}")
                for row in rows:
                    if row["category"] == "sleep":
                        text = (
                            f"🛌 Sleep: asleep at {row['sleep_time']} · wake at {row['wake_time']}"
                        )
                    elif row["category"] == "meals":
                        carbs = row.get("carbs_grams")
                        carb_text = f" ({carbs} g carbs)" if carbs is not None else ""
                        text = (
                            f"🍽️ Meal: {row['meal_name']} at {row['meal_time']}{carb_text}"
                        )
                    else:
                        text = (
                            f"💪 Workout: {row['workout_name']} at {row['start_time']} ({row['duration_minutes']} min)"
                        )
                    _render_history_item(
                        text,
                        f"hist_all_{row['category']}_{row['id']}",
                        lambda r=row: _delete_history_entry(r["category"], r),
                    )
    st.markdown("</div>", unsafe_allow_html=True)
