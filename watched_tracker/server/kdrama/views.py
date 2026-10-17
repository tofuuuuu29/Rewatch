from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from kdrama.models import Kdrama
from kdrama.serializers import KdramaSerializer


class KdramaListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        kdramas = Kdrama.objects.filter(user=request.user)
        serializer = KdramaSerializer(kdramas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = KdramaSerializer(data=request.data, context={'request': request})

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


class KdramaDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        try:
            return Kdrama.objects.get(pk=pk, user=request.user)
        except Kdrama.DoesNotExist:
            return None

    def get(self, request, pk):
        kdrama = self.get_object(request, pk)

        if kdrama is None:
            return Response(
                {'message': 'K-drama does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = KdramaSerializer(kdrama)
        return Response(serializer.data)

    def put(self, request, pk):
        kdrama = self.get_object(request, pk)

        if kdrama is None:
            return Response(
                {'message': 'K-drama does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = KdramaSerializer(kdrama, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        kdrama = self.get_object(request, pk)

        if kdrama is None:
            return Response(
                {'message': 'K-drama does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        kdrama.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)