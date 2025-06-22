from django.db import models
from django.conf import settings
from django.db.models import Sum, Count
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_published = models.BooleanField(default=False)
    total_lectures = models.PositiveIntegerField(default=0,editable=False)
    total_duration = models.DurationField(default=timedelta(0),editable=False)  # Stores total time like 61h 44m
    created_at = models.DateTimeField(auto_now_add=True)

    def update_course_stats(self):
        """Recalculate total lectures and duration for the course"""
        stats = Lesson.objects.filter(module__course=self).aggregate(
            total_lectures=Count("id"), 
            total_duration=Sum("duration")
        )
        self.total_lectures = stats["total_lectures"] or 0
        self.total_duration = stats["total_duration"] or timedelta(0)
        self.save()

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)  # Helps order modules
    lecture_count = models.PositiveIntegerField(default=0,editable=False)
    total_duration = models.DurationField(default=timedelta(0),editable=False)

    def update_module_stats(self):
        """Recalculate total lectures and duration for the module"""
        stats = Lesson.objects.filter(module=self).aggregate(
            total_lectures=Count("id"), 
            total_duration=Sum("duration")
        )
        self.lecture_count = stats["total_lectures"] or 0
        self.total_duration = stats["total_duration"] or timedelta(0)
        self.save()
        # Update the parent course too
        self.course.update_course_stats()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)  # Helps order lessons
    duration = models.DurationField(default=timedelta(0))  # Duration of the lesson
    is_preview = models.BooleanField(default=False)  # Free preview lesson

    # Content fields
    video_url = models.URLField(blank=True, null=True)
    pdf_file = models.FileField(upload_to="lesson_pdfs/", blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"
