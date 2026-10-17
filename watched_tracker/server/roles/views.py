from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from config.permissions import IsAdminRole
from roles.models import Roles
from roles.serializers import RoleSerializer


class RoleListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsAdminRole()]

    def get(self, request):
        roles = Roles.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class RoleDetailView(APIView):

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]

        return [IsAuthenticated(), IsAdminRole()]

    def get_object(self, pk):
        try:
            return Roles.objects.get(pk=pk)
        except Roles.DoesNotExist:
            return None

    def get(self, request, pk):
        roles = self.get_object(pk)

        if roles is None:
            return Response(
                data={'message': 'Role does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RoleSerializer(roles)
        return Response(serializer.data)

    def put(self, request, pk):
        roles = self.get_object(pk)

        if roles is None:
            return Response(
                data={'message': 'Role does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = RoleSerializer(roles, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        roles = self.get_object(pk)

        if roles is None:
            return Response(
                data={'message': 'Role does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        roles.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)