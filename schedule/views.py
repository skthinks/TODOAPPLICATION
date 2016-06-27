import hashlib

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .models import Users, Schedule
from .serializers import UserSerializer, ScheduleSerializer


def logged_in(request):
    if 'login' in request.session.keys():
        if request.session['login'] == "Yes":
            return True
    return False


@api_view(['GET', 'POST'])
def list_users(request, format=None):
    if request.method == 'GET':
        if not logged_in(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        users = Users.objects.all().filter(verified=True, deleted_flag=False)
        serializer = UserSerializer(users, many=True)
        responses = {}
        try:
            responses['data'] = serializer.data
            responses['status'] = {'success': True,
                                   'message': "Data Retrieved"}
            for response in responses['data']:
                del response['password']
                del response['verified']
                del response['deleted_flag']
            return Response(responses)
        except:
            responses['status'] = {'success': False,
                                   'error': "Data could not be retrieved"}
            return Response(responses, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        response = {}
        data = JSONParser().parse(request)
        data['password'] = hashlib.sha1(data['password']).hexdigest()
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response['status'] = {'success': True,
                                  'error': "Verification Mail Sent"}
            return Response(response, status=status.HTTP_201_CREATED)
        response['status'] = {'success': False,
                              'message': "Registration Failed",
                              'error': serializer.errors}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def get_users(request, pk, format=None):
    try:
        user = Users.objects.get(pk=pk, deleted_flag=False)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        if not logged_in(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user)
        response = serializer.data
        del response['password']
        del response['verified']
        del response['deleted_flag']
        return Response(response)

    elif request.method == 'PUT':
        response = {}
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            response['status'] = {"success": True,
                                  "message": "Registration Successful"}
            return Response(response, status=status.HTTP_201_CREATED)
        response['status'] = {'success': False,
                              'message': "Registration Failed",
                              'error': serializer.errors}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not logged_in(request):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = UserSerializer(user)
        response = serializer.data
        response['deleted_flag'] = True
        res = {}
        serializer_delete = UserSerializer(user, data=response)
        if serializer_delete.is_valid():
            serializer_delete.save()
            res['status'] = {"success": True, "message": "User Deleted"}
            return Response(res, status=status.HTTP_204_NO_CONTENT)
        res['status'] = {'success': False,
                         'message': "Registration Failed",
                         'error': serializer.errors}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def schedule(request, format=None):
    if not logged_in(request):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    if request.method == 'GET':
        response = {}
        schedule = Schedule.objects.all()
        serializer = ScheduleSerializer(schedule, many=True)
        try:
            response['data'] = serializer.data
            for resp in response['data']:
                resp['user_id'] = resp.get('user').get('id')
                del resp['user']
                del resp['checked']
                del resp['id']
            response['status'] = {"success": True}
            return Response(response)
        except:
            response['status'] = {'success': False,
                                  'message': "Resource not available"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        response = {}
        try:
            user = Users.objects.get(id=data['user_id'])
            schedule = Schedule(user=user, task=data['task'],
                                scheduled_time=data['scheduled_time'],
                                checked=True)
            schedule.save()
            response['status'] = {'success': True,
                                  'message': "Schedule Entry Added"}
            return Response(response, status=status.HTTP_201_CREATED)
        except:
            response['status'] = {'success': False,
                                  'message': "Entry could not be added",
                                  'error': "Check for missing or Invalid Fields"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        password = hashlib.sha1(password).hexdigest()
        if Users.objects.filter(email=email, password=password).exists():
            user = Users.objects.get(email=email)
            serializer = UserSerializer(user)
            request.session['user_id'] = serializer.data['id']
            request.session['login'] = "Yes"
            return Response({"success": True,
                             "message": "Logged In"},
                            status=status.HTTP_200_OK)
        else:
            request.session['login'] = "No"
            return Response({"success": False,
                             "message": "Incorrect Credentials"},
                            status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def logout(request):
    if logged_in(request):
        request.session['login'] = "No"
        return Response({"success": True,
                         "message": "Logged out successfully"})
    else:
        return Response({"success": False,
                         "message": "User was not logged in"})


@api_view(['GET', 'PUT'])
def user_schedule(request, pk, format=None):
    if not logged_in(request):
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    try:
        user = Users.objects.get(pk=pk, deleted_flag=False, verified=True)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    response = {}
    if request.method == 'GET':
        schedule = Schedule.objects.all().filter(user=user)
        serializer = ScheduleSerializer(schedule, many=True)
        try:
            response['data'] = serializer.data
            for resp in response['data']:
                resp['user_id'] = resp.get('user').get('id')
                del resp['user']
                del resp['checked']
                del resp['id']
            response['status'] = {"success": True}
            return Response(response)
        except:
            response['status'] = {'success': False,
                                  'message': "Resource not available"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # requires parameters in PUT body - Those names assumed
        response = {}
        if 'parameter_time' not in request.data.keys() or
           'parameter_task' not in request.data.keys():
            response['status'] = {'success': False,
                                  'message': "Parameters missing"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            datadict = {"task": request.data['task'],
                        "scheduled_time": request.data['scheduled_time'],
                        "checked": request.data['checked']}
            up_sched, created = Schedule.objects.update_or_create(user=user,
                                                                  task=request.data['parameter_task'],
                                                                  scheduled_time=request.data['parameter_time'],
                                                                  defaults=datadict)
            up_sched.save()
            response['status'] = {'success': True,
                                  'message': "Field Updated"}
            return Response(response, status=status.HTTP_201_CREATED)
        except:
            response['status'] = {'success': False,
                                  'message': "Invalid or missing Fields"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
