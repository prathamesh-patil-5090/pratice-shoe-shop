
from rest_framework.routers import DefaultRouter
from rest_framework.urls import urlpatterns

from orders.views import OrderViewSet


router = DefaultRouter()

router.register(r'orders', OrderViewSet)

urlpatterns = router.urls
