from rest_framework import routers

from .views import MLViewSet, PredictViewSet

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"predict/", PredictViewSet, basename="ml-predict")
router.register(r"", MLViewSet)

urlpatterns = router.urls
