from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Workgroup, Today

# Register your models here.
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            "User Info",
            {"fields": ("username", "password", "nickname", "email", "status")},
        ),
    )
    list_display = (
        "username",
        "status",
        "email",
    )


@admin.register(Workgroup)
class WorkgroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Today)
class TodayAdmin(admin.ModelAdmin):
    pass