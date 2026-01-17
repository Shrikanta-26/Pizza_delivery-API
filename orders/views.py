from django.shortcuts import render,get_object_or_404
from rest_framework import generics,status
from rest_framework.response import Response
from .serializers import OrderCreationSerializer,OrderDetailSerializer,OrderStatusUpdateSerializer,DummySerializer,OrderUpdateSerializer
from .models import Order
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.pagination import PageNumberPagination
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle
from .throttling import UserOrderThrottle,OrderCreateThrottle,AdminOrderReadThrottle,AdminOrderWriteThrottle,AdminOrderDeleteThrottle

User = get_user_model()

# Pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50



# Hello View
class HelloOrderView(generics.GenericAPIView):
    serializer_class = DummySerializer
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    @swagger_auto_schema(operation_summary="Hello Orders")
    def get(self, request):
        return Response({"message": "Hello Orders"}, status=status.HTTP_200_OK)


# Create & List Orders

class OrderCreateListView(generics.GenericAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreationSerializer
        return OrderDetailSerializer

    def get_throttles(self):
        if self.request.method == "POST":
            return [OrderCreateThrottle()]
        if self.request.user.is_staff:
            return [AdminOrderReadThrottle()]
        return [UserOrderThrottle()]

    @swagger_auto_schema(operation_summary="List all orders made")
    def get(self, request):
        orders = Order.objects.all()

        # Filtering

        status_filter = request.query_params.get('status')
        size_filter = request.query_params.get('size')
        search = request.query_params.get('search')
       
        if status_filter:
            orders = orders.filter(order_status=status_filter.upper())
        if size_filter:
            orders = orders.filter(size=size_filter.upper())
        if search:
            orders = orders.filter(Q(customer__username__icontains=search) | Q(id__icontains=search))

        #Pagination
        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(orders,request)

        serializer = self.get_serializer_class()(orders, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(operation_summary="Create a new order")
    def post(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(customer=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Retrieve / Delete Order by ID (Admin only)
class OrderDetailView(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAdminUser]

    def get_throttles(self):
        if self.request.method == "GET":
            return [AdminOrderReadThrottle()]
        if self.request.method == "DELETE":
            return [AdminOrderDeleteThrottle()]
        return super().get_throttles()

    @swagger_auto_schema(operation_summary="Retrieve an order by id")
    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_summary="Remove an order")
    def delete(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




# Update Order Status (Admin only)
class UpdateOrderStatusView(generics.GenericAPIView):
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [IsAdminUser]

    def get_throttles(self):
        if self.request.method == "PUT":
            return [AdminOrderWriteThrottle()]
        return super().get_throttles()

    @swagger_auto_schema(operation_summary="Update an order status")
    def put(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        serializer = self.serializer_class(instance=order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


# Full Update Order (User & Admin only)
class UpdateOrderView(generics.GenericAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == "PUT":
            if self.request.user.is_staff:
                return [AdminOrderWriteThrottle()]
            return [UserOrderThrottle()]
        return super().get_throttles()

    @swagger_auto_schema(operation_summary="Update an order by id")
    def put(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)

        # Permissions & restrictions
        if not request.user.is_staff:
            # Users can only update their own orders
            if order.customer != request.user:
                return Response({"detail": "You do not have permission to update this order."},status=status.HTTP_403_FORBIDDEN)
            # Users cannot update if order is in transit or delivered
            if order.order_status != Order.StatusChoices.PENDING:
                return Response({"detail": "Cannot update an order that is in transit or delivered."},status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(instance=order, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



# List all orders of a user
class UserOrdersView(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = [StandardResultsSetPagination]

    def get_throttles(self):
        return [UserOrderThrottle()]

    @swagger_auto_schema(operation_summary="Get all orders for a user")
    def get(self, request, user_id=None):
        # Admins can fetch any user's orders
        if request.user.is_staff and user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = request.user

        if not request.user.is_staff and user != request.user:
            return Response({"detail": "You do not have permission to view this user's orders."}, status=status.HTTP_403_FORBIDDEN)

        orders = Order.objects.filter(customer=user)

        # Filtering
        status_filter = request.query_params.get('status')
        size_filter = request.query_params.get('size')
        search = request.query_params.get('search')

        if status_filter:
            orders = orders.filter(order_status=status_filter.upper())
        if size_filter:
            orders = orders.filter(size=size_filter.upper())
        if search:
            orders = orders.filter(Q(id__icontains=search))

        paginator = StandardResultsSetPagination()
        result_page = paginator.paginate_queryset(orders, request)
        serializer = self.serializer_class(orders, many=True)
        return paginator.get_paginated_response(serializer.data)


# Retrieve a specific order for a user
class UserOrderDetail(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        return [UserOrderThrottle()]

    @swagger_auto_schema(operation_summary="Get a user's specific order")
    def get(self, request, order_id, user_id=None):
        # Admin can query any user
        if request.user.is_staff and user_id:
            user = get_object_or_404(User, pk=user_id)
        else:
            user = request.user

        if not request.user.is_staff and user != request.user:
            return Response({"detail": "You do not have permission to view this user's order."}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, pk=order_id, customer=user)
        serializer = self.serializer_class(order)
        return Response(serializer.data, status=status.HTTP_200_OK)