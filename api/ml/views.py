import uuid
from bson.objectid import ObjectId
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from api.ml.constants import VALID_MODEL_TYPE, ModelType
from api.ml.serializers import MLSerializer

from .models import ML
from services import predict as PredictService
from services.s3 import S3Service
from utils.file import convert_base64_to_jpg, get_file_size
from utils.pagination import VsionPagination
from utils.parse import parse_s3_path
from utils.response import VsionResponse


class MLViewSet(viewsets.ModelViewSet):
    serializer_class = ML
    queryset = ML.objects.all()
    lookup_field = "id"
    pagination_class = VsionPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_date', 'updated_date']

    response = VsionResponse("ML Model")
    s3_service = S3Service()

    def list(self, request):
        try:
            query = request.GET

            if "last" in query and  query["last"] == "true":
                last_model = ML.objects.latest('updated_date')
                serializer = MLSerializer(last_model)

                response_data, status = self.response.retrieve_success('last', serializer.data)
                return Response(response_data, status)

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

            if "file" not in request.FILES:
                raise KeyError({"file": ["A valid file is required."]})

            file = request.FILES["file"]

            # Upload file to S3
            file_size = get_file_size(file)
            folder_name = "ml-model"
            uploaded_file_path = self.s3_service.upload_file(
                file=file, folder_name=folder_name
            )

            # Add and cast rest data value
            data["file_path"] = parse_s3_path(uploaded_file_path)
            data["file_size"] = file_size
            if "name" not in data:
                data["name"] = f'ML Model-{str(uuid.uuid4())}'
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

class PredictViewSet(viewsets.ModelViewSet):
    response = VsionResponse("ML Model")


    def create(self, request):
        data = request.data

        try:
            if 'image' not in data:
                raise KeyError({"image": ["A valid image is required."]})

            image = data["image"]

            if 'model' not in data:
                raise KeyError({"model": ["Model type is not specified. Try model='MobileNet'."]})


            model_type = data['model']
            if (model_type not in VALID_MODEL_TYPE):
                raise Exception(f"{model_type} is not included in valid model type! Current valid model type 'MobileNet'")

            img_name = 'img' + str(uuid.uuid4())
            img_file = convert_base64_to_jpg(image, img_name)

            if (model_type == ModelType.MOBILE_NET or model_type == ModelType.FASTER_RCNN):
                result = PredictService.get_predictions(img_file, model_type)
                response_data, status = self.response.predict_success(result)

                return Response(response_data, status)

        except KeyError as e:
            error_obj, status = self.response.params_invalid(e.args[0])
            return Response(error_obj, status)
        except Exception as e:
            response_data, status = self.response.predict_failed(f"Error: {str(e)}")
            return Response(response_data, status)



