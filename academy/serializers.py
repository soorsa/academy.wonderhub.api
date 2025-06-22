from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.StringRelatedField()
    class Meta:
        model = Course
        fields ="__all__"