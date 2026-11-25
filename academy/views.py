from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from .models import *
from rest_framework.permissions import AllowAny, IsAuthenticated,IsAdminUser


# Create your views here.
class CourseApiSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    lookup_field = "slug"
    filterset_fields = ["title", "topic__slug",]
    search_fields = ["title", "topic__name","description","topic__description","benefits","instructor__first_name","instructor__last_name"]
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_serializer_class(self):
        if self.action == "modules":
            return ModuleSerializer
        if self.action in ("enroll", "pre_enroll"):
            return EnrollmentSerializer
        return super().get_serializer_class()
    
    def get_permissions(self):
        if self.action in ["list", "retrieve","modules","pre_enroll"]:
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)

    @action(detail=True, methods=["get"])
    def modules(self, request, slug=None):
        course = self.get_object()
        serializer = ModuleSerializer(
            course.modules.all(),
            many=True
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def enroll(self, request, slug=None):
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)
        
        if not created and not enrollment.is_active:
            enrollment.is_active = True
            enrollment.save()
            
        serializer = EnrollmentSerializer(enrollment, context={"request": request})
        return Response(serializer.data, status=201 if created else 200)
    
    @action(detail=True, methods=["post"], permission_classes=[AllowAny()])
    def pre_enroll(self, request, slug=None):
        # course = self.get_object()
        serializer = EnrollmentSerializer(data=request.data, context={"request":request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # enrollment, created = Enrollment.objects.get_or_create(student=None, course=course)
        
        # if not created and not enrollment.is_active:
        #     enrollment.is_active = True
        #     enrollment.save()
            
        # serializer = EnrollmentSerializer(enrollment, context={"request": request})
        return Response(serializer.data, status=201)

class LessonApiSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    lookup_field = "slug"
    # filterset_fields = ["name", "type", "duration"]
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]
    
class ModuleApiSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    lookup_field = "slug"
    # filterset_fields = ["name", "type", "duration"]
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [AllowAny()]
    
    def get_serializer_class(self):
        if self.action == "lessons":
            return LessonSerializer
        return super().get_serializer_class()

    @action(detail=True, methods=["get"])
    def lessons(self, request, slug=None):
        module = self.get_object()
        serializer = LessonSerializer(
            module.lessons.all(),
            many=True
        )
        return Response(serializer.data)

    
class CategoryApiSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    lookup_field = "slug"
    # filterset_fields = ["name", "type", "duration"]
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(),IsAdminUser()]
    
class TopicApiSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["name", "category__slug",]
    lookup_field = "slug"
    # ordering_fields = ["created_at", "duration", "interest_rate"]
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]
    
class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["course__slug", "is_active"]

    def get_queryset(self):
        # Admins can view all enrollments; regular users only see their own
        user = self.request.user
        if user.is_staff:
            return Enrollment.objects.all()
        return Enrollment.objects.filter(student=user)

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["status", "amount", "transaction_type"]

    def get_queryset(self):
        # Admins can view all enrollments; regular users only see their own
        user = self.request.user
        if user.is_staff:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def initiate(self, request):
        serializer = TransactionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reference = f"WHA_{uuid.uuid4().hex[:12].upper()}"
        user = request.user if request.user.is_authenticated else None

        serializer.save(
        user=user,
        reference=reference,
        status=Transaction.Status.PENDING,  # Always force PENDING on creation
        )
        return Response(serializer.data)