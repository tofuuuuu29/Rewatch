from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from users.models import User
from roles.models import Roles


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'username',
            'password',
            'email',
            'gender',
            'role'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'role': {'read_only': True}
        }

    def validate(self, data):
        # the password is required when registering, but optional when editing a user
        if self.instance is None and not data.get('password'):
            raise serializers.ValidationError(
                {'password': 'This field is required.'}
            )
        return data

    def create(self, validated_data):
        # Assign the normal User role automatically
        try:
            user_role = Roles.objects.get(name__iexact='User')
        except Roles.DoesNotExist:
            raise serializers.ValidationError(
                {'role': 'The default User role does not exist.'}
            )

        validated_data['role'] = user_role
        validated_data['password'] = make_password(
            validated_data['password']
        )

        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            validated_data['password'] = make_password(
                validated_data['password']
            )

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance