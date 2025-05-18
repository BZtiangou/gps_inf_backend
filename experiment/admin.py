from django.contrib import admin
from .models import Experiment,exp_history
# Register your models here.

class experimentAdmin(admin.ModelAdmin):
    fields = ( 'start_time','end_time','exp_title','description',)
    list_display = ('exp_id','exp_title','description','start_time','end_time',"participants_name",)
    list_per_page = 10
    search_fields = ['exp_title']
    list_filter = ('exp_title',)
    list_editable = ("start_time","end_time",'exp_title','description',"participants_name")
admin.site.register(Experiment,experimentAdmin)

class exp_historyAdmin(admin.ModelAdmin):
    fields = ('exp_title','username')
    list_display = ('exp_id','username','exp_title','join_time','exit_time')
    list_per_page = 10
    search_fields = ['exp_title']
    list_filter = ('exp_title',)
    list_editable = ("username","exp_title",)
admin.site.register(exp_history,exp_historyAdmin)