# FitTrack — Fitness Tracking App

A full-stack web application where users create an account, log daily meals and workouts, and track their progress over time with interactive charts.

## Features

- **User Authentication**: Register and log in with username/password. Sessions persist across page reloads.
- **Meal Logging**: Search a built-in database of ~200 common foods, select one, choose a number of servings, and log it. The app multiplies per-serving macros (calories, protein, carbs, fat) by the number of servings and stores the computed totals.
- **Workout Tracking**: Log exercises with sets, reps, and weight (for strength training) or duration in minutes (for cardio).
- **Daily Summaries**: See total calories, protein, carbs, and fat for any day. Navigate between days with arrow buttons.
- **Progress Charts**: Four Chart.js visualizations:
  - Line chart showing daily calorie intake over the past 30 days
  - Stacked bar chart breaking down protein/carbs/fat per day
  - Bar chart showing workout frequency per day
  - Doughnut chart showing today's macro split
- **Responsive UI**: Works on desktop and mobile.

## Tech Stack

- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **API**: 12 RESTful endpoints

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create a new account |
| POST | `/api/auth/login` | Log in |
| POST | `/api/auth/logout` | Log out |
| GET | `/api/auth/me` | Check current session |
| GET | `/api/foods/search?q=` | Search nutrition database |
| GET | `/api/foods/<name>` | Get nutrition info for a food |
| GET | `/api/meals?date=` | Get meals for a date |
| POST | `/api/meals` | Log a meal |
| DELETE | `/api/meals/<id>` | Delete a meal |
| GET | `/api/workouts?date=` | Get workouts for a date |
| POST | `/api/workouts` | Log a workout |
| DELETE | `/api/workouts/<id>` | Delete a workout |
| GET | `/api/stats/calories` | Calorie totals (past 30 days) |
| GET | `/api/stats/macros` | Macro breakdown (past 30 days) |
| GET | `/api/stats/workouts` | Workout frequency (past 30 days) |

## Nutrition Database

Custom Python dictionary of ~200 common foods, each mapped to calories, protein (g), carbs (g), and fat (g) per serving. Categories include proteins, eggs & dairy, grains, fruits, vegetables, legumes & nuts, oils & condiments, snacks & prepared foods, drinks, and breakfast items.

## Running Locally

```bash
# Clone the repo
git clone https://github.com/hrashidzada/fitness-tracker.git
cd fitness-tracker

# Install Flask
pip install flask

# Run the app
python app.py
```

Then open `http://localhost:5000` in your browser.

## Project Structure

```
fitness-tracker/
├── app.py                # Flask server with all API endpoints
├── nutrition_db.py       # ~200 food nutrition database
├── templates/
│   └── index.html        # Single-page frontend (HTML/CSS/JS + Chart.js)
├── requirements.txt
└── README.md
```
