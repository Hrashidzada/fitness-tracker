# FitTrack — Fitness Tracking App

FitTrack is a full-stack web application that allows users to log meals and workouts, track daily nutrition, and visualize long-term fitness progress through interactive charts.

The goal of the project is to make nutrition and fitness tracking simple, structured, and data-driven.

---

## Key Features

- **User authentication system**  
  Secure registration and login with persistent sessions across page reloads.

- **Meal tracking with nutrition database**  
  Users can search and log foods from a built-in database of ~200 common items. Macro values (calories, protein, carbs, fat) are automatically calculated based on serving size.

- **Workout logging system**  
  Supports both strength training (sets, reps, weight) and cardio (duration-based tracking).

- **Daily nutrition summaries**  
  Users can view total macros for any selected day and navigate across dates.

- **Progress analytics dashboard**  
  Interactive charts visualize long-term trends in nutrition and fitness.

---

## Data Visualizations

Built using Chart.js:

- 30-day calorie intake trend (line chart)
- Daily macro breakdown (stacked bar chart)
- Workout frequency over time (bar chart)
- Current day macro distribution (doughnut chart)

---

## Tech Stack

- **Backend:** Python, Flask, SQLite  
- **Frontend:** HTML, CSS, JavaScript  
- **Visualization:** Chart.js  
- **Architecture:** REST API + single-page frontend

---

## System Design

FitTrack is structured as a lightweight REST-based full-stack application:

- **Backend (Flask API):** Handles authentication, meal/workout CRUD operations, and statistical aggregation.
- **Frontend (Single Page App):** Dynamic UI built with vanilla JavaScript for fast interactions without page reloads.
- **Nutrition Engine:** Custom dataset of ~200 foods with precomputed macros per serving.
- **Analytics Layer:** Aggregates user data into time-based summaries for visualization.

---

## My Role

I built the entire application end-to-end, including:

- Designing and implementing all REST API endpoints
- Building the authentication and session system
- Creating the nutrition database and macro calculation logic
- Developing the frontend UI and interactive dashboard
- Integrating Chart.js for data visualization
- Structuring the application for scalability and maintainability

---

## What I Learned

- Building full-stack applications with Flask
- Designing RESTful APIs and data models
- Handling authentication and session persistence
- Working with client-side data visualization
- Structuring and integrating a nutrition data system
