from bson.objectid import ObjectId
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import serializers
from api.ml.serializers import MLSerializer
from api.objects.models import Object
from utils.file import get_file_size
from .models import ML
from utils.response import VsionResponse
from utils.pagination import VsionPagination
from utils.parse import parse_s3_path
from services.s3 import S3Service
from django_filters.rest_framework import DjangoFilterBackend

class MLViewSet(viewsets.ModelViewSet):
    serializer_class = ML
    queryset = ML.objects.all()
    lookup_field = "id"
    pagination_class = VsionPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['version']
    search_fields = ['name']
    ordering_fields = ['name', 'created_date', 'updated_date']

    response = VsionResponse("ML Model")
    s3_service = S3Service()

    def list(self, request):
        try:
            filtered_data = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(filtered_data)
            serializer = MLSerializer(page, many=True)
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

            model = ML.objects.get(pk=ObjectId(id))
            result = MLSerializer(model)

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

            if not "file" in request.FILES:
                raise KeyError({"file": ["A valid file is required."]})

            if not "version" in data:
                raise KeyError({"version": ["A valid integer is required."]})

            file = request.FILES["file"]

            # Check extension of model file
            [_, file_ext] = file.name.split(".")
            # if file_ext != "h5":
            #     raise KeyError({"file": ["File doesn't have '.h5' extension."]})

            # Upload file to S3
            file_size = get_file_size(file)
            folder_name = "ml-model"
            uploaded_file_path = self.s3_service.upload_file(
                file=file, folder_name=folder_name
            )

            # Add and cast rest data value
            data["file_path"] = parse_s3_path(uploaded_file_path)
            data["version"] = int(data["version"][0])
            data["file_size"] = file_size
            if "name" not in data:
                data["name"] = f'ML Model-{data["version"]}'
            validated_data = MLSerializer(data=data)

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
            data = ML.objects.get(pk=ObjectId(id))
            serialized_data = MLSerializer(data)
            file_path = serialized_data.data["file_path"]

            self.s3_service.delete_file(file_path)
            data.delete()

            response_data, status = self.response.delete_success(id)
            return Response(response_data, status)
        except ML.DoesNotExist:
            error_obj, status = self.response.delete_not_found(id)
            return Response(error_obj, status)
        except Exception as e:
            response_data, status = self.response.delete_failed(f"Error: {str(e)}")
            return Response(response_data, status)
