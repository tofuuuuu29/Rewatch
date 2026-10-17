from config.serializers import TitleSerializer
from kdrama.models import Kdrama


class KdramaSerializer(TitleSerializer):
    name_field = 'kdrama_name'

    class Meta:
        model = Kdrama
        fields = '__all__'
        read_only_fields = ['user']