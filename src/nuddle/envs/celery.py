# nuddle/envs/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from kombu import Queue, Exchange

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nuddle.envs.common')

app = Celery('nuddle')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.task_queues = (
    Queue('celery', Exchange('celery'), routing_key='task.#'),
    Queue('smsOTP)', Exchange('smsOTP'), routing_key='sms.otp.send'),
)
