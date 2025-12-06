# Product Requirements Document (PRD)

## Diabetes Lifestyle Tracker (Web App)

---

## 1. Product Overview

**Product Name:** Diabetes Lifestyle Tracker

**Platform:** Web-based Python app using Streamlit

**Purpose:**
A simple, private web application that allows a single user to log and review daily lifestyle data relevant to diabetes management, including sleep, meals, and workouts.

**Target User:**
One individual (single-user app with no public accounts)

---

## 2. Goals & Objectives

### Primary Goals

* Enable fast and intuitive daily data entry
* Provide a clear historical view of lifestyle habits
* Maintain reliable, long-term data storage in a simple database (SQLite)

### Success Metrics

* User can complete daily logging in under 2 minutes
* 100% of entered data is successfully saved
* Historical data loads in under 2 seconds

---

## 3. Technology Stack

**App Framework:**

* **Streamlit** (Python library)

**Database Options:**

* **SQLite** (local file-based, simplest)
* Optional: **Supabase** (PostgreSQL) for cloud storage

**Hosting / Deployment Options:**

* Local machine
* Streamlit Community Cloud (free)
* Railway / Render (optional cloud deployment)

---

## 4. In-Scope Features

### 4.1 Sleep Tracking

The user can:

* Log wake-up time
* Log sleep time
* Edit existing entries

### 4.2 Meal Tracking

The user can:

* Add meals with:

  * Name/description
  * Time consumed
* Edit or delete meal entries

### 4.3 Workout Tracking

The user can:

* Add workouts with:

  * Workout name/type
  * Start time
  * Duration in minutes
* Edit or delete workout entries

### 4.4 Historical Review

The user can:

* View data by date
* Scroll through past days
* Filter entries by:

  * Date range
  * Category (sleep, meals, workouts)

---

## 5. Out of Scope (Version 1)

The following are explicitly excluded from this version:

* Multi-user accounts
* Social sharing
* Device integrations
* Medical or glucose sensor integrations
* Notifications and reminders

---

## 6. User Flow

1. User opens the app in a browser
2. User enters:

   * Sleep data
   * Meal entries
   * Workout entries
3. User reviews history in the same app interface

---

## 7. Functional Requirements

### 7.1 Data Handling

* All entries must be saved in SQLite in real time (or Supabase if chosen)
* All entries must be editable and deletable
* Data must be tied to a specific calendar date

### 7.2 Performance

* Page load time must be under 2 seconds
* Database queries must return results within 1 second

### 7.3 Reliability

* SQLite file must persist across app restarts
* Optional: Cloud database (Supabase) must handle backups

---

## 8. Data Model

### DailyLog

* `id` (INTEGER, primary key)
* `log_date` (TEXT, YYYY-MM-DD)

### SleepLog

* `id` (INTEGER, primary key)
* `log_date` (TEXT, YYYY-MM-DD)
* `wake_time` (TEXT, HH:MM)
* `sleep_time` (TEXT, HH:MM)

### MealLog

* `id` (INTEGER, primary key)
* `log_date` (TEXT, YYYY-MM-DD)
* `meal_name` (TEXT)
* `meal_time` (TEXT, HH:MM)

### WorkoutLog

* `id` (INTEGER, primary key)
* `log_date` (TEXT, YYYY-MM-DD)
* `workout_name` (TEXT)
* `start_time` (TEXT, HH:MM)
* `duration_minutes` (INTEGER)

---

## 9. UI / UX Requirements

### Interface

* Single-page app layout (Streamlit)
* Sections for Sleep, Meals, Workouts, and History
* Mobile-friendly
* Minimalist layout
* Large, easy-to-use input controls

---

## 10. Security Requirements

* App runs on HTTPS when deployed online (Streamlit Cloud or other hosting)
* Local SQLite file permissions must be secure
* No public user authentication required (single-user app)

---

## 11. Assumptions & Constraints

### Assumptions

* App is for a single trusted user
* No multi-user authentication is required
* User is comfortable running Python locally or deploying on Streamlit Cloud

### Constraints

* Must run entirely in Python (Streamlit)
* Must be deployable as a web app with minimal setup

---

## 12. Future Enhancements (Post-MVP)

* Graphs and trend analysis (e.g., sleep patterns, meal times, workout duration)
* Export data to CSV or Excel
* Optional integration with cloud databases (Supabase)
* Notifications or reminders for logging data
* Blood glucose logging

