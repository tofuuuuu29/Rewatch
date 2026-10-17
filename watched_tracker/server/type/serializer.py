from rest_framework import serializers
from type.models import Type


class TypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Type
        fields = '__all__'

    def validate(self, data):
        fields = ['anime', 'movie', 'tv_series', 'kdrama']

        if self.instance:
            for field in fields:
                if field not in data:
                    data[field] = getattr(self.instance, field)

        count = sum(
            data.get(field) is not None
            for field in fields
        )

        if count != 1:
            raise serializers.ValidationError(
                "Exactly one media type must be selected."
            )

        # a user can only link titles that belong to them
        request = self.context.get('request')
        if request is not None:
            for field in fields:
                title = data.get(field)
                if title is not None and title.user_id != request.user.id:
                    raise serializers.ValidationError(
                        "You can only link your own titles."
                    )

        return data