import logging

from bson.objectid import ObjectId
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from .models import Object
from api.objects.constants import valid_images
from api.objects.serializers import ObjectSerializer
from services.s3 import S3Service
from utils.file import convert_img_to_jpg
from utils.file import get_file_size
from utils.file import get_img_dimension
from utils.file import get_valid_img_ext
from utils.pagination import VsionPagination
from utils.parse import parse_s3_path
from utils.response import VsionResponse
logger = logging.getLogger(__name__)


class ObjectViewSet(viewsets.ModelViewSet):
    serializer_class = Object
    lookup_field = "id"
    queryset = Object.objects.all()
    pagination_class = VsionPagination

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['img_name']
    ordering_fields = ['img_name', 'created_date', 'updated_date']

    response = VsionResponse("Image object")
    s3_service = S3Service()

    def list(self, request):
        try:
            filtered_data = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(filtered_data)
            serializer = ObjectSerializer(page, many=True)
            data = self.get_paginated_response(serializer.data)

            response_data, status = self.response.list_success(data.data)
            return Response(response_data, status)
        except Exception as e:
            error_obj, status = self.response.internal_server_error(str(e))
            return Response(error_obj, status)

    def retrieve(self, request, id=None):
        try:
            if not ObjectId.is_valid(id):
                raise KeyError()

            model = Object.objects.get(pk=ObjectId(id))
            result = ObjectSerializer(model)

            response_data, status = self.response.retrieve_success(id, result.data)
            return Response(response_data, status)
        except KeyError:
            error_obj, status = self.response.params_invalid(id)
            return Response(error_obj, status)
        except Exception as e:
            error_obj, status = self.response.retrieve_failed(f"Error: {str(e)}")
            return Response(error_obj, status)

    def create(self, request):
        try:
            data = request.POST.dict()

            if "file" not in request.FILES:
                raise KeyError({"file": ["An image file is required."]})

            file = request.FILES["file"]

            # Check image file extension
            file_ext = get_valid_img_ext(file.name)
            if not file_ext:
                raise KeyError(
                    {"file": [f"Accepted image file extensions are {valid_images}."]}
                )

            # Convert image to jpg
            img_file = convert_img_to_jpg(file)

            # Get img property
            img_dim = get_img_dimension(img_file)
            img_size = get_file_size(img_file)

            # Upload file to S3
            folder_name = "object-image"
            uploaded_file_path = self.s3_service.upload_file(
                file=img_file, folder_name=folder_name
            )

            # Add and cast rest data value
            data["img_name"] = file.name
            data["img_url"] = parse_s3_path(uploaded_file_path)
            data["img_size"] = img_size
            data["img_dimension"] = img_dim
            validated_data = ObjectSerializer(data=data)
            if not validated_data.is_valid():
                raise serializers.ValidationError(validated_data.errors)

            validated_data.save()

            response_data, status = self.response.create_success(validated_data.data)
            return Response(response_data, status)
        except KeyError as e:
            response_data, status = self.response.create_failed(e.args[0])
            return Response(response_data, status)
        except serializers.ValidationError as e:
            self.s3_service.delete_file(uploaded_file_path)
            response_data, status = self.response.create_failed(e.detail)
            return Response(response_data, status)
        except Exception as e:
            self.s3_service.delete_file(uploaded_file_path)
            response_data, status = self.response.create_failed(f"Error: {str(e)}")
            return Response(response_data, status)

    def destroy(self, request, id):
        try:
            data = Object.objects.get(pk=ObjectId(id))
            serialized_data = ObjectSerializer(data)
            img_url = serialized_data.data["img_url"]

            self.s3_service.delete_file(img_url)
            data.delete()

            response_data, status = self.response.delete_success(id)
            return Response(response_data, status)
        except Object.DoesNotExist:
            error_obj, status = self.response.delete_not_found(id)
            return Response(error_obj, status)
        except Exception as e:
            response_data, status = self.response.delete_failed(f"Error: {str(e)}")
            return Response(response_data, status)
