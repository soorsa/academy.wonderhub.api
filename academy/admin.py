from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Category)
admin.site.register(Topic)
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(Lesson)