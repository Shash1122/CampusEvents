#events/serializers.py
from rest_framework import serializers
from .models import College, Student, Event, Registration, Attendance, Feedback

# events/serializers.py

class RegistrationCreateSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    event_id = serializers.UUIDField()

    def validate(self, data):
        from .models import Student, Event, Registration
        try:
            student = Student.objects.get(id=data["student_id"])
            event = Event.objects.get(id=data["event_id"])
        except (Student.DoesNotExist, Event.DoesNotExist):
            raise serializers.ValidationError("Invalid student_id or event_id.")

        # Ensure student & event belong to same college
        if student.college_id != event.college_id:
            raise serializers.ValidationError("Student and Event must be in the same college.")

        # ✅ Enforce event capacity (if set)
        if event.capacity is not None:
            reg_count = Registration.objects.filter(event=event).count()
            if reg_count >= event.capacity:
                raise serializers.ValidationError("Event capacity reached. Cannot register more students.")

        data["student"] = student
        data["event"] = event
        return data

    def create(self, validated):
        from .models import Registration
        obj, created = Registration.objects.get_or_create(
            student=validated["student"], event=validated["event"]
        )
        return obj

class CheckinSerializer(serializers.Serializer):
    registration_id = serializers.UUIDField(required=False)
    student_id = serializers.UUIDField(required=False)
    event_id = serializers.UUIDField(required=False)

    def validate(self, data):
        from .models import Registration, Student, Event
        reg = None
        if data.get("registration_id"):
            reg = Registration.objects.filter(id=data["registration_id"]).first()
        elif data.get("student_id") and data.get("event_id"):
            reg = Registration.objects.filter(
                student_id=data["student_id"], event_id=data["event_id"]
            ).first()
        if not reg:
            raise serializers.ValidationError("Matching registration not found.")
        data["registration"] = reg
        return data

    def create(self, validated):
        from .models import Attendance
        obj, _ = Attendance.objects.get_or_create(registration=validated["registration"])
        obj.present = True
        obj.save()
        return obj


class FeedbackSerializer(serializers.Serializer):
    registration_id = serializers.UUIDField(required=False)
    student_id = serializers.UUIDField(required=False)
    event_id = serializers.UUIDField(required=False)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(allow_blank=True, required=False)

    def validate(self, data):
        from .models import Registration
        reg = None
        if data.get("registration_id"):
            reg = Registration.objects.filter(id=data["registration_id"]).first()
        elif data.get("student_id") and data.get("event_id"):
            reg = Registration.objects.filter(
                student_id=data["student_id"], event_id=data["event_id"]
            ).first()
        if not reg:
            raise serializers.ValidationError("Matching registration not found.")
        data["registration"] = reg
        return data

    def create(self, validated):
        from .models import Feedback
        fb, _ = Feedback.objects.update_or_create(
            registration=validated["registration"],
            defaults={
                "rating": validated["rating"],
                "comment": validated.get("comment", ""),
            },
        )
        return fb


# Read-only serializers for reports
class EventReportSerializer(serializers.ModelSerializer):
    registrations = serializers.IntegerField()
    attendance = serializers.IntegerField()
    attendance_pct = serializers.FloatField()
    avg_rating = serializers.FloatField()

    class Meta:
        model = Event
        fields = ["id", "title", "code", "registrations", "attendance", "attendance_pct", "avg_rating"]


class StudentParticipationSerializer(serializers.ModelSerializer):
    attended_events = serializers.IntegerField()

    class Meta:
        model = Student
        fields = ["id", "name", "roll_number", "attended_events"]
