from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from tvseries.models import TvSeries
from tvseries.serializers import TvSeriesSerializer


class TvSeriesListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        series = TvSeries.objects.filter(user=request.user)
        serializer = TvSeriesSerializer(series, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TvSeriesSerializer(data=request.data, context={'request': request})

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


class TvSeriesDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            return TvSeries.objects.get(pk=pk, user=request.user)
        except TvSeries.DoesNotExist:
            return None

    def get(self, request, pk):
        series = self.get_object(request, pk)

        if series is None:
            return Response(
                {'message': 'TV series does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TvSeriesSerializer(series)
        return Response(serializer.data)

    def put(self, request, pk):
        series = self.get_object(request, pk)

        if series is None:
            return Response(
                {'message': 'TV series does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TvSeriesSerializer(series, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        series = self.get_object(request, pk)

        if series is None:
            return Response(
                {'message': 'TV series does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        series.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)