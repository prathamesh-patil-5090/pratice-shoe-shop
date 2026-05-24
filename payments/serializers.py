from rest_framework import serializers
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_gateway', 'transaction_id', 'amount', 'status', 'paid_at')
        read_only_fields = ('id', 'paid_at')
