from rest_framework.routers import DefaultRouter
from rest_framework.urls import urlpatterns

from products.views import BrandViewSet, CategoryViewSet, ProductViewSet, ReviewViewSet

router = DefaultRouter()

router.register(r'brands', BrandViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = router.urls
