# Importing functions
import threading
import time
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from cpgsapp.controllers.NetworkController import (
    change_hostname, connect_to_wifi, get_network_settings, 
    saveNetworkSetting, set_dynamic_ip, set_static_ip
)
from cpgsapp.serializers import NetworkSettingsSerializer
from .models import NetworkSettings
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_406_NOT_ACCEPTABLE
from django.views.decorators.csrf import csrf_exempt
from cpgsapp.controllers.CameraViewController import (
    capture, get_camera_view_with_space_coordinates, 
    get_monitoring_spaces, liveMode
)
from cpgsapp.controllers.FileSystemContoller import (
    change_mode_to_config, change_mode_to_live, clear_space_coordinates, 
    get_mode_info, get_space_coordinates, get_space_info, save_space_coordinates
)

# Function to monitor mode continuously
def ModeMonitor():
    while True:
        time.sleep(2)
        mode = get_mode_info()
        if mode == "live":
            liveMode()

# Function to initiate tasks
def initiate(req):
    threading.Thread(target=capture).start()  # Start the camera capture thread
    threading.Thread(target=ModeMonitor).start()  # Start the mode monitor thread
    return HttpResponse("")

# Handle Mode-related tasks
class ModeHandler(APIView):
    def post(self, req):
        islive = req.data['islive']
        if islive:
            change_mode_to_live()
        else:
            change_mode_to_config()
        mode = get_mode_info()
        return Response({'data': mode}, status=HTTP_200_OK)
    
    def get(self, req):
        mode = get_mode_info()
        return Response({'data': mode}, status=HTTP_200_OK)

# Handles Network-related tasks
class NetworkHandler(APIView):
    def post(self, req):
        task, data = req.data['task'], req.data['data']
        networkSettings = NetworkSettings.objects.first()  # Efficient query for the first object

        if task == "iptype":
            networkSettings.ipv4_address = data['ipv4_address']
            networkSettings.gateway_address = data['gateway_address']
            networkSettings.subnet_mask = data['subnet_mask']
            networkSettings.ip_type = data['ip_type']
            if data['ip_type'] == 'static':
                set_static_ip()
            elif data['ip_type'] == 'dynamic':
                set_dynamic_ip()

        elif task == 'accesspoint':
            connect_to_wifi(data['ap_ssid'], data['ap_password'])
            networkSettings.ap_ssid = data['ap_ssid']
            networkSettings.ap_password = data['ap_password']

        elif task == 'server':
            networkSettings.server_ip = data['server_ip']
            networkSettings.server_port = data['server_port']

        elif task == 'visibility':
            change_hostname(data['host_name'])
            networkSettings.host_name = data['host_name']

        networkSettings.save()
        return Response({"data": 'reload'}, status=HTTP_200_OK)
    
    def get(self, req):
        return Response({'data': get_network_settings()}, status=HTTP_200_OK)

# Handle Live Stream related tasks
class LiveStreamHandler(APIView):
    def post(self, req):
        # Placeholder for handling live stream tasks
        return Response(status=HTTP_200_OK)
    
    def get(self, req):
        # Placeholder for getting live stream status
        return Response(status=HTTP_200_OK)

# Handle Account-related tasks
class AccountHandler(APIView):
    def post(self, req):
        # Placeholder for account tasks
        return Response(status=HTTP_200_OK)
    
    def get(self, req):
        # Placeholder for getting account status
        return Response(status=HTTP_200_OK)

# Handle Monitoring space related tasks
class MonitorHandler(APIView):
    def post(self, req):
        if 'task' not in req.data or 'data' not in req.data:
            return Response(data={"status": 'Please mention a task and data'}, status=HTTP_406_NOT_ACCEPTABLE)
        
        task, data = req.data['task'], req.data['data']

        if task == 'GET_MONITOR_COUNT':
            spaces = get_space_coordinates()
            return Response(data={'data': len(spaces)}, status=HTTP_200_OK)
        
        if task == 'GET_MONITOR_VIEWS':
            spaces = get_monitoring_spaces()
            return Response({'data': spaces}, status=HTTP_200_OK)

    def get(self, req):
        return Response(status=HTTP_200_OK)

# Handle Calibration related tasks
class CalibrateHandler(APIView):
    def post(self, req):
        if 'task' not in req.data or 'data' not in req.data:
            return Response(data={"status": 'Please mention a task and data'}, status=HTTP_406_NOT_ACCEPTABLE)

        task, data = req.data['task'], req.data['data']

        # Handle different calibration tasks
        if task == 'UPDATE_SPACE_COORDINATES':
            save_space_coordinates(data['x'], data['y'])
            return Response(status=HTTP_200_OK)
        
        if task == 'GET_CAMERA_VIEW_WITH_COORDINATES':
            camera_view_with_coordinates = get_camera_view_with_space_coordinates()
            return Response(status=HTTP_200_OK, data={"data": camera_view_with_coordinates})
        
        if task == 'CLEAR_SPACE_COORDINATES':
            clear_space_coordinates()
            return Response(status=HTTP_200_OK)
        
        return Response(status=HTTP_200_OK)

    def get(self, req):
        return Response(status=HTTP_200_OK)
