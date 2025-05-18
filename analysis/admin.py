from django.contrib import admin
from .models import  gps_cluster,bt_cluster

class gps_clusterAdmin(admin.ModelAdmin):
    fields = ('username', 'cluster_name', 'longitude', 'latitude')
    list_display = ('username', 'cluster_name', 'longitude', 'latitude','label', 'timestamp')
    search_fields = ['username']
    list_per_page = 20
    actions = ['delete_selected']  # Ensure bulk delete is enabled
    list_editable = ("cluster_name",)
admin.site.register(gps_cluster, gps_clusterAdmin)


class bt_clusterAdmin(admin.ModelAdmin):
    fields = ('username', 'label', 'bt_device')
    list_display = ('username', 'label','bt_device')
    search_fields = ['username']
    list_per_page = 20
    list_editable = ("label",)
    actions = ['delete_selected']  # Ensure bulk delete is enabled
admin.site.register(bt_cluster, bt_clusterAdmin)