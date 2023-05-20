import base64

from django.core.files.base import ContentFile
from recipes.models import Tag
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """Кастомное поле сериализатора для
    кодирования и декодирования c помощью base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class TagListField(serializers.ListField):
    """Кастомное поле сериализатора для возврата объекто модели по id."""

    def to_internal_value(self, data):
        return Tag.objects.in_bulk(data)
