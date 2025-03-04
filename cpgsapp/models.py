from django.db import models

# Create your models here.
class NetworkSettings(models.Model):
    ipv4_address = models.TextField(default='192.168.0.254')
    gateway_address = models.TextField(default="192.168.0.1")
    ap_ssid = models.TextField(default="admin")
    ap_password = models.TextField(default="admin@1234")
    server_ip = models.TextField(default="192.168.1.100")
    server_port = models.TextField(default="9090")
    host_name = models.TextField(default="cpgs")
    subnet_mask = models.TextField(default="255.255.255.1")
    ip_type = models.TextField(choices=(('static','static'),('dynamic', 'dynamic')), default='static')

# class Spaces(models.Model):
#     spaceID = models.CharField(max_length=10)
#     licenseNumber = models.CharField(max_length=20)
#     spaceStatus = models.CharField(max_length=30, choices=(('occupied','occupied'),('vaccant','vaccant')))
#     entryTime = models.CharField(max_length=20)
#     exitTime = models.CharField(max_length=20)

