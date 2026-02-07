from django.contrib import admin
from .models import Task
# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created',) # hace que el campo created sea de solo lectura en el admin

admin.site.register(Task, TaskAdmin)