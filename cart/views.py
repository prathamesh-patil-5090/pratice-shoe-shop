
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from cart.models import Cart
from cart.serializers import CartSerializer


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
