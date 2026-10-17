from rest_framework import serializers


class TitleSerializer(serializers.ModelSerializer):
    """Shared checks for movies, anime, kdrama and tvseries."""

    name_field = ''  # each subclass sets its own title column

    def _check_positive(self, value, label):
        if value is not None and value < 1:
            raise serializers.ValidationError(f'{label} must be 1 or higher.')
        return value

    # blank is allowed (None), but 0 and negative numbers are not
    def validate_season(self, value):
        return self._check_positive(value, 'Season')

    def validate_episode(self, value):
        return self._check_positive(value, 'Episode')

    def validate(self, data):
        name = data.get(self.name_field)

        if name is not None:
            # on edit, the owner is the title's owner; on create, it's the logged-in user
            if self.instance is not None:
                owner = self.instance.user
            else:
                request = self.context.get('request')
                owner = request.user if request else None

            if owner is not None:
                clash = self.Meta.model.objects.filter(
                    user=owner,
                    **{f'{self.name_field}__iexact': name}
                )
                if self.instance is not None:
                    clash = clash.exclude(pk=self.instance.pk)

                if clash.exists():
                    raise serializers.ValidationError(
                        {self.name_field: 'You already have this title.'}
                    )

        return data