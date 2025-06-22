from django.contrib import admin
from .models import CustomUser
# Register your models here.
admin.site.site_header = "Academy Admin Portal"
admin.sites.AdminSite.site_title = "Academy Admin Portal"
admin.site.index_title = "Welcome to Academy Admin Portal"
# admin.site.login_template = "users/login.html"
admin.site.register(CustomUser)