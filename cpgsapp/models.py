from django.db import models

# Create your models here.
class NetworkSettings(models.Model):
    ipv4_address = models.TextField(default='192.168.0.254')
    gateway_address = models.TextField(default="192.168.0.1")