import re
from click.testing import CliRunner
from habit_tracker.cli.commands import cli

def test_cli_workflow_default_and_filters(tmp_path):
    """
    Test the end-to-end CLI workflow including reset, list (all and filtered),
    create, complete, show, analyze, delete, and reset again.
    """
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=str(tmp_path)):
        # 1. Reset database to add defaults
        result = runner.invoke(cli, ['reset'])
        assert result.exit_code == 0

        # 2. List all habits (should show 5 seeded habits + header)
        result = runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        lines = result.output.strip().splitlines()
        # header + 5 rows
        assert len(lines) == 6

        # 3. Filter by daily
        result = runner.invoke(cli, ['list', '--periodicity', 'daily'])
        assert result.exit_code == 0
        daily_lines = result.output.strip().splitlines()[1:]
        assert all('daily' in line.lower() for line in daily_lines)

        # 4. Filter by weekly
        result = runner.invoke(cli, ['list', '-p', 'weekly'])
        assert result.exit_code == 0
        weekly_lines = result.output.strip().splitlines()[1:]
        assert all('weekly' in line.lower() for line in weekly_lines)

        # 5. Create a new habit
        result = runner.invoke(cli, ['create', '--name', 'Exercise', '--periodicity', 'daily'])
        assert result.exit_code == 0
        assert 'Created habit: Exercise' in result.output
        match = re.search(r'ID: (\d+)', result.output)
        assert match, "Expected an ID in create output"
        new_id = match.group(1)

        # 6. Complete the new habit
        result = runner.invoke(cli, ['complete', new_id])
        assert result.exit_code == 0
        assert f'Recorded completion for habit ID {new_id}' in result.output

        # 7. Show detailed info for the new habit
        result = runner.invoke(cli, ['details', new_id])
        assert result.exit_code == 0
        assert 'Completions:' in result.output

        # 8. Analyze longest streak across all habits
        result = runner.invoke(cli, ['analyze', '--longest'])
        assert result.exit_code == 0
        assert 'Max streak' in result.output or 'Longest streak' in result.output

        # 9. Analyze longest streak for the new habit
        result = runner.invoke(cli, ['analyze', '--id', new_id, '--longest'])
        assert result.exit_code == 0
        assert 'Longest streak' in result.output

        # 10. Delete the new habit
        result = runner.invoke(cli, ['delete', new_id])
        assert result.exit_code == 0
        assert f'Deleted habit ID {new_id}' in result.output
