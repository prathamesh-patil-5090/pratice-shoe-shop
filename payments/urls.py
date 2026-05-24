

from rest_framework.routers import DefaultRouter
from rest_framework.urls import urlpatterns

from payments.views import PaymentViewSet



router = DefaultRouter()

router.register(r'payments', PaymentViewSet)

urlpatterns = router.urls
