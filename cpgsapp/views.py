import threading
from rest_framework.response import Response
from django.shortcuts import HttpResponse
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_406_NOT_ACCEPTABLE

from cpgsapp.controllers.CameraViewController import capture, get_camera_view_with_space_coordinates, get_monitoring_spaces
from cpgsapp.controllers.FileSystemContoller import clear_space_coordinates, get_space_coordinates, get_space_info, save_space_coordinates


def initiate(req):
    ShootCameraThread = threading.Thread(target=capture)
    ShootCameraThread.start()
    return HttpResponse("")

# Handles Network related tasks
class NetworkHandler(APIView):
    def post(self, req):
        task, data  = req.data['task'], req.data['data']
        print(task, data)
        return Response(status=HTTP_200_OK)
    def get(self, req):
        return Response(status=HTTP_200_OK)

# Handle Live Stream Related Tasks
class LiveStreamHandler(APIView):
    def post(self, req):
        task, data  = req.data['task'], req.data['data']
        print(task, data)
        return Response(status=HTTP_200_OK)
    def get(self, req):
        return Response(status=HTTP_200_OK)
    
# Handle Account Related Tasks
class AccountHandler(APIView):
    def post(self, req):
        task, data  = req.data['task'], req.data['data']
        print(task, data)
        return Response(status=HTTP_200_OK)
    def get(self, req):
        return Response(status=HTTP_200_OK)

# Handle Monitoring space related tasks
class MonitorHandler(APIView):
    def post(self, req):
        
        if 'task' not in req.data:
            return Response(data={"status":'Please mention a task'},status=HTTP_406_NOT_ACCEPTABLE)
        if 'data' not in req.data:
            return Response(data={"status":'Please mention a data'},status=HTTP_406_NOT_ACCEPTABLE)

        task, data  = req.data['task'], req.data['data']

        if task == 'GET_MONITOR_COUNT':
            spaces = get_space_coordinates()
            NoOfSpaces = len(spaces)
            return Response(data={'data':NoOfSpaces},status=HTTP_200_OK)
        
        if task == 'GET_MONITOR_VIEWS':
            spaces  = get_monitoring_spaces()
            # print('your search is here - ',spaces)
            return Response({'data':spaces}, status=HTTP_200_OK)
            # return Response({"data":spaces},status=HTTP_200_OK)

        
    def get(self, req):
        return Response(status=HTTP_200_OK)
    
# Handle Calibration related tasks
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class CalibrateHandler(APIView):

    def post(self, req):
        if 'task' not in req.data:
            return Response(data={"status":'Please mention a task'},status=HTTP_406_NOT_ACCEPTABLE)
        if 'data' not in req.data:
            return Response(data={"status":'Please mention a data'},status=HTTP_406_NOT_ACCEPTABLE)

        task, data  = req.data['task'], req.data['data']

        if task == 'UPDATE_SPACE_COORDINATES':
            x = data['x']
            y = data['y']
            save_space_coordinates(x, y)
            return Response(status=HTTP_200_OK)
        
        if task == 'GET_CAMERA_VIEW_WITH_COORDINATES':
            camera_view_with_coordinates = get_camera_view_with_space_coordinates()
            return Response(status=HTTP_200_OK, data={"data":camera_view_with_coordinates})
        
        if task == 'CLEAR_SPACE_COORDINATES':
            clear_space_coordinates()
            return Response(status=HTTP_200_OK)
        
        return Response(status=HTTP_200_OK)
    def get(self, req):
        return Response(status=HTTP_200_OK)
    