from django.contrib import admin
from .models import Profile, Complaint

# Customizing the Complaint model in the admin interface
class ComplaintAdmin(admin.ModelAdmin):
    list_filter = ('status', 'type')  # Enables filtering by status and type
    search_fields = ('subject', 'description', 'user__username')  # Enables searching by subject, description, and username

# Customizing the Profile model in the admin interface
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'department', 'contact_number')  # Enables searching by username, department, and contact number

# Register Profile with the custom admin class
admin.site.register(Profile, ProfileAdmin)

# Register Complaint with the custom admin class
admin.site.register(Complaint, ComplaintAdmin)
