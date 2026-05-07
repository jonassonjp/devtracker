from django.contrib import admin
from .models import Project, Session, Event
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name','language','total_sessions','created_at']
    prepopulated_fields = {'slug': ('name',)}
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ['project','started_at','ended_at','auto_closed']
    list_filter = ['project','auto_closed']
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['session','event_type','timestamp']
    list_filter = ['event_type']
