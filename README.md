# Habit Tracking App
A command-line interface (CLI) application for defining, tracking, and analyzing daily or weekly habits. Built in Python with a clean separation of concerns:
- **Models**: Data classes for habits and completion records.
- **Repository**: SQLite-backend persistence layer.
- **Services**: Business logic for habit workflows and analytics.
- **CLI**: Click-based commands to interact with the application.

# Prerequisites
- Python 3.7 or later.
- Git (to clone the repo)

# Installation
1. **Clone the repo**
    ```
    git clone
    cd habit_tracker
    ```

2. **Create a virtual environment**
- macOs/Linux
    python3 -m venv .venv
    source .venv/bin/activate

- Windows (PowerShell)
    ```
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    ```

- Windows (CMD)
    ```
    python -m venv .venv
    .\.venv\Scripts\activate.bat
    ```

3. **Install dependencies**
    ```
    pip install -r requirements.txt
    ```

# Usage
All commands share the same invocation patter. Below are the main ones with examples.

# List habits
Show all habits or filter by preiodicity:
    ```
    python -m habit_tracker.cli.commands list
    python -m habit_tracker.cli.commands list --periodicity daily
    ```

# Create a habit
Add a new habit:
    ```
    python -m habit_tracker.cli.commands create \
        --name "Exercise" \
        --periodicity daily \
        --category health
    ```

# Complete a habit 
Mark a habit as done:
    ```
    python -m habit_tracker.cli.commands complete 5
    ```

# Show habit details
View creation time and all completion timestamps:
    ```
    python -m habit_tracker.cli.commands details 5
    ```

# Analyze habits
Run analytics accross all habits or a single habit by ID:
1. **Overall analytics**:
    ```
    python -m habit_tracker.cli.commands analyze --longest --rate --weekly-report
    ```

2. **Single habit analytics**:
    ```
    python -m habit_tracker.cli.commands analyze --id 5 --longest --current
    ```

# Delete a habit
Remove a habit and its completions:
    ```
    python -m habit_tracker.cli.commands delete 5
    ```

# Reset database 
Clear and resend defaults:
    ```
    python -m habit_tracker.cli.commands reset
    ```

# Testing
Run the full test suite with pytest
    ```
    pytest
    ```
This covers:
- Repository CRUD and seeding
- Analytics calculations (streaks, rates, reports)
- End-to-end CLI flows