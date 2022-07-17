from rest_framework import serializers

from .models import ML


class MLSerializer(serializers.ModelSerializer):
    class Meta:
        model = ML
        fields = "__all__"
