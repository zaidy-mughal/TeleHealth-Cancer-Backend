from django.db import models


class ActionTypes(models.IntegerChoices):
    CREATE = 0, "Create"
    READ = 1, "Read"
    UPDATE = 2, "Update"
    DELETE = 3, "Delete"
    # LOGIN = 4, 'Login' TODO in future,
    # EXPORT = 5, 'Export'


class StatusChoices(models.IntegerChoices):
    SUCCESS = 0, "Success"
    FAILURE = 1, "Failure"
    PENDING = 2, "Pending"


class UserTypes(models.IntegerChoices):
    ADMIN = 0, "Admin"
    DOCTOR = 1, "Doctor"
    NURSE = 2, "Nurse"
    PATIENT = 3, "Patient"
