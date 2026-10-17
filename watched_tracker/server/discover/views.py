from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from discover.services import CATEGORIES, DiscoverError, search, trending


class DiscoverView(APIView):
    permission_classes = [IsAuthenticated]

    # GET /api/discover/?category=movies&q=parasite
    def get(self, request):
        category = request.query_params.get('category', '')
        query = request.query_params.get('q', '').strip()

        if category not in CATEGORIES:
            return Response(
                {'message': f"category must be one of: {', '.join(CATEGORIES)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(query) < 2:
            return Response([])

        try:
            return Response(search(category, query))
        except DiscoverError as e:
            return Response({'message': e.message}, status=e.status)


class TrendingView(APIView):
    # Public on purpose: the login page shows it before anyone has logged in.
    # No authentication classes, so an old or expired token in the browser can't cause a 401 here.
    authentication_classes = []
    permission_classes = [AllowAny]

    # GET /api/discover/trending/
    def get(self, request):
        return Response(trending())