from rest_framework import filters, viewsets
from rest_framework.permissions import IsAuthenticated
from products.models import Brand, Category, Product, Review
from products.serializers import BrandSerializer, CategorySerializer, ProductSerializer, ReviewSerializer

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.select_related('brand').prefetch_related(
        'categories',
        'images',
        'variants',
        'reviews'
    )
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created-at', 'updated-at']
