from django.contrib import admin
from cas_offinder.models import Job
import os
import shutil
from django.conf import settings
from django.db.models import QuerySet
# Register your models here.


class JobQuerySet(QuerySet):
    def delete(self):
        job_data_path = settings.JOB_DATA_PATH
        for job in self:
            job_folder_path = os.path.join(job_data_path, str(job.UUID))
            if os.path.exists(job_folder_path):
                try:
                    shutil.rmtree(job_folder_path)
                    print(f"DELETE FOLDER: {job_folder_path}")
                except OSError as e:
                    print(f"ERROR deleting folder {job_folder_path}: {e}")
        super().delete()

class JobAdmin(admin.ModelAdmin):
    fields = [
        'UUID',
        'job_title',
        'email',
        'time_stamp',
        'job_finish',
        'error',
        'logs',
        'results_url_link',
    ]
    readonly_fields = [
        'UUID',
        'time_stamp',
        'error',
        'logs',
        'results_url_link',
    ]
    list_display=['job_title','job_finish','error','time_stamp']
    list_filter = ['job_finish','error']
    search_fields = ['job_title','email']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return JobQuerySet(self.model, using=qs._db)

    def delete_queryset(self, request, queryset):
        job_data_path = settings.JOB_DATA_PATH
        for job in queryset:
            job_folder_path = os.path.join(job_data_path, str(job.UUID))
            if os.path.exists(job_folder_path):
                try:
                    shutil.rmtree(job_folder_path)
                    print(f"DELETE FOLDER: {job_folder_path}")
                except OSError as e:
                    print(f"ERROR deleting folder {job_folder_path}: {e}")
        queryset.delete()


admin.site.register(Job, JobAdmin)
