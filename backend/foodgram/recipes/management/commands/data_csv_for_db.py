import csv
import logging
import sys

from django.core.management.base import BaseCommand
from recipes.models import Ingredient, Tag

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(name)s, %(message)s',
)
handler.setFormatter(formatter)


class Command(BaseCommand):
    help = 'Импорт объектов в БД из CSV файлов'

    def handle(self, *args, **options):
        files_path = ['./data/ingredients.csv', './data/tags.csv']
        for index, file_path in enumerate(files_path, start=1):
            try:
                with open(file_path, encoding='utf8') as file:
                    obj_ingredient = []
                    obj_tag = []
                    reader = csv.reader(file)
                    for i, row in enumerate(reader, start=1):
                        if index == 1:
                            obj_ingredient.append(Ingredient(i, *row))
                        obj_tag.append(Tag(i, *row))
                    if obj_ingredient:
                        Ingredient.objects.bulk_create(obj_ingredient)
                    else:
                        Tag.objects.bulk_create(obj_tag)
                logger.info('Данные успешно записаны в БД')
            except Exception as error:
                logger.error(error, exc_info=True)
