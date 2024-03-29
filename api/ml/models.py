from django.utils import timezone
from djongo import models


class ML(models.Model):
    id = models.ObjectIdField()
    created_date = models.DateTimeField(auto_now_add=timezone.now)
    updated_date = models.DateTimeField(auto_now=timezone.now)
    file_path = models.URLField()
    file_size = models.IntegerField(default=0)
    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = "file_model"
