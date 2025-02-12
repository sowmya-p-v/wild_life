from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import UserRegistration

# ✅ Customizing UserRegistration Admin Panel
class UserRegistrationAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Additional Info", {"fields": ("phone", "city", "address", "postal_code")}),
    )
    
    list_display = ('username', 'email', 'is_staff', 'is_superuser', 'get_groups')  # Display groups in list
    list_filter = ('groups', 'is_staff', 'is_superuser')  # Filter users by groups
    search_fields = ('username', 'email')  # Enable searching

    def get_groups(self, obj):
        return ", ".join([g.name for g in obj.groups.all()]) if obj.groups.exists() else "No Group"
    get_groups.short_description = 'Groups'

# ✅ Register UserRegistration with Django Admin
admin.site.register(UserRegistration, UserRegistrationAdmin)

# ✅ Customizing Group Admin to Show Users
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "get_users")  # Show group name and users

    def get_users(self, obj):
        users = obj.userregistration_groups.all()  # Retrieve users in group
        return ", ".join([user.username for user in users]) if users else "No users"
    
    get_users.short_description = "Users in Group"

# ✅ Register Custom Group Admin
admin.site.unregister(Group)  # Remove default group admin
admin.site.register(Group, CustomGroupAdmin)  # Register custom group admin
