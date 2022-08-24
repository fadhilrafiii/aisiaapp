import json
from rest_framework import serializers

from .models import Annotation, Object


class AnnotationSerializer(serializers.ModelSerializer):
    box =  serializers.SerializerMethodField(read_only = True)
    xmin = serializers.FloatField(write_only=True)
    ymin = serializers.FloatField(write_only=True)
    xmax = serializers.FloatField(write_only=True)
    ymax = serializers.FloatField(write_only=True)

    def get_box(self, obj):
        return [obj.xmin, obj.ymin, obj.xmax, obj.ymax]

    class Meta:
        model = Annotation
        fields = [
            "label",
            "xmin",
            "ymin",
            "xmax",
            "ymax",
            "box",
        ]


class ObjectSerializer(serializers.ModelSerializer):
    annotations = AnnotationSerializer(many=True)

    def create(self, validated_data):
        annotations_data = validated_data.pop('annotations', [])

        created_annotations = []
        for annotation in annotations_data:
            created_annotation = Annotation.objects.create(**annotation)
            created_annotations.append(created_annotation)

        image_object = Object(**validated_data)
        image_object.annotations.add(*created_annotations)
        image_object.save()

        return image_object
    class Meta:
        model = Object
        fields = [
            'created_date',
            'updated_date',
            'img_url',
            'img_name',
            'img_size',
            'img_dimension',
            'annotations',
        ]


