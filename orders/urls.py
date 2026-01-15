from django.urls import path
from . import views

urlpatterns = [
    # Hello endpoint
    path('',views.HelloOrderView.as_view(), name='hello_orders'),
     
    # Orders: List & Create
    path('orders/',views.OrderCreateListView.as_view(),name='orders_list_create'),

    # Retrieve / Delete an order (Admin only)
    path('orders/<int:order_id>/',views.OrderDetailView.as_view(),name='order_retrieve_delete'),

    # Update order status (Admin only)
    path('orders/<int:order_id>/status/',views.UpdateOrderStatusView.as_view(),name='order_update_status'),

    # Full update order (User & Admin)
    path('orders/<int:order_id>/update/',views.UpdateOrderView.as_view(),name='order_full_update'),

    # Logged-in user's orders
    path('my/orders/',views.UserOrdersView.as_view(),name='my_orders_list'),
    path('my/orders/<int:order_id>/',views.UserOrderDetail.as_view(),name='my_order_detail'),

    # Admin fetching orders of any user
    path('user/<int:user_id>/orders/',views.UserOrdersView.as_view(),name='user_orders_list'),
    path('user/<int:user_id>/orders/<int:order_id>/',views.UserOrderDetail.as_view(),name='user_order_detail'),
]
