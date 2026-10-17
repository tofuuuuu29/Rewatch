from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from type.models import Type
from type.serializer import TypeSerializer


def own_types(user):
    # a Type row belongs to the user who owns the title it points to
    return Type.objects.filter(
        Q(anime__user=user) | Q(movie__user=user) |
        Q(tv_series__user=user) | Q(kdrama__user=user)
    )


class TypeListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    # GET: Retrieve all types
    def get(self, request):
        types = own_types(request.user)
        serializer = TypeSerializer(types, many=True)
        return Response(serializer.data)

    # POST: Create a new type
    def post(self, request):
        serializer = TypeSerializer(data=request.data, context={'request': request})

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


class TypeDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # Retrieve a type by ID
    def get_object(self, request, pk):
        try:
            return own_types(request.user).get(pk=pk)
        except Type.DoesNotExist:
            return None

    # GET: Retrieve a specific type
    def get(self, request, pk):
        item = self.get_object(request, pk)

        if item is None:
            return Response(
                {'message': 'Type does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TypeSerializer(item)
        return Response(serializer.data)

    # PUT: Update a type
    def put(self, request, pk):
        item = self.get_object(request, pk)

        if item is None:
            return Response(
                {'message': 'Type does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TypeSerializer(item, data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE: Delete a type
    def delete(self, request, pk):
        item = self.get_object(request, pk)

        if item is None:
            return Response(
                {'message': 'Type does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)