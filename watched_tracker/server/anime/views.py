from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from anime.models import Anime
from anime.serializers import AnimeSerializer


class AnimeListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    # GET: Retrieve all anime
    def get(self, request):
        anime = Anime.objects.filter(user=request.user)
        serializer = AnimeSerializer(anime, many=True)
        return Response(serializer.data)

    # POST: Create anime (Admin only)
    def post(self, request):
        serializer = AnimeSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AnimeDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # Helper function
    def get_object(self, request, pk):
        try:
            return Anime.objects.get(pk=pk, user=request.user)
        except Anime.DoesNotExist:
            return None

    # GET: Retrieve a specific anime
    def get(self, request, pk):
        anime = self.get_object(request, pk)

        if anime is None:
            return Response(
                {'message': 'Anime does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AnimeSerializer(anime)
        return Response(serializer.data)

    # PUT: Update anime (Admin only)
    def put(self, request, pk):
        anime = self.get_object(request, pk)

        if anime is None:
            return Response(
                {'message': 'Anime does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AnimeSerializer(anime, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE: Delete anime (Admin only)
    def delete(self, request, pk):
        anime = self.get_object(request, pk)

        if anime is None:
            return Response(
                {'message': 'Anime does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        anime.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)