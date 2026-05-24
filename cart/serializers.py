from rest_framework import serializers
from django.db import transaction
from cart.models import Cart, CartItem
from products.models import ShoeVariant


class CartItemSerializer(serializers.ModelSerializer):
    shoe_varient = serializers.PrimaryKeyRelatedField(queryset=ShoeVariant.objects.all())
    shoe_varient_display = serializers.StringRelatedField(source='shoe_varient', read_only=True)

    class Meta:
        model = CartItem
        fields = ('id', 'cart', 'shoe_varient', 'shoe_varient_display', 'quantity')
        read_only_fields = ('id', 'cart')

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, required=False)

    class Meta:
        model = Cart
        fields = ('id', 'user', 'created_at', 'cart_items')
        read_only_fields = ('id', 'created_at')

    def create(self, validated_data):
        cart_items_data = validated_data.pop('cart_items', [])
        with transaction.atomic():
            cart = Cart.objects.create(**validated_data)
            seen = set()
            for item in cart_items_data:
                sv = item['shoe_varient']
                if sv.id in seen:
                    raise serializers.ValidationError("Duplicate shoe_varient in cart_items.")
                seen.add(sv.id)
                CartItem.objects.create(cart=cart, shoe_varient=sv, quantity=item.get('quantity', 1))
        return cart

    def update(self, instance, validated_data):
        cart_items_data = validated_data.pop('cart_items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        with transaction.atomic():
            instance.save()
            if cart_items_data is not None:
                existing_items = {ci.shoe_varient_id: ci for ci in instance.cart_items.select_related('shoe_varient').all()}
                seen = set()
                for item in cart_items_data:
                    sv = item['shoe_varient']
                    if sv.id in seen:
                        raise serializers.ValidationError("Duplicate shoe_varient in cart_items.")
                    seen.add(sv.id)
                    qty = item.get('quantity', 1)
                    if sv.id in existing_items:
                        ci = existing_items.pop(sv.id)
                        if ci.quantity != qty:
                            ci.quantity = qty
                            ci.save()
                    else:
                        CartItem.objects.create(cart=instance, shoe_varient=sv, quantity=qty)
                # delete remaining items not present in the incoming data
                for ci in existing_items.values():
                    ci.delete()
        return instance
