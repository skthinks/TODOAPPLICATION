import hashlib

from django.contrib.auth.models import User
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context
from django.http import HttpResponse
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .models import Users, Schedule
from .serializers import UserSerializer, ScheduleSerializer

def index(request):
    t = get_template('index.html')
    html = t.render(Context({}))
    return HttpResponse(html)


def is_authenticated(header, u_id):
    if 'HTTP_TOKEN' in header.keys():
        try:
            token = Token.objects.get(key=header['HTTP_TOKEN'])
            if str(token.user_id) == str(u_id):
                return True
            return False
        except:
            return False
    return False      


def is_superuser(header):
    if 'HTTP_TOKEN' in header.keys():
        try:
            token = Token.objects.get(key=header['HTTP_TOKEN'])
            user = User.objects.get(id=token.user_id)
            return user.is_superuser
        except:
            return False


@api_view(['POST'])
def logging_in(request, format=None):
    if request.method == 'POST':
        email = request.data['email']
        password = request.data['password']
        password = hashlib.sha1(password).hexdigest()
        try:
            user = User.objects.get(email=email, password=password)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'success': True, 'message': 'Logged In',
                             'token': token.key, 'user_id': token.user_id})
        except:
            return Response({'success': False, 'message': "Invalid Credentials"},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def logging_out(request, pk):
    if request.method == 'GET':
        try:
            token = Token.objects.get(key=pk)
            token.delete()
            return Response({'success': True, 'message': 'Logged Out'},
                            status=status.HTTP_204_NO_CONTENT)
        except:
            return Response({'success': False, 'message': 'Token does not exist'},
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def list_users(request, format=None):
    if request.method == 'GET':
        if not is_superuser(request.META):
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
            auth_user = User(username=data['email'],
                             password=data['password'],
                             first_name=data['first_name'],
                             last_name=data['last_name'],
                             email=data['email'])
            auth_user.save()
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
        if (not is_authenticated(request.META, pk) and 
            not is_superuser(request.META)):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        auth_user = User.objects.get(id=pk)
        user = Users.objects.get(email=auth_user.email, deleted_flag=False)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
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
    if request.method == 'GET':
        if not is_superuser(request.META):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = {}
        schedule = Schedule.objects.all()
        serializer = ScheduleSerializer(schedule, many=True)
        try:
            response['data'] = serializer.data
            for resp in response['data']:
                resp['user_id'] = resp.get('user').get('id')
                del resp['user']
                del resp['checked']
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
            if (not is_authenticated(request.META, data['user_id']) and
                not is_superuser(request.META)):
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            auth_user = User.objects.get(id=data['user_id'])
            user = Users.objects.get(email=auth_user.email, deleted_flag=False)
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


@api_view(['GET', 'PUT'])
def user_schedule(request, pk, format=None):
    try:
        if (not is_authenticated(request.META, pk) and
            not is_superuser(request.META)):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        auth_user = User.objects.get(id=pk)
        user = Users.objects.get(email=auth_user.email, deleted_flag=False, verified=True)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    response = {}
    if request.method == 'GET':
        schedule = Schedule.objects.all().filter(user=user, checked=True)
        serializer = ScheduleSerializer(schedule, many=True)
        try:
            response['data'] = serializer.data
            for resp in response['data']:
                resp['user_id'] = resp.get('user').get('id')
                del resp['user']
                del resp['checked']
            response['status'] = {"success": True}
            return Response(response)
        except:
            response['status'] = {'success': False,
                                  'message': "Resource not available"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        # requires parameters in PUT body - Those names assumed
        response = {}
        if 'parameter_id' not in request.data.keys():
            response['status'] = {'success': False,
                                  'message': "Parameters missing"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        try:
            datadict = {"task": request.data['task'],
                        "scheduled_time": request.data['scheduled_time'],
                        "checked": request.data['checked']}
            up_sched, created = Schedule.objects.update_or_create(user=user,
                                                                  id=request.data['parameter_id'],
                                                                  defaults=datadict)
            up_sched.save()
            response['status'] = {'success': True,
                                  'message': "Field Updated"}
            return Response(response, status=status.HTTP_201_CREATED)
        except:
            response['status'] = {'success': False,
                                  'message': "Invalid or missing Fields"}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
