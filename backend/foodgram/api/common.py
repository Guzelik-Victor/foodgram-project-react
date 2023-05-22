from recipes.models import IngredientRecipe, TagRecipe
from rest_framework import status
from rest_framework.response import Response


def add_del_obj_action(request, model, serializer, data):
    """Функция для добавления и удаления данных в модели Favorite,
    Follow, ShoppingCart."""

    obj_exists = model.objects.filter(**data)
    if request.method == 'POST':
        serializer = serializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )
    obj_exists.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_is_field_action(request, model, data):
    """Функция для фильтрации queryset по заданным параметрам."""

    user = None
    if request and hasattr(request, 'user'):
        user = request.user
    if not user:
        return False
    data.update({'user': user.id})
    return model.objects.filter(**data).exists()


def create_update_instance_recipe(recipe, ingredients, tags):
    obj_tag_recipe = []
    obj_ingredient_recipe = []

    for data in ingredients:
        obj_ingredient_recipe.append(
            IngredientRecipe(
                recipe=recipe,
                ingredient=data['ingredient'].get('id'),
                amount=data.get('amount'),
            )
        )
    IngredientRecipe.objects.bulk_create(obj_ingredient_recipe)

    for tag in tags.values():
        obj_tag_recipe.append(
            TagRecipe(recipe=recipe, tag=tag)
        )
    TagRecipe.objects.bulk_create(obj_tag_recipe)

    return
