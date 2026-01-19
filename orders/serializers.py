from rest_framework import serializers
from .models import Order


class DummySerializer(serializers.Serializer):
    pass


def  mappping_choice(value,choices,field_name):
    for choice in choices:
        if value.lower() == choice.label.lower():
            return choice.value
    raise serializers.ValidationError(f"Invalid {field_name} '{value}' . Must be one of: " + ", ".join(c.label for c in choices))          


# Create Serializer
class OrderCreationSerializer(serializers.ModelSerializer):
    size = serializers.CharField(max_length=20,help_text="Enter size as Small, Medium, Large, or Extra Large")
    order_status = serializers.HiddenField(default=Order.StatusChoices.PENDING)
    quantity = serializers.IntegerField(min_value=1,help_text="Must be at least 1")

    class Meta:
        model = Order
        fields = ['size', 'order_status', 'quantity']

    def validate_size(self, value):
        return mappping_choice(value, Order.SizeChoices,"size")
        


#  Detail / List Serializer
class OrderDetailSerializer(serializers.ModelSerializer):
    size = serializers.SerializerMethodField()
    order_status = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'customer','size', 'order_status', 'quantity', 'created_at', 'updated_at']

    def get_size(self, obj):
        return obj.get_size_display()

    def get_order_status(self, obj):
        return obj.get_order_status_display()
    
    def get_customer(self,obj):
        return {
            "id":obj.customer.id,
            "username":obj.customer.username,
            "email":obj.customer.email
        }


# Update Status Only Serializer 
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    order_status = serializers.CharField(
        help_text="Enter status as Pending, In Transit, or Delivered"
    )

    class Meta:
        model = Order
        fields = ['order_status']

   
    def validate_order_status(self, value):
        return mappping_choice(value,Order.StatusChoices,"status")


# Full Update Serializer
class OrderUpdateSerializer(serializers.ModelSerializer):
    size = serializers.CharField(max_length=20,help_text="Enter size as Small, Medium, Large, or Extra Large")
    order_status = serializers.CharField(help_text="Enter status as Pending, In Transit, or Delivered")
    quantity = serializers.IntegerField(min_value=1,help_text="Must be at least 1")

    class Meta:
        model = Order
        fields = ['size', 'order_status', 'quantity']

  
    def validate_size(self, value):
        return mappping_choice(value, Order.SizeChoices, "size")

    def validate_order_status(self, value):
        return mappping_choice(value, Order.StatusChoices, "status")
