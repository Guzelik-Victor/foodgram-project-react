import csv
import os
import logging
import sys
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


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
        dirname = os.path.dirname(__file__)
        file_path = os.path.join(dirname, '../../../../../data/ingredients.csv')
        try:
            with open(file_path, encoding='utf8') as file:
                obj_list = []
                reader = csv.reader(file)
                for i, row in enumerate(reader):
                    obj_list.append(Ingredient(i, *row))
                Ingredient.objects.bulk_create(obj_list)
            logger.info('Данные успешно записаны в БД')
        except Exception as error:
            logger.error(error, exc_info=True)
