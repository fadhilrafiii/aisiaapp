from djongo import models
from django.utils import timezone


class ObjectDimension(models.Model):
    width = models.IntegerField()
    height = models.IntegerField

    class Meta:
        abstract = True


class Object(models.Model):
    _id = models.ObjectIdField()
    created_date = models.DateTimeField(auto_now_add=timezone.now)
    updated_date = models.DateTimeField(auto_now=timezone.now)
    img_url = models.CharField(verbose_name='url', max_length=200)
    img_name = models.CharField(verbose_name="name", max_length=50)
    img_size = models.IntegerField()
    img_dimension = models.JSONField()

    class Meta:
        db_table = "objects"
