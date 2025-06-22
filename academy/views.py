from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import CourseSerializer
from .models import Course


# Create your views here.

def home(request):
    return render(request, 'academy/home.html')

@api_view(['GET'])
def getCourses(request):
    courses = CourseSerializer(Course.objects.all(), many=True)
    return Response(courses.data)
