from background_task.models import Task


def revert_command(command):
    if command == 'hour':
        return Task.HOURLY
    elif command == 'week':
        return Task.WEEKLY
    elif command == 'day':
        return Task.DAILY
    elif command == 'month':
        return Task.EVERY_4_WEEKS
    elif command == 'never':
        return Task.NEVER
