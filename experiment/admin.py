from django.contrib import admin
from .models import Experiment,exp_history
# Register your models here.

class experimentAdmin(admin.ModelAdmin):
    fields = ( 'start_time','end_time','exp_name','description',)
    list_display = ('exp_id','exp_name','description','start_time','end_time',"participants_name",)
    list_per_page = 10
    search_fields = ['exp_name']
    list_filter = ('exp_name',)
    list_editable = ("start_time","end_time",'exp_name','description',"participants_name")
admin.site.register(Experiment,experimentAdmin)

class exp_historyAdmin(admin.ModelAdmin):
    fields = ('exp_name','username')
    list_display = ('exp_id','username','exp_name','join_time','exit_time')
    list_per_page = 10
    search_fields = ['exp_name']
    list_filter = ('exp_name',)
    list_editable = ("username","exp_name",)
admin.site.register(exp_history,exp_historyAdmin)