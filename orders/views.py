from django.shortcuts import render,get_object_or_404
from rest_framework import generics,status
from rest_framework.response import Response
from .serializers import OrderCreationSerializer,OrderDetailSerializer,OrderStatusUpdateSerializer,DummySerializer,OrderUpdateSerializer
from .models import Order
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,IsAdminUser
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework.throttling import UserRateThrottle,AnonRateThrottle
from .throttling import UserOrderThrottle,OrderCreateThrottle,AdminOrderReadThrottle,AdminOrderWriteThrottle,AdminOrderDeleteThrottle

User=get_user_model()
# Create your views here.

class HelloOrderView(generics.GenericAPIView):
    serializer_class = DummySerializer
    throttle_classes = [UserRateThrottle,AnonRateThrottle]
    
    @swagger_auto_schema(operation_summary="Hello Orders")
    def get(self,request):
        return Response(data={"message":"Hello Orders"}, status=status.HTTP_200_OK)


class OrderCreateListView(generics.GenericAPIView):
    serializer_class = OrderCreationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_throttles(self):
        if self.request.method == "POST":
            return [OrderCreateThrottle()]
        return [AdminOrderReadThrottle()]
    

    @swagger_auto_schema(operation_summary="List all orders made")
    def get(self,request):
        orders = Order.objects.all()
        serializer = self.serializer_class(instance=orders,many=True)

        return Response(data=serializer.data,status=status.HTTP_200_OK)      
    
    @swagger_auto_schema(operation_summary="Create a new order")
    def post(self,request):
        data=request.data
        serializer=self.serializer_class(data=data)
        
        user = request.user

        if serializer.is_valid():
            serializer.save(customer=user)
            return Response(data=serializer.data,status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class OrderDetailView(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes=[IsAdminUser]
   
    def get_throttles(self):
        if self.request.method == "GET":
            return [AdminOrderReadThrottle()]  # throttle for retrieving orders
        if self.request.method == "DELETE":
            return [AdminOrderDeleteThrottle()]  # throttle for deleting orders
        return super().get_throttles() 


    @swagger_auto_schema(operation_summary="Retrieve an order by id")    
    def get(self,request,order_id):
        order=get_object_or_404(Order,pk=order_id)
        serializer=self.serializer_class(instance=order)
        return Response(data=serializer.data,status=status.HTTP_200_OK)
    
    @swagger_auto_schema(operation_summary="Remove an order")
    def delete(self,request,order_id):
        order=get_object_or_404(Order,pk=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UpdateOrderStatusView(generics.GenericAPIView):
    serializer_class=OrderStatusUpdateSerializer
    permission_classes = [IsAdminUser]

    def get_throttles(self):
        if self.request.method == "PUT":
            return [AdminOrderWriteThrottle()]
        return super().get_throttles()


    @swagger_auto_schema(operation_summary="Update an order status")  
    def put(self,request,order_id):
        order=get_object_or_404(Order,pk=order_id)
        data=request.data
        serializer=self.serializer_class(data=data,instance=order)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    

class UpdateOrderView(generics.GenericAPIView):
    serializer_class = OrderUpdateSerializer
    permission_classes = [IsAdminUser]

    def get_throttles(self):
        if self.request.method == "PUT":
            return [AdminOrderWriteThrottle()]
        return super().get_throttles()

    @swagger_auto_schema(operation_summary="Update an order by id")
    def put(self,request,order_id):
        data=request.data
        order=get_object_or_404(Order,pk=order_id)
        serializer=self.serializer_class(data=data,instance=order)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data,status=status.HTTP_200_OK)
        return Response(data=serializer.errors,status=status.HTTP_400_BAD_REQUEST)  


class UserOrdersView(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == "GET":
            return [UserOrderThrottle()]
        return super().get_throttles() 
   

    @swagger_auto_schema(operation_summary="Get all orders for a user")
    def get(self, request, user_id):
        user = get_object_or_404(User,pk=user_id)

        # Normal users can only see their own orders
        if not request.user.is_staff and request.user != user:
            return Response({"detail": "You do not have permission to view this user's orders."},status=status.HTTP_403_FORBIDDEN)

        orders = Order.objects.filter(customer=user)
        serializer = self.serializer_class(instance=orders, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
      

class UserOrderDetail(generics.GenericAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_throttles(self):
        if self.request.method == "GET":
            return [UserOrderThrottle()]
        return super().get_throttles()  
     
    @swagger_auto_schema(operation_summary="Get a user's specific order")
    def get(self,request,user_id,order_id):
        user=get_object_or_404(User, pk=user_id)
        if not request.user.is_staff and request.user != user:
            return Response(
                {"detail": "You do not have permission to view this user's orders."},
                status=status.HTTP_403_FORBIDDEN
            )
        order= get_object_or_404(Order,pk=order_id, customer=user)
        serializer=self.serializer_class(instance=order)

        return Response(data=serializer.data,status=status.HTTP_200_OK)
