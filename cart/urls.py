

from rest_framework.routers import DefaultRouter
from rest_framework.urls import urlpatterns

from cart.views import CartViewSet



router = DefaultRouter()

router.register(r'cart', CartViewSet)

urlpatterns = router.urls
