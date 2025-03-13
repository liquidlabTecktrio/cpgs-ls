# Developed By Tecktrio At Liquidlab Infosystems
# Project: Views or Main Module were requests are handled
# Version: 1.0
# Date: 2025-03-08
# Description: Fullfull the requests comming from servers or other remote devices in the network

# Importing functions
import threading
import time
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from cpgsapp.controllers.HardwareController import RebootSystem
from cpgsapp.controllers.NetworkController import (
    change_hostname, connect_to_wifi, get_network_settings, 
    set_dynamic_ip, set_static_ip
)
from cpgsapp.serializers import AccountSerializer
from cpgsserver.settings import USER_VALIDATE_TOKEN
from .models import Account, NetworkSettings
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_406_NOT_ACCEPTABLE, HTTP_401_UNAUTHORIZED
from cpgsapp.controllers.CameraViewController import (
    capture, get_camera_view_with_space_coordinates, 
    get_monitoring_spaces, liveMode
)
from cpgsapp.controllers.FileSystemContoller import (
    change_mode_to_config, change_mode_to_live, clear_space_coordinates, 
    get_mode_info, get_space_coordinates, save_space_coordinates
)
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator



# Validate user method
def ValidateUser(req):
    if "token" in req.data:
        token = req.data['token']
        if token == USER_VALIDATE_TOKEN:
            return True
        else:
            return False
    else:
        return False
    

# Function to monitor mode continuously
def ModeMonitor():
    print("Starting Monitoring Mode")
    while True:
        time.sleep(2)
        mode = get_mode_info()
        if mode == "live":
            liveMode()


# Function to initiate tasks
def initiate(req):
    print('Initiating CPGS')
    threading.Thread(target=capture).start()  # Start the camera capture thread
    threading.Thread(target=ModeMonitor).start()  # Start the mode monitor thread
    return HttpResponse("")

# RebootSystem
def reboot(req):
    print('Rebooting...')
    RebootSystem()
    return Response(status = HTTP_200_OK)


# Handle Mode-related tasks
class ModeHandler(APIView):
    def post(self, req):
        if ValidateUser(req):
            islive = req.data['islive']
            if islive:
                change_mode_to_live()
            else:
                change_mode_to_config()
            mode = get_mode_info()
            return Response({'data': mode}, status=HTTP_200_OK)
        else:
            return Response({"status":"Missing Authorization Token in body"},status=HTTP_401_UNAUTHORIZED)
        
    def get(self, req):
        mode = get_mode_info()
        return Response({'data': mode}, status=HTTP_200_OK)


# Handles Network-related tasks
class NetworkHandler(APIView):
    def post(self, req):
        if ValidateUser(req):
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
        else:
            return Response({"status":"Missing Authorization Token in body"},status=HTTP_401_UNAUTHORIZED)
    
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
# @method_decorator(csrf_exempt, name='dispatch')
class AccountHandler(APIView):
    def post(self, req):
        if 'username' not in req.data or 'password' not in req.data:
            return Response({"status":"Username or password is Required"}, status=HTTP_406_NOT_ACCEPTABLE)
        username = req.data['username']
        password = req.data['password']
        user = Account.objects.filter(username=username, password=password)
        if user:
            return Response({"token":USER_VALIDATE_TOKEN},status=HTTP_200_OK)
        else:
            return Response({"status":"User Do Not Exist"},status=HTTP_401_UNAUTHORIZED)
    
    def get(self, req):
        user = Account.objects.first()
        AccountSerialized = AccountSerializer(user)
        return Response({'data':AccountSerialized.data},status=HTTP_200_OK)

    def put(self, req):
        if 'old_username' not in req.data or 'old_password' not in req.data or 'new_password' not in req.data or 'new_username' not in req.data:
            return Response({"status":"Username or password is Required"}, status=HTTP_406_NOT_ACCEPTABLE)
        # old_username = req.data['old_username']
        # old_password = req.data['old_password'] 
        new_username = req.data['new_username']
        new_password = req.data['new_password']
        user = Account.objects.first()
        if user:
            user.username = new_username
            user.password = new_password
            user.save()
            serializedUser = AccountSerializer(user)
            return Response({"data":serializedUser.data},status=HTTP_200_OK)
        else:
            return Response({"status":"User Do Not Exist"},status=HTTP_401_UNAUTHORIZED)



# Handle Monitoring space related tasks
class MonitorHandler(APIView):
    def post(self, req):
        if ValidateUser(req):
            if 'task' not in req.data or 'data' not in req.data:
                return Response(data={"status": 'Please mention a task and data'}, status=HTTP_406_NOT_ACCEPTABLE)
            task, _ = req.data['task'], req.data['data']

            if task == 'GET_MONITOR_COUNT':
                spaces = get_space_coordinates()
                return Response(data={'data': len(spaces)}, status=HTTP_200_OK)
            
            if task == 'GET_MONITOR_VIEWS':
                spaces = get_monitoring_spaces()
                return Response({'data': spaces}, status=HTTP_200_OK)
        else:
            return Response({"status":"Missing Authorization Token in body"},status=HTTP_401_UNAUTHORIZED)

    def get(self, req):
        return Response(status=HTTP_200_OK)



# Handle Calibration related tasks
class CalibrateHandler(APIView):
    def post(self, req):
        if ValidateUser(req):
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
        else:
            return Response({"status":"Missing Authorization Token in body"},status=HTTP_401_UNAUTHORIZED)

    def get(self, req):
        return Response(status=HTTP_200_OK)
