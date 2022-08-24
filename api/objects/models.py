from django.utils import timezone
from djongo import models

class Annotation(models.Model):
    id = models.ObjectIdField()
    xmin = models.FloatField(null=True, blank=True)
    xmax = models.FloatField(null=True, blank=True)
    ymin = models.FloatField(null=True, blank=True)
    ymax = models.FloatField(null=True, blank=True)
    label = models.CharField(max_length=50, verbose_name='Image Label')

    objects = models.DjongoManager()

    db_table = "annotations"

class Object(models.Model):
    id = models.ObjectIdField()
    created_date = models.DateTimeField(auto_now_add=timezone.now)
    updated_date = models.DateTimeField(auto_now=timezone.now)
    img_url = models.CharField(verbose_name='url', max_length=200)
    img_name = models.CharField(verbose_name="name", max_length=50)
    img_size = models.IntegerField()
    img_dimension = models.JSONField()
    annotations = models.ArrayReferenceField(
        to=Annotation,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="annotations")

    objects = models.DjongoManager()
    class Meta:
        db_table = "objects"
