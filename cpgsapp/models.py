from django.db import models

# Create your models here.
class NetworkSettings(models.Model):
    ipv4_address = models.TextField(default='192.168.0.254')
    gateway_address = models.TextField(default="192.168.0.1")


# class Spaces(models.Model):
#     spaceID = models.CharField(max_length=10)
#     licenseNumber = models.CharField(max_length=20)
#     spaceStatus = models.CharField(max_length=30, choices=(('occupied','occupied'),('vaccant','vaccant')))
#     entryTime = models.CharField(max_length=20)
#     exitTime = models.CharField(max_length=20)