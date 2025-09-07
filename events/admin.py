#events/admin.py
from django.contrib import admin
from .models import College, Student, Event, Registration, Attendance, Feedback

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("name", "roll_number", "email", "college")
    search_fields = ("name", "roll_number", "email")
    list_filter = ("college",)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "college", "start_time", "end_time", "capacity")
    search_fields = ("title", "code")
    list_filter = ("college",)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("event", "student", "registered_at")
    search_fields = ("event__title", "student__roll_number")
    list_filter = ("event__college",)

admin.site.register(Attendance)
admin.site.register(Feedback)
