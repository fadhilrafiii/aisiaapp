from rest_framework import routers
from .views import MLViewSet

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"", MLViewSet)

urlpatterns = router.urls
