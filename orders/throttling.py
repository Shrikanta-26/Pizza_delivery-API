from rest_framework.throttling import UserRateThrottle


# Limit how often a user can create orders
class OrderCreateThrottle(UserRateThrottle):
    scope = "order_create"


# Limit how often a user can read their own orders
class UserOrderThrottle(UserRateThrottle):
    scope = "user_orders"


# Limit admin order reads
class AdminOrderReadThrottle(UserRateThrottle):
    scope = "admin_order_read"


# Limit admin order updates
class AdminOrderWriteThrottle(UserRateThrottle):
    scope = "admin_order_write"

# limit admin delete order
class AdminOrderDeleteThrottle(UserRateThrottle):
    scope = "admin_delete_order"