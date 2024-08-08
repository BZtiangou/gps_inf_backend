from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import LocationInf, AccelerometerInf, BlueToothInf

class LocationAdmin(admin.ModelAdmin):
    fields = ('username', 'device', 'longitude', 'latitude', 'accuracy')
    list_display = ('username', 'device', 'longitude', 'latitude', 'accuracy', 'timestamp', 'label')
    search_fields = ['username']
    list_per_page = 20
    actions = ['delete_selected']  # Ensure bulk delete is enabled

admin.site.register(LocationInf, LocationAdmin)

class BlueToothAdmin(admin.ModelAdmin):
    fields = ('username', 'device', 'connection_device')
    list_display = ('username', 'device', 'connection_device', 'timestamp')
    search_fields = ['username']
    list_per_page = 6
    actions = ['delete_selected']  # Ensure bulk delete is enabled

admin.site.register(BlueToothInf, BlueToothAdmin)

class AccelerometerAdmin(admin.ModelAdmin):
    fields = ('username', 'device', 'acc_x', 'acc_y', 'acc_z')
    list_display = ('username', 'device', 'acc_x', 'acc_y', 'acc_z', 'timestamp')
    search_fields = ['username']
    list_per_page = 20
    actions = ['delete_selected']  # Ensure bulk delete is enabled

admin.site.register(AccelerometerInf, AccelerometerAdmin)
