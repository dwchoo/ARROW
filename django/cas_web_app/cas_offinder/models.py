from django.db import models
from django.utils.html import format_html

import os
import shutil
from django.conf import settings


# Create your models here.

class Job(models.Model):
    id            = models.AutoField(primary_key=True)
    UUID          = models.CharField(max_length=64)
    job_title     = models.CharField(max_length=200)
    email         = models.EmailField(max_length=254, null=True, blank=True)
    time_stamp    = models.DateTimeField(auto_now=True)
    job_finish    = models.BooleanField(default=False)
    logs          = models.TextField(blank=True, null=True, default=None)
    error         = models.BooleanField(default=True)
    job_data_dump = models.TextField(blank=True, null=True, default=None)
    results_url   = models.URLField("results url", max_length=254,null=True, default=None)

    def __str__(self):
        return self.UUID

    def results_url_link(self,):
        __foramt = format_html(
            #f'<a href="{self.results_url}" target="_blank">Result page link</a>'
            f'<a href="/{self.UUID}/results" target="_blank">Result page link</a>'
        )
        return __foramt
    
    def delete(self, *args, **kwargs):
        job_data_path = settings.JOB_DATA_PATH
        job_folder_path = os.path.join(job_data_path, str(self.UUID))

        if os.path.exists(job_folder_path):
            try:
                shutil.rmtree(job_folder_path)  # 폴더와 그 내용물을 삭제합니다.
                print(f"DELETE FOLDER: {job_folder_path}")
            except OSError as e:
                print(f"ERROR deleting folder {job_folder_path}: {e}")

        super().delete(*args, **kwargs)


#class Dataframe_table(models.Model):
#    #header = ["query","chr","site","seq","direction","mismatch"]
#    #data_type = {'site' : 'int32', 'mismatch' : 'int8',}
#    index       = models.PositiveBigIntegerField()
#    query       = models.CharField(max_length=64)
#    chromosome  = models.CharField(max_length=64)
#    site        = models.PositiveBigIntegerField()
#    sequence    = models.CharField(max_length=64)
#    direction   = models.CharField(max_length=16)
#    mismatch    = models.SmallIntegerField()
