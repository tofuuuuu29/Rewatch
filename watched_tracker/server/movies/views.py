from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from movies.models import Movie
from movies.serializers import MovieSerializer


class MovieListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        movies = Movie.objects.filter(user=request.user)
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MovieSerializer(data=request.data, context={'request': request})

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


class MovieDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            return Movie.objects.get(pk=pk, user=request.user)
        except Movie.DoesNotExist:
            return None

    def get(self, request, pk):
        movie = self.get_object(request, pk)

        if movie is None:
            return Response(
                {'message': 'Movie does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MovieSerializer(movie)
        return Response(serializer.data)

    def put(self, request, pk):
        movie = self.get_object(request, pk)

        if movie is None:
            return Response(
                {'message': 'Movie does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = MovieSerializer(movie, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        movie = self.get_object(request, pk)

        if movie is None:
            return Response(
                {'message': 'Movie does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)