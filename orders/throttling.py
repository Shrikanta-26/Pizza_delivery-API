from rest_framework.throttling import UserRateThrottle,AnonRateThrottle


class UserOrderThrottle(UserRateThrottle):
    scope = 'specific_users_all_order'