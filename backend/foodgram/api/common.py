from rest_framework import status
from rest_framework.response import Response


def add_del_obj_action(request, model, serializer, data):
    obj_exists = model.objects.filter(**data)
    if request.method == 'POST':
        serializer = serializer(data=data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    obj_exists.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


def get_is_field_action(request, model, data):
    user = None
    if request and hasattr(request, 'user'):
        user = request.user
    if not user:
        return False
    data.update({'user': user.id})
    is_exists = model.objects.filter(**data).exists()
    return is_exists
