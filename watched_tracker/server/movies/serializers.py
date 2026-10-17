from config.serializers import TitleSerializer
from movies.models import Movie


class MovieSerializer(TitleSerializer):
    name_field = 'movie_name'

    class Meta:
        model = Movie
        fields = '__all__'
        read_only_fields = ['user']