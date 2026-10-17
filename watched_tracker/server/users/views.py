from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from config.permissions import IsAdminRole
from users.models import User
from users.serializers import UserSerializer


class UserListCreateView(APIView):

    def get_permissions(self):
        # anyone can register
        if self.request.method == 'POST':
            return [AllowAny()]

        # listing all users is admin only
        return [IsAuthenticated(), IsAdminRole()]

    # GET: Retrieve all users
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    # POST: Register a new user
    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserDetailView(APIView):

    def get_permissions(self):
        # view, edit and delete a user: admin only
        return [IsAuthenticated(), IsAdminRole()]

    # Helper function: Get a user by ID
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    # GET: Retrieve a specific user
    def get(self, request, pk):
        user = self.get_object(pk)

        if user is None:
            return Response(
                {'message': 'User does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user)
        return Response(serializer.data)

    # PUT: Update a user
    def put(self, request, pk):
        user = self.get_object(pk)

        if user is None:
            return Response(
                {'message': 'User does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE: Delete a user
    def delete(self, request, pk):
        user = self.get_object(pk)

        if user is None:
            return Response(
                {'message': 'User does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)