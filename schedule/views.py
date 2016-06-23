
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from .models import Users, Schedule
from .serializers import UserSerializer, ScheduleSerializer


@api_view(['GET', 'POST'])
def list_users(request, format = None):
    if request.method == 'GET':
        users = Users.objects.all().filter(verified=True)
        serializer = UserSerializer(users, many=True)
        responses = serializer.data
        for response in responses:
            del response['password']
            del response['verified']
        return Response(responses)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def get_users(request, pk, format = None):
    try:
        user = Users.objects.get(pk=pk)
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':     
        serializer = UserSerializer(user)
        response = serializer.data
        del response['password']
        del response['verified']
        return Response(response)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'GET'])
def schedule(request, format = None):
    print dict(request.session)
    if request.method == 'GET':
        schedule = Schedule.objects.all()
        serializer = ScheduleSerializer(schedule, many=True)
        try:
            return Response(serializer.data)
        except:
            pass
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ScheduleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def login(request):
    request.session['login'] = "Yes"
    return Response({}, status=status.HTTP_200_OK)


@api_view(['GET'])
def logout(request):
    request.session['login'] = "No"


@api_view(['GET','PUT'])
def user_schedule(request, pk, format=None):
    u_id = Users.objects.get(pk=pk)
    if request.method == 'GET':
        schedule = Schedule.objects.all().filter(user=u_id)
        serializer = ScheduleSerializer(schedule, many=True)
        try:
            return Response(serializer.data)
        except:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    #Not Yet Tested
    elif request.method == 'PUT':
        #requires parameters in PUT body - Those names assumed
        print request.data['first_name']
        if (not request.data['parameter_time'] or 
            not request.data['parameter_task']):
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        schedule_task = Schedule.objects.all().filter(user=u_id,
            task=request.data['parameter_task'],
                scheduled_time = request.data['parameter_time'])
        del data.request['parameter_time']
        del data.request['parameter_task']
        serializer = ScheduleSerializer(schedule_task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
