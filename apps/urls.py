from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from apps.views import CityListAPIView, DeliveryPointsListAPIView, DeliveryPointsRetrieveAPIView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('cities', CityListAPIView.as_view(), name='city_list_api'),
    # path('delivery-points', DeliveryPointsListAPIView.as_view(), name='delivery_points_api'),
    # path('delivery-points/<int:pk>', DeliveryPointsRetrieveAPIView.as_view(), name='delivery_point_api'),
]
