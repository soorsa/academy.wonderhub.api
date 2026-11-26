from django.db import models
from django.db.models import Sum, Count
from datetime import timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from users.models import User
import uuid

LEVEL_CHOICES = (
    ("beginner", "Beginner"),
    ("intermediate", "Intermediate"),
    ("advanced", "Advanced"),
    )

SALE_CHOICES = (
    ("sale", "Sale"),
    ("presale", "Presale"),
    ("free", "Free"),
    )

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True)  # Allow blank for auto-generation
    is_popular = models.BooleanField(default=False)  # Allow blank for auto-generation
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def total_courses(self):
        topics = self.topics.all()
        total = 0
        for topic in topics:
            total += topic.total_courses
        return total
    
    def __str__(self):
        return self.name    
class Topic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True )  # Allow blank for auto-generation
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="topics")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def total_courses(self):
        total = self.courses.all().count()
        return total
    
    def __str__(self):
        return self.name    
class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="courses/", default="/thumbnail.png")
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    topic = models.ManyToManyField(Topic, related_name="courses", blank=True)
    benefits = models.JSONField(default=list, blank=True)
    suitable_for = models.JSONField(default=list, blank=True)
    undiscounted_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sale_type = models.CharField(max_length=15, choices=SALE_CHOICES, default="sale")
    preview_video = models.CharField(max_length=100, default="", blank=True, null=True)
    sale_header = models.CharField(max_length=100, default="Enroll for this course", blank=True, null=True)
    sales_message = models.TextField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    total_duration = models.DurationField(default=timedelta(0),editable=False)  # Stores total time like 61h 44m
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def total_lectures(self):
        """Recalculate total lectures and duration for the course"""
        total = self.modules.lessons.all().count()
        return total
    
    @property
    def number_of_students(self):
        """Return count of active student enrollments for the course."""
        # Uses prefetched cache if available; otherwise queries active enrollments
        return self.enrollments.all().count()
    
    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)  # Helps order modules
    total_duration = models.DurationField(default=timedelta(0),editable=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def lecture_count(self):
        """Recalculate total lectures and duration for the module"""
        return self.lessons.all().count()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Lesson(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)  # Helps order lessons
    duration = models.DurationField(default=timedelta(0))  # Duration of the lesson
    is_preview = models.BooleanField(default=False)  # Free preview lesson
    video_url = models.URLField(blank=True, null=True)
    pdf_file = models.FileField(upload_to="lesson_pdfs/", blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.module.course.title} - {self.module.title} - {self.title}"
    
class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", "Deposit"
        WITHDRAWAL = "WITHDRAWAL", "Withdrawal"
        PAYMENT = "PAYMENT", "Payment"
        REFUND = "REFUND", "Refund"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESS = "SUCCESS", "Success"
        FAILED = "FAILED", "Failed"
        REVERSED = "REVERSED", "Reversed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="transactions",
        blank=True,
        null=True
    )
    reference = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="NGN")
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        default=TransactionType.PAYMENT,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    description = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.reference} - {self.currency} {self.amount} ({self.status})"

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments", blank=True, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    fullname = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    transaction = models.OneToOneField(Transaction, on_delete=models.PROTECT, related_name="enrollment", null=True, blank=True)

    class Meta:
        unique_together = ("student", "course")
        ordering = ["-enrolled_at"]

    def __str__(self):
        identifier = self.student.email if self.student else self.fullname
        return f"{identifier} enrolled in {self.course.title}"