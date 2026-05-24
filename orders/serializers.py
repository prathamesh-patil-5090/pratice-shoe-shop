from rest_framework import serializers
from django.db import transaction
from decimal import Decimal
from orders.models import Order, OrderItem
from products.models import ShoeVariant


class OrderItemSerializer(serializers.ModelSerializer):
    shoe_variant = serializers.PrimaryKeyRelatedField(queryset=ShoeVariant.objects.all())
    shoe_variant_display = serializers.StringRelatedField(source='shoe_variant', read_only=True)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'shoe_variant', 'shoe_variant_display', 'quantity', 'unit_price', 'total_price')
        read_only_fields = ('id', 'order', 'unit_price', 'total_price')

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer.")
        return value


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'user', 'total_amount', 'status', 'shipping_address', 'payment_method', 'created_at', 'order_items')
        read_only_fields = ('id', 'created_at', 'total_amount')

    def create(self, validated_data):
        items_data = validated_data.pop('order_items', [])
        with transaction.atomic():
            # lock variants to avoid race conditions
            variant_ids = [item['shoe_variant'].id for item in items_data]
            variants = ShoeVariant.objects.select_for_update().filter(id__in=variant_ids).select_related('product')
            variants_map = {v.id: v for v in variants}
            # validate stock availability
            for item in items_data:
                sv = item['shoe_variant']
                sv_locked = variants_map.get(sv.id)
                if sv_locked is None:
                    raise serializers.ValidationError({"order_items": f"ShoeVariant with id {sv.id} does not exist."})
                qty = item.get('quantity', 1)
                if sv_locked.stock < qty:
                    raise serializers.ValidationError({"order_items": f"Not enough stock for variant {sv_locked} (requested {qty}, available {sv_locked.stock})."})
            order = Order.objects.create(**validated_data)
            total = Decimal('0.00')
            for item in items_data:
                sv = variants_map[item['shoe_variant'].id]
                qty = item.get('quantity', 1)
                unit_price = sv.product.effective_price
                oi = OrderItem.objects.create(order=order, shoe_variant=sv, quantity=qty, unit_price=unit_price)
                # reduce stock
                sv.stock = sv.stock - qty
                sv.save()
                total += oi.total_price
            order.total_amount = total
            order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('order_items', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        with transaction.atomic():
            instance.save()
            if items_data is not None:
                # map old items by variant id
                old_items = {oi.shoe_variant_id: oi for oi in instance.order_items.select_related('shoe_variant').all()}
                new_map = {item['shoe_variant'].id: item.get('quantity', 1) for item in items_data}
                variant_ids = list(set(list(old_items.keys()) + list(new_map.keys())))
                variants = ShoeVariant.objects.select_for_update().filter(id__in=variant_ids).select_related('product')
                variants_map = {v.id: v for v in variants}
                # validate stock for increases
                for vid, new_qty in new_map.items():
                    old_qty = old_items.get(vid).quantity if vid in old_items else 0
                    delta = new_qty - old_qty
                    if delta > 0:
                        variant = variants_map.get(vid)
                        if variant is None:
                            raise serializers.ValidationError({"order_items": f"ShoeVariant with id {vid} does not exist."})
                        if variant.stock < delta:
                            raise serializers.ValidationError({"order_items": f"Not enough stock for variant {variant} (need {delta}, available {variant.stock})."})
                # apply changes
                # update existing or create new
                for item in items_data:
                    sv = item['shoe_variant']
                    qty = item.get('quantity', 1)
                    unit_price = sv.product.effective_price
                    if sv.id in old_items:
                        oi = old_items.pop(sv.id)
                        delta = qty - oi.quantity
                        if delta != 0:
                            sv.stock = sv.stock - delta
                            sv.save()
                        oi.quantity = qty
                        oi.unit_price = unit_price
                        oi.save()
                    else:
                        OrderItem.objects.create(order=instance, shoe_variant=sv, quantity=qty, unit_price=unit_price)
                        sv.stock = sv.stock - qty
                        sv.save()
                # delete removed items and restore stock
                for oi in old_items.values():
                    sv = oi.shoe_variant
                    sv.stock = sv.stock + oi.quantity
                    sv.save()
                    oi.delete()
                # recompute total_amount
                total = Decimal('0.00')
                for oi in instance.order_items.all():
                    total += oi.total_price
                instance.total_amount = total
                instance.save()
        return instance
