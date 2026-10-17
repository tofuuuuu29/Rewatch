from rest_framework import serializers
from roles.models import Roles
from roles.models import Roles


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roles
        fields = '__all__'
        read_only_fields = ['id','created_at','updated_at']