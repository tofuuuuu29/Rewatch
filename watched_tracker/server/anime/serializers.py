from config.serializers import TitleSerializer
from anime.models import Anime


class AnimeSerializer(TitleSerializer):
    name_field = 'anime_name'

    class Meta:
        model = Anime
        fields = '__all__'
        read_only_fields = ['user']