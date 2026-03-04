"""
Fitness Tracker App - Flask Backend
RESTful API with user auth, meal logging, workout tracking, and nutrition analysis.
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, session, render_template, g

from nutrition_db import FOODS, search_foods, get_food

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DATABASE = os.path.join(os.path.dirname(__file__), "fitness.db")


# ── Database ──────────────────────────────────────────────

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DATABASE)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            servings REAL NOT NULL DEFAULT 1.0,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbs REAL NOT NULL,
            fat REAL NOT NULL,
            logged_at TEXT DEFAULT (datetime('now')),
            date TEXT DEFAULT (date('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            duration_minutes REAL,
            logged_at TEXT DEFAULT (datetime('now')),
            date TEXT DEFAULT (date('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE INDEX IF NOT EXISTS idx_meals_user_date ON meals(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_workouts_user_date ON workouts(user_id, date);
    """)
    db.close()


# ── Auth Helpers ──────────────────────────────────────────

def hash_password(password):
    salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}:{h}"


def verify_password(stored, password):
    salt, h = stored.split(":")
    return hashlib.sha256((salt + password).encode()).hexdigest() == h


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Not logged in"}), 401
        return f(*args, **kwargs)
    return decorated


# ── Auth Routes ───────────────────────────────────────────

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return jsonify({"error": "Username already taken"}), 409

    password_hash = hash_password(password)
    cursor = db.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash)
    )
    db.commit()

    session["user_id"] = cursor.lastrowid
    session["username"] = username
    return jsonify({"message": "Account created", "username": username}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "")

    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if not user or not verify_password(user["password_hash"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"message": "Logged in", "username": user["username"]})


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
def me():
    if "user_id" not in session:
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "username": session.get("username"),
        "user_id": session.get("user_id"),
    })


# ── Nutrition Search ──────────────────────────────────────

@app.route("/api/foods/search", methods=["GET"])
def food_search():
    query = request.args.get("q", "")
    results = search_foods(query)
    return jsonify([
        {"name": name, **data} for name, data in results
    ])


@app.route("/api/foods/<path:food_name>", methods=["GET"])
def food_detail(food_name):
    data = get_food(food_name)
    if not data:
        return jsonify({"error": "Food not found"}), 404
    return jsonify({"name": food_name, **data})


# ── Meals ─────────────────────────────────────────────────

@app.route("/api/meals", methods=["GET"])
@login_required
def get_meals():
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    db = get_db()
    rows = db.execute(
        "SELECT * FROM meals WHERE user_id = ? AND date = ? ORDER BY logged_at DESC",
        (session["user_id"], date)
    ).fetchall()
    meals = [dict(r) for r in rows]

    totals = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
    for m in meals:
        totals["calories"] += m["calories"]
        totals["protein"] += m["protein"]
        totals["carbs"] += m["carbs"]
        totals["fat"] += m["fat"]

    return jsonify({"date": date, "meals": meals, "totals": totals})


@app.route("/api/meals", methods=["POST"])
@login_required
def add_meal():
    data = request.get_json()
    food_name = data.get("food_name", "").strip().lower()
    servings = float(data.get("servings", 1))
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    food = get_food(food_name)
    if not food:
        return jsonify({"error": f"Food '{food_name}' not found in database"}), 404

    calories = round(food["calories"] * servings, 1)
    protein = round(food["protein"] * servings, 1)
    carbs = round(food["carbs"] * servings, 1)
    fat = round(food["fat"] * servings, 1)

    db = get_db()
    cursor = db.execute(
        """INSERT INTO meals (user_id, food_name, servings, calories, protein, carbs, fat, date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (session["user_id"], food_name, servings, calories, protein, carbs, fat, date)
    )
    db.commit()

    return jsonify({
        "id": cursor.lastrowid,
        "food_name": food_name,
        "servings": servings,
        "serving_size": food["serving"],
        "calories": calories,
        "protein": protein,
        "carbs": carbs,
        "fat": fat,
        "date": date,
    }), 201


@app.route("/api/meals/<int:meal_id>", methods=["DELETE"])
@login_required
def delete_meal(meal_id):
    db = get_db()
    db.execute(
        "DELETE FROM meals WHERE id = ? AND user_id = ?",
        (meal_id, session["user_id"])
    )
    db.commit()
    return jsonify({"message": "Meal deleted"})


# ── Workouts ──────────────────────────────────────────────

@app.route("/api/workouts", methods=["GET"])
@login_required
def get_workouts():
    date = request.args.get("date", datetime.now().strftime("%Y-%m-%d"))
    db = get_db()
    rows = db.execute(
        "SELECT * FROM workouts WHERE user_id = ? AND date = ? ORDER BY logged_at DESC",
        (session["user_id"], date)
    ).fetchall()
    return jsonify({"date": date, "workouts": [dict(r) for r in rows]})


@app.route("/api/workouts", methods=["POST"])
@login_required
def add_workout():
    data = request.get_json()
    exercise = data.get("exercise", "").strip()
    sets = data.get("sets")
    reps = data.get("reps")
    weight = data.get("weight")
    duration = data.get("duration_minutes")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))

    if not exercise:
        return jsonify({"error": "Exercise name required"}), 400

    db = get_db()
    cursor = db.execute(
        """INSERT INTO workouts (user_id, exercise, sets, reps, weight, duration_minutes, date)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (session["user_id"], exercise, sets, reps, weight, duration, date)
    )
    db.commit()

    return jsonify({
        "id": cursor.lastrowid,
        "exercise": exercise,
        "sets": sets,
        "reps": reps,
        "weight": weight,
        "duration_minutes": duration,
        "date": date,
    }), 201


@app.route("/api/workouts/<int:workout_id>", methods=["DELETE"])
@login_required
def delete_workout(workout_id):
    db = get_db()
    db.execute(
        "DELETE FROM workouts WHERE id = ? AND user_id = ?",
        (workout_id, session["user_id"])
    )
    db.commit()
    return jsonify({"message": "Workout deleted"})


# ── Stats / Charts ────────────────────────────────────────

@app.route("/api/stats/calories", methods=["GET"])
@login_required
def stats_calories():
    """Daily calorie totals over the past 30 days."""
    days = int(request.args.get("days", 30))
    db = get_db()
    rows = db.execute(
        """SELECT date, SUM(calories) as total_calories
           FROM meals WHERE user_id = ? AND date >= date('now', ?)
           GROUP BY date ORDER BY date""",
        (session["user_id"], f"-{days} days")
    ).fetchall()
    return jsonify([{"date": r["date"], "calories": round(r["total_calories"], 1)} for r in rows])


@app.route("/api/stats/macros", methods=["GET"])
@login_required
def stats_macros():
    """Daily macro breakdown over the past 30 days."""
    days = int(request.args.get("days", 30))
    db = get_db()
    rows = db.execute(
        """SELECT date,
                  SUM(protein) as protein,
                  SUM(carbs) as carbs,
                  SUM(fat) as fat
           FROM meals WHERE user_id = ? AND date >= date('now', ?)
           GROUP BY date ORDER BY date""",
        (session["user_id"], f"-{days} days")
    ).fetchall()
    return jsonify([{
        "date": r["date"],
        "protein": round(r["protein"], 1),
        "carbs": round(r["carbs"], 1),
        "fat": round(r["fat"], 1),
    } for r in rows])


@app.route("/api/stats/workouts", methods=["GET"])
@login_required
def stats_workouts():
    """Workout frequency over the past 30 days."""
    days = int(request.args.get("days", 30))
    db = get_db()
    rows = db.execute(
        """SELECT date, COUNT(*) as count
           FROM workouts WHERE user_id = ? AND date >= date('now', ?)
           GROUP BY date ORDER BY date""",
        (session["user_id"], f"-{days} days")
    ).fetchall()
    return jsonify([{"date": r["date"], "count": r["count"]} for r in rows])


# ── Frontend ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── Init & Run ────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
