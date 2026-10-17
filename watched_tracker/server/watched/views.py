from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from config.permissions import user_is_admin
from watched.categories import CATEGORIES, category_of
from watched.models import WatchEntry
from watched.serializers import WatchEntrySerializer

STATUSES = [key for key, _ in WatchEntry.STATUS_CHOICES]


def entries_for(request):
    """The user's own entries. Admins can add ?scope=all to see everybody's."""
    entries = WatchEntry.objects.select_related(
        'user',
        'type',
        'type__anime',
        'type__movie',
        'type__kdrama',
        'type__tv_series',
    )

    if request.query_params.get('scope') == 'all' and user_is_admin(request.user):
        return entries

    return entries.filter(user=request.user)


class WatchedListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # GET: my list. Filters: ?status=completed  ?category=anime
    def get(self, request):
        entries = entries_for(request)

        status_filter = request.query_params.get('status')
        if status_filter:
            if status_filter not in STATUSES:
                return Response(
                    {'message': f"status must be one of: {', '.join(STATUSES)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            entries = entries.filter(status=status_filter)

        category = request.query_params.get('category')
        if category:
            if category not in CATEGORIES:
                return Response(
                    {'message': f"category must be one of: {', '.join(CATEGORIES)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            field = CATEGORIES[category]['field']
            entries = entries.filter(**{f'type__{field}__isnull': False})

        serializer = WatchEntrySerializer(entries, many=True)
        return Response(serializer.data)

    # POST: add a title to my list
    def post(self, request):
        serializer = WatchEntrySerializer(data=request.data)

        if serializer.is_valid():
            entry = serializer.save(user=request.user)
            return Response(
                WatchEntrySerializer(entry).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class WatchedDetailView(APIView):
    permission_classes = [IsAuthenticated]

    # Helper function: an entry is only reachable by its owner (or an admin)
    def get_object(self, request, pk):
        entries = WatchEntry.objects.select_related(
            'user',
            'type',
            'type__anime',
            'type__movie',
            'type__kdrama',
            'type__tv_series',
        )

        if not user_is_admin(request.user):
            entries = entries.filter(user=request.user)

        return entries.filter(pk=pk).first()

    def not_found(self):
        return Response(
            {'message': 'Entry does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )

    # GET: one entry
    def get(self, request, pk):
        entry = self.get_object(request, pk)

        if entry is None:
            return self.not_found()

        return Response(WatchEntrySerializer(entry).data)

    # PUT: update an entry
    def put(self, request, pk):
        return self.update_entry(request, pk, partial=False)

    # PATCH: change just some fields, e.g. only the status
    def patch(self, request, pk):
        return self.update_entry(request, pk, partial=True)

    def update_entry(self, request, pk, partial):
        entry = self.get_object(request, pk)

        if entry is None:
            return self.not_found()

        serializer = WatchEntrySerializer(entry, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # DELETE: remove from my list
    def delete(self, request, pk):
        entry = self.get_object(request, pk)

        if entry is None:
            return self.not_found()

        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WatchedStatsView(APIView):
    permission_classes = [IsAuthenticated]

    # GET: totals for my list
    def get(self, request):
        entries = list(entries_for(request))

        by_status = {key: 0 for key in STATUSES}
        by_category = {key: 0 for key in CATEGORIES}
        ratings = []

        for entry in entries:
            by_status[entry.status] += 1

            category = category_of(entry.type)
            if category:
                by_category[category] += 1

            if entry.rating is not None:
                ratings.append(entry.rating)

        average = round(sum(ratings) / len(ratings), 1) if ratings else None

        return Response({
            'total': len(entries),
            'average_rating': average,
            'by_status': by_status,
            'by_category': by_category,
        })
