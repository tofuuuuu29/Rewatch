from rest_framework import serializers

from type.models import Type
from watched.categories import CATEGORIES, category_of
from watched.models import WatchEntry


class WatchEntrySerializer(serializers.ModelSerializer):
    # only used when adding a title to the list: which kind of title and which one
    category = serializers.ChoiceField(choices=list(CATEGORIES), write_only=True, required=False)
    title_id = serializers.IntegerField(write_only=True, required=False, min_value=1)

    username = serializers.CharField(source='user.username', read_only=True)
    media = serializers.SerializerMethodField()

    class Meta:
        model = WatchEntry
        fields = [
            'id',
            'username',
            'media',
            'category',
            'title_id',
            'status',
            'rating',
            'season',
            'episode',
            'notes',
            'date_started',
            'date_finished',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_media(self, obj):
        key = category_of(obj.type)
        if key is None:
            return None

        cfg = CATEGORIES[key]
        title = getattr(obj.type, cfg['field'])
        return {
            'category': key,
            'id': title.id,
            'title': getattr(title, cfg['name']),
            'poster_url': getattr(title, 'poster_url', ''),
        }

    def validate(self, data):
        if self.instance is None:
            errors = {}
            if 'category' not in data:
                errors['category'] = 'This field is required.'
            if 'title_id' not in data:
                errors['title_id'] = 'This field is required.'
            if errors:
                raise serializers.ValidationError(errors)
        else:
            # the title of an existing entry cannot be changed
            data.pop('category', None)
            data.pop('title_id', None)

        started = data.get('date_started', getattr(self.instance, 'date_started', None))
        finished = data.get('date_finished', getattr(self.instance, 'date_finished', None))
        if started and finished and finished < started:
            raise serializers.ValidationError(
                {'date_finished': 'The finish date cannot be before the start date.'}
            )

        return data

    def create(self, validated_data):
        user = validated_data.pop('user')
        category = validated_data.pop('category')
        title_id = validated_data.pop('title_id')
        cfg = CATEGORIES[category]

        try:
            title = cfg['model'].objects.get(pk=title_id)
        except cfg['model'].DoesNotExist:
            raise serializers.ValidationError({'title_id': 'This title does not exist.'})

        # reuse the Type row for this title, or create it
        type_obj = Type.objects.filter(**{cfg['field']: title}).first()
        if type_obj is None:
            type_obj = Type.objects.create(**{cfg['field']: title})

        if WatchEntry.objects.filter(user=user, type=type_obj).exists():
            raise serializers.ValidationError(
                {'title_id': 'This title is already on your list.'}
            )

        return WatchEntry.objects.create(user=user, type=type_obj, **validated_data)
