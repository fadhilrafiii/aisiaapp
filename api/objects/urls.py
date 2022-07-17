from rest_framework import routers

from .views import ObjectViewSet

router = routers.SimpleRouter(trailing_slash=False)

router.register(r"", ObjectViewSet)

urlpatterns = router.urls
