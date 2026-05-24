from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import get_attribute
from products.models import Brand, Category, Product, ProductsImage, ShoeVariant, Review
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from users.serializers import UserSerializer
from users.models import User


class BrandSerializer(serializers.ModelSerializer):

    class Meta:
        model = Brand
        fields = ('id', 'name', 'logo_url')
        read_only_fields = ('id',)

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name', 'description')
        read_only_fields = ('id',)

class ProductsImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductsImage
        fields = ('id', 'product', 'image_url')
        read_only_fields = ('id',)

class ShoeVariantSerializer(serializers.ModelSerializer):
    product_display = serializers.StringRelatedField(source='product', read_only=True)

    class Meta:
        model = ShoeVariant
        fields = ('id', 'product', 'product_display', 'size', 'color', 'stock', 'sku')
        read_only_fields = ('id',)

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    user_display = UserSerializer(source='user', read_only=True)
    product_display = serializers.StringRelatedField(source='product', read_only=True)

    class Meta:
        model = Review
        fields = ('id','user','user_display','product','product_display','rating','comment','created_at')
        read_only_fields = ('id','created_at')

    def validate_rating(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError('Rating must be between 0 and 5')
        return value

class ProductSerializer(serializers.ModelSerializer):
    images = ProductsImageSerializer(many=True, read_only=True)
    variants = ShoeVariantSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'discount_price', 'gender', 'categories', 'brand', 'thumbnail', 'is_featured', 'updated_at', 'created_at', 'images', 'variants', 'reviews', 'effective_price')
        read_only_fields = ('id','updated_at', 'created_at')

    def create(self, validated_data):
        categories = validated_data.pop('categories', None)
        product = Product(**validated_data)
        try:
            product.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        with transaction.atomic():
            product.save()
            if categories is not None:
                product.categories.set(categories)
        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict)
        with transaction.atomic():
            instance.save()
            if categories is not None:
                instance.categories.set(categories)
        return instance

    def validate(self, data):
        price = data.get("price")
        discount = data.get("discount_price")

        if discount and discount > price:
            raise ValidationError('Discount price cannot exceed actual price')

        return data
