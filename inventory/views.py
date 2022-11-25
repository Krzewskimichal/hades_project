import django.db.utils
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from collections.abc import Iterable
from django.contrib.auth.models import User
from django.shortcuts import get_list_or_404

from inventory.serializers import InventoryModelSerializer, ProjectModelSerializer, UserProjectModelSerializer,\
    LocalizationModelSerializer, InventoryStatusModelSerializer, InventoryTypeModelSerializer
from inventory.models import InventoryModel, ProjectModel, UserProjectModel, LocalizationModel, InventoryStatusModel,\
    InventoryTypeModel
from utils import get_jwt_data
from inventory.controller import check_token


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def project_crud(request: Request, pk=None) -> Response:
    """
        CRUD for project model
    """
    logged_user = check_token(request)
    if request.method == 'GET':
        if pk:
            project = get_object_or_404(ProjectModel, id=pk)
            serializer = ProjectModelSerializer(project)
        else:
            instance = [instance.project_id for instance in get_list_or_404(UserProjectModel, user_id=logged_user.id)]
            instance = ProjectModel.objects.filter(id__in=instance)
            serializer = ProjectModelSerializer(instance, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        try:
            project = ProjectModel(name=request.data.get('name'), company_name=request.data.get('company_name'))
            project.save()
            user_project = UserProjectModel(user_id=int(logged_user.id), project=project, role='OW')
            user_project.save()
            return Response({'message': f"Project {project.name} created"}, status=status.HTTP_200_OK)
        except django.db.utils.IntegrityError:
            return Response({'message': 'missing requirement parameters'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        if pk:
            project = get_object_or_404(ProjectModel, id=pk)
            serializer = ProjectModelSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': f"Project {project.name} updated"}, status=status.HTTP_200_OK)
            return Response({'message': f"Cannot update {project.name} project, data invalid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f"Missing project id!"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if pk:
            project = get_object_or_404(ProjectModel, id=pk)
            project.delete()
            return Response({'message': f"Project {project.name} has been deleted"}, status=status.HTTP_200_OK)
        return Response({'message': f"Missing project id!"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def localization_crud(request: Request, project_id=None, pk=None) -> Response:
    """
        crud for localization available in project
    """

    logged_user = check_token(request)
    if request.method == 'GET':
        if pk:
            localization = get_object_or_404(LocalizationModel, id=pk)
            serializer = ProjectModelSerializer(localization)
        else:
            instance = LocalizationModel.objects.filter(project_id=project_id)
            serializer = LocalizationModelSerializer(instance, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        try:
            project = get_object_or_404(ProjectModel, id=project_id)
            localization = LocalizationModel(project_id=project.id, place=request.data.get('place'))
            localization.save()
            return Response({'message': f"Localization: {localization.place} add to {project.name} project"}, status=status.HTTP_200_OK)
        except django.db.utils.IntegrityError:
            return Response({'message': 'missing requirement parameters'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        if pk:
            localization = get_object_or_404(LocalizationModel, id=pk)
            serializer = LocalizationModelSerializer(localization, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': f"Localization {localization.place} updated"}, status=status.HTTP_200_OK)
            return Response({'message': f"Cannot update {localization.place} localization, data invalid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f"Missing localization id!"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if pk:
            localization = get_object_or_404(LocalizationModel, id=pk)
            localization.delete()
            return Response({'message': f"Localization {localization.place} has been deleted"}, status=status.HTTP_200_OK)
        return Response({'message': f"Missing Localization id!"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def inventory_status_crud(request: Request, project_id=None, pk=None) -> Response:
    """
        crud for inventory status available in project
    """

    logged_user = check_token(request)
    if request.method == 'GET':
        if pk:
            inventory_status = get_object_or_404(InventoryStatusModel, id=pk)
            serializer = InventoryStatusModelSerializer(inventory_status)
        else:
            inventory_status = InventoryStatusModel.objects.filter(project_id=project_id)
            serializer = InventoryStatusModelSerializer(inventory_status, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        try:
            project = get_object_or_404(ProjectModel, id=project_id)
            inventory_status = InventoryStatusModel(project_id=project.id, status=request.data.get('status'))
            inventory_status.save()
            return Response({'message': f"Status: {inventory_status.status} add to {project.name} project"}, status=status.HTTP_200_OK)
        except django.db.utils.IntegrityError:
            return Response({'message': 'missing requirement parameters'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        if pk:
            inventory_status = get_object_or_404(InventoryStatusModel, id=pk)
            serializer = InventoryStatusModelSerializer(inventory_status, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': f"status {inventory_status.status} updated"}, status=status.HTTP_200_OK)
            return Response({'message': f"Cannot update {inventory_status.status} status, data invalid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f"Missing status id!"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if pk:
            inventory_status = get_object_or_404(InventoryStatusModel, id=pk)
            inventory_status.delete()
            return Response({'message': f"status {inventory_status.status} has been deleted"}, status=status.HTTP_200_OK)
        return Response({'message': f"Missing status id!"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def inventory_type_crud(request: Request, project_id=None, pk=None) -> Response:
    """
        crud for inventory status available in project
    """

    logged_user = check_token(request)
    if request.method == 'GET':
        if pk:
            inventory_type = get_object_or_404(InventoryTypeModel, id=pk)
            serializer = InventoryTypeModelSerializer(inventory_type)
        else:
            inventory_type = InventoryTypeModel.objects.filter(project_id=project_id)
            serializer = InventoryTypeModelSerializer(inventory_type, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        try:
            project = get_object_or_404(ProjectModel, id=project_id)
            inventory_type = InventoryTypeModel(project_id=project.id, name=request.data.get('name'))
            inventory_type.save()
            return Response({'message': f"Type: {inventory_type.name} add to {project.name} project"}, status=status.HTTP_200_OK)
        except django.db.utils.IntegrityError:
            return Response({'message': 'missing requirement parameters'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'PATCH':
        if pk:
            inventory_type = get_object_or_404(InventoryTypeModel, id=pk)
            serializer = InventoryTypeModelSerializer(inventory_type, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': f"type {inventory_type.name} updated"}, status=status.HTTP_200_OK)
            return Response({'message': f"Cannot update {inventory_type.name} type, data invalid"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': f"Missing type id!"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if pk:
            inventory_type = get_object_or_404(InventoryTypeModel, id=pk)
            inventory_type.delete()
            return Response({'message': f"type {inventory_type.name} has been deleted"}, status=status.HTTP_200_OK)
        return Response({'message': f"Missing type id!"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'message': 'invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def inventory_crud(request: Request, project_id=None, pk=None) -> Response:
    """
        crud for inventory status available in project
    """

    logged_user = check_token(request)
    if request.method == 'GET':
        if pk:
            inventory = get_object_or_404(InventoryModel, id=pk)
            serializer = InventoryModelSerializer(inventory)
        else:
            inventory = InventoryModel.objects.filter(project_id=project_id)
            serializer = InventoryModelSerializer(inventory, many=True)
        return Response(serializer.data)
    # elif request.method == 'POST':
    #     try:
    #         project = get_object_or_404(InventoryModel, id=project_id)
    #         inventory_type = InventoryTypeModel(project_id=project.id, data=request.data)
    #         inventory_type.save()
    #         return Response({'message': f"Type: {inventory_type.name} add to {project.name} project"}, status=status.HTTP_200_OK)
    #     except django.db.utils.IntegrityError:
    #         return Response({'message': 'missing requirement parameters'}, status=status.HTTP_400_BAD_REQUEST)
    # elif request.method == 'PATCH':
    #     if pk:
    #         inventory_type = get_object_or_404(InventoryTypeModel, id=pk)
    #         serializer = InventoryTypeModelSerializer(inventory_type, data=request.data, partial=True)
    #         if serializer.is_valid():
    #             serializer.save()
    #             return Response({'message': f"type {inventory_type.name} updated"}, status=status.HTTP_200_OK)
    #         return Response({'message': f"Cannot update {inventory_type.name} type, data invalid"}, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({'message': f"Missing type id!"}, status=status.HTTP_400_BAD_REQUEST)
    # elif request.method == 'DELETE':
    #     if pk:
    #         inventory_type = get_object_or_404(InventoryTypeModel, id=pk)
    #         inventory_type.delete()
    #         return Response({'message': f"type {inventory_type.name} has been deleted"}, status=status.HTTP_200_OK)
    #     return Response({'message': f"Missing type id!"}, status=status.HTTP_400_BAD_REQUEST)
    # return Response({'message': 'invalid method'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)