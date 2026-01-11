from rest_framework import serializers
from .models import Order


class DummySerializer(serializers.Serializer):
    pass


# Create Serializer
class OrderCreationSerializer(serializers.ModelSerializer):
    size = serializers.CharField(max_length=20,help_text="Enter size as Small, Medium, Large, or Extra Large")
    order_status = serializers.HiddenField(default=Order.StatusChoices.PENDING)
    quantity = serializers.IntegerField(min_value=1,error_messages={'min_value': 'Quantity must be at least 1'}
    )

    class Meta:
        model = Order
        fields = ['id', 'size', 'order_status', 'quantity']

    # Convert human-readable size input to DB value
    def validate_size(self, value):
        for choice in Order.SizeChoices:
            if value.lower() == choice.label.lower():
                return choice.value
        raise serializers.ValidationError(
            f"Invalid size '{value}'. Must be one of: Small, Medium, Large, Extra Large"
        )


#  Detail / List Serializer
class OrderDetailSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'size', 'order_status', 'quantity', 'created_at', 'updated_at']

    # Human-readable size
    def get_size(self, obj):
        return obj.get_size_display()

    # Human-readable status
    def get_order_status(self, obj):
        return obj.get_order_status_display()


# Update Status Only Serializer 
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(
        help_text="Enter status as Pending, In Transit, or Delivered"
    )

    class Meta:
        model = Order
        fields = ['order_status']

    # Convert human-readable status input to DB value
    def validate_order_status(self, value):
        for choice in Order.StatusChoices:
            if value.lower() == choice.label.lower():
                return choice.value
        raise serializers.ValidationError(
            f"Invalid status '{value}'. Must be one of: Pending, In Transit, Delivered"
        )


# Full Update Serializer
class OrderUpdateSerializer(serializers.ModelSerializer):
    size = serializers.CharField(max_length=20,help_text="Enter size as Small, Medium, Large, or Extra Large"
    )
    order_status = serializers.CharField(help_text="Enter status as Pending, In Transit, or Delivered")
    quantity = serializers.IntegerField(min_value=1)

    class Meta:
        model = Order
        fields = ['size', 'order_status', 'quantity']

    # Validate size input
    def validate_size(self, value):
        for choice in Order.SizeChoices:
            if value.lower() == choice.label.lower():
                return choice.value
        raise serializers.ValidationError(
            f"Invalid size '{value}'. Must be one of: Small, Medium, Large, Extra Large"
        )

    # Validate status input
    def validate_order_status(self, value):
        for choice in Order.StatusChoices:
            if value.lower() == choice.label.lower():
                return choice.value
        raise serializers.ValidationError(
            f"Invalid status '{value}'. Must be one of: Pending, In Transit, Delivered"
        )
