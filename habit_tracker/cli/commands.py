import click
from tabulate import tabulate
from habit_tracker.sqlite_repository import SQLiteHabitRepository
from habit_tracker.services import HabitService, AnalyticsService

@click.group()
def cli():
    """Habit‐Tracker CLI."""
    pass

@cli.command()
@click.option("--name", "-n", required=True, help="Name of the habit.")
@click.option("--periodicity", "-p", type=click.Choice(["daily","weekly"]), required=True)
@click.option("--category", "-c", default="general", help="Category of the habit.")
def create(name, periodicity, category):
    """Create a new habit."""
    repo = SQLiteHabitRepository()
    svc = HabitService(repo)
    habit = svc.create_habit(name, periodicity, category)
    click.echo(f"Created habit: {habit.name} (ID: {habit.id})")

@cli.command()
@click.argument("habit_id", type=int)
def complete(habit_id):
    """Mark an existing habit as completed."""
    repo = SQLiteHabitRepository()
    svc = HabitService(repo)
    try:
        svc.record_completion(habit_id)
        click.echo(f"Recorded completion for habit ID {habit_id}")
    except ValueError as e:
        click.echo(f"Error: {e}")

@cli.command(name="list")
@click.option(
    "--periodicity", "-p",
    type=click.Choice(["daily", "weekly"]),
    help="Only show habits with this periodicity."
)
def _list(periodicity):
    """
    List all habits, optionally filtering by periodicity.
    """
    repo = SQLiteHabitRepository()
    svc = HabitService(repo)
    habits = svc.list_habits()
    
    if not habits:
        click.echo("No habits found; initializing database with defaults.")
        ctx = click.get_current_context()
        ctx.invoke(reset)
        habits = svc.list_habits()

    if periodicity:
        habits = [h for h in habits if h.periodicity == periodicity]

    table = [
        [h.id, h.name, h.periodicity, h.category, h.created.date().isoformat(), len(h.completions)]
        for h in habits
    ]
    headers = ["ID", "Name", "Periodicity", "Category", "Created", "Completions"]
    click.echo(tabulate(table, headers=headers, tablefmt="plain"))

@cli.command()
@click.option("--id", "habit_id", type=int, help="Analyze a single habit by ID.")
@click.option("--longest", is_flag=True, help="Show longest streak.")
@click.option("--current", is_flag=True, help="Show current streak.")
@click.option("--rate", "completion_rate", is_flag=True, help="Show completion rate.")
@click.option("--weekly-report", is_flag=True, help="Show this week's report.")
@click.option("--monthly-report", is_flag=True, help="Show this month's report.")
def analyze(habit_id, longest, current, completion_rate, weekly_report, monthly_report):
    """Run analytics."""
    repo = SQLiteHabitRepository()
    svc = HabitService(repo)
    analytics = AnalyticsService()
    habits = svc.list_habits()

    if habit_id:
        h = repo.get_by_id(habit_id)
        if not h:
            return click.echo(f"No habit with ID {habit_id}")
        if longest:
            click.echo(f"Longest streak: {analytics.longest_streak(h)}")
        if current:
            click.echo(f"Current streak: {analytics.current_streak(h)}")
        if completion_rate:
            click.echo(f"Completion rate: {analytics.completion_rate(h)*100:.2f}%")
        if weekly_report or monthly_report:
            click.echo("Weekly/monthly report applies to all habits only.")
    else:
        if longest:
            click.echo(f"Max streak (all habits): {max(analytics.longest_streak(h) for h in habits)}")
        if current:
            click.echo("Current streaks:")
            for h in habits:
                click.echo(f"- {h.name}: {analytics.current_streak(h)}")
        if completion_rate:
            avg = sum(analytics.completion_rate(h) for h in habits)/len(habits) if habits else 0
            click.echo(f"Avg completion rate: {avg*100:.2f}%")
        if weekly_report:
            rpt = analytics.report(habits, "weekly")
            click.echo("Weekly report:")
            for name, done in rpt.items():
                click.echo(f"- {name}: {'✅' if done else '❌'}")
        if monthly_report:
            rpt = analytics.report(habits, "monthly")
            click.echo("Monthly report:")
            for name, done in rpt.items():
                click.echo(f"- {name}: {'✅' if done else '❌'}")

@cli.command()
@click.argument("habit_id", type=int)
def delete(habit_id):
    """Delete a habit by ID."""
    repo = SQLiteHabitRepository()
    repo.delete(habit_id)
    click.echo(f"Deleted habit ID {habit_id}")

@cli.command()
def reset():
    """Wipe and reinitialize the database."""
    repo = SQLiteHabitRepository()
    import os
    if os.path.exists(repo.db_path):
        os.remove(repo.db_path)
    repo._initialize_db()

    repo.add_defaults()

@cli.command(name='details')
@click.argument("habit_id", type=int)
def details(habit_id):
    """
    Show detailed info for a habit: creation time and all completion timestamps.
    """
    repo = SQLiteHabitRepository()
    habit = repo.get_by_id(habit_id)
    if not habit:
        return click.echo(f"No habit with ID {habit_id}")

    click.echo(f"ID:         {habit.id}")
    click.echo(f"Name:       {habit.name}")
    click.echo(f"Periodicity:{habit.periodicity}")
    click.echo(f"Category:   {habit.category}")
    click.echo(f"Created:    {habit.created.isoformat()}")

    if habit.completions:
        click.echo("Completions:")
        for comp in habit.completions:
            click.echo(f"  • {comp.timestamp.isoformat()}")
    else:
        click.echo("No completions yet.")

if __name__ == "__main__":
    cli()