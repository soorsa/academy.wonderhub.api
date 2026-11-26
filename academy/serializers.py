from decimal import Decimal
from rest_framework import serializers
from .models import *
from users.serializers import UserSerializer

class TopicSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(slug_field="slug", queryset=Category.objects.all())
    class Meta:
        model = Topic
        depth = 3
        fields =["id","category","name","slug","description","total_courses"]

class InstructorSerializer(serializers.ModelSerializer):
    number_of_courses = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'job_title', 'bio', 'username', 'number_of_courses')
        read_only_fields = ('id', 'email', 'first_name', 'last_name', 'role', 'username', 'number_of_courses')

    def get_number_of_courses(self, obj):
        if hasattr(obj, 'number_of_courses'):
            return obj.number_of_courses
        return obj.courses.count()

class CourseSerializer(serializers.ModelSerializer):
    instructor = InstructorSerializer(required=False)
    topic = TopicSerializer(read_only=True, many=True)
    topic_slugs = serializers.SlugRelatedField(slug_field="slug", many=True, write_only=True, queryset=Topic.objects.all())
    class Meta:
        model = Course
        fields = [
            'slug',
            'title',
            'thumbnail',
            'description',
            'level',
            'benefits',
            'suitable_for',
            'price',
            'undiscounted_price',
            'sale_type',
            'sale_header',
            'sale_message',
            'is_published',
            'total_duration',
            'created_at',
            'topic',
            'instructor',
            'number_of_students',
            'total_lectures',
            'topic_slugs'
        ]
        read_only_fields = [
            "id",
            "slug",
            "total_duration",
            "total_lectures",
            "number_of_students",
            "created_at",
        ]
class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.SlugRelatedField(slug_field="slug", queryset=Course.objects.all())
    class Meta:
        depth = 2
        model = Module
        fields = ["id", "title", "slug", "order", "lecture_count", "course"]
class LessonSerializer(serializers.ModelSerializer):
    module = serializers.SlugRelatedField(slug_field="slug", write_only=True, queryset=Module.objects.all())
    module_obj = ModuleSerializer(source="module", read_only=True)
    class Meta:
        depth = 2
        model = Lesson
        fields ="__all__"
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name','slug', 'description', 'is_popular', 'total_courses']


class TransactionSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal("0.01")
    )
    currency = serializers.CharField(max_length=3, default="NGN")
    transaction_type = serializers.ChoiceField(
        choices=Transaction.TransactionType.choices,
        default=Transaction.TransactionType.PAYMENT,
    )
    description = serializers.CharField(required=False, allow_blank=True, default="")
    metadata = serializers.JSONField(required=False, default=dict)
    reference = serializers.CharField(
        required=False, allow_blank=False, max_length=100
    )

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = (
                    "id",
                    "reference",
                    "status",
                    "created_at",
                    "updated_at",
                )
        
    def validate_reference(self, value):
        if value and Transaction.objects.filter(reference=value).exists():
            raise serializers.ValidationError("A transaction with this reference already exists.")
        return value
    

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)  # Or your standard User serializer
    course = CourseSerializer(read_only=True)
    course_slug = serializers.SlugRelatedField(
        slug_field="slug", 
        queryset=Course.objects.all(), 
        write_only=True, 
        source="course"
    )
    transaction = TransactionSerializer(read_only=True)
    transaction_id = serializers.PrimaryKeyRelatedField(
        queryset = Transaction.objects.all(),
        write_only = True,
        source = "transaction",
        required=False
    )

    class Meta:
        model = Enrollment
        fields = ["id", "student", "course", "course_slug", "fullname", "email", "phone_number", "amount_paid", "transaction","transaction_id", "enrolled_at", "is_active"]
        read_only_fields = ["id", "enrolled_at", "is_active", "transaction"]

