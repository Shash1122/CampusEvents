#events/models.py
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class College(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.SlugField(unique=True)  # e.g., "nitk", "iiitd"
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Student(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="students", db_index=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    roll_number = models.CharField(max_length=50)

    class Meta:
        unique_together = [
            ("college", "email"),
            ("college", "roll_number"),
        ]
        indexes = [
            models.Index(fields=["college", "roll_number"]),
            models.Index(fields=["college", "email"]),
        ]

    def __str__(self):
        return f"{self.name} [{self.roll_number}]"


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="events", db_index=True)
    code = models.SlugField()  # short, human-friendly code, unique inside a college
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = [("college", "code")]
        indexes = [models.Index(fields=["college", "start_time"])]

    def __str__(self):
        return f"{self.title} ({self.code})"


class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="registrations", db_index=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="registrations", db_index=True)
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("event", "student")]
        indexes = [
            models.Index(fields=["event", "student"]),
            models.Index(fields=["student", "event"]),
        ]


class Attendance(models.Model):
    # One attendance per registration
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name="attendance")
    present = models.BooleanField(default=True)
    checkin_time = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name="feedback")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
