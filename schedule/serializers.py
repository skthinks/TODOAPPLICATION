
from rest_framework import serializers
from .models import Users, Schedule


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Users
        fields = ('id', 'first_name', 'last_name', 'email',
                  'password', 'verified', 'deleted_flag')


class ScheduleSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Schedule
        fields = ('id', 'task', 'scheduled_time', 'checked', 'user')
