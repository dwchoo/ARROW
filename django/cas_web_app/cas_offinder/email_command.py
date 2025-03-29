from __future__ import absolute_import, unicode_literals
from django.core.mail import EmailMessage
from django.conf import settings

from cas_offinder.data_class import job_data
from cas_offinder.raw_text_format import return_email_content



def send_email(email_addr, _job_data):
    if settings.GMAIL_SETTED:
        email_title = f"CAS-OFFINDER - {_job_data.job_title} finished!"
        email_contents = return_email_content(_job_data) 
        email = EmailMessage(email_title, email_contents, to=[email_addr])
        email.send()
