from config.serializers import TitleSerializer
from tvseries.models import TvSeries


class TvSeriesSerializer(TitleSerializer):
    name_field = 'tv_series'

    class Meta:
        model = TvSeries
        fields = '__all__'
        read_only_fields = ['user']