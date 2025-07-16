def get_django_weekday_numbers(days_of_week):
    """
    Convert DaysOfWeek choice values to Django week_day lookup values.
    Django week_day: Sunday=1, Monday=2, Tuesday=3, ..., Saturday=7
    DaysOfWeek choices: Monday=1, Tuesday=2, ..., Sunday=7
    """
    django_weekdays = []
    for day in days_of_week:
        if day == 7:
            django_weekdays.append(1)
        else:
            django_weekdays.append(day + 1)
    return django_weekdays
