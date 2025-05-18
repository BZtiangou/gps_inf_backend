from django.contrib import admin
from .models import PoseSource

class PoseSourceAdmin(admin.ModelAdmin):
    list_display = ('video', 'upload_date', 'username')
    list_filter = ('upload_date', 'username')
    ordering = ('-upload_date',)

admin.site.register(PoseSource, PoseSourceAdmin)
