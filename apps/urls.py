from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.views import (CityListAPIView, DeliveryPointsListAPIView, DeliveryPointsRetrieveAPIView, ChatHistoryView,
                        ImageUploadView, ProductViewSet, ChatRoomListView, ChatRoomGetOrCreateView, )
from apps.users.views import (QRCodeLoginRequestView,QRCodeLoginAuthorizeView,QRCodeLoginStatusView,)

urlpatterns = [
    # Auth & JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # QR-code auth
    path("auth/qr/request/", QRCodeLoginRequestView.as_view(), name="qr_login_request"),
    path("auth/qr/authorize/", QRCodeLoginAuthorizeView.as_view(), name="qr_login_authorize"),
    path("auth/qr/status/", QRCodeLoginStatusView.as_view(), name="qr_login_status"),

    # Location APIs
    path("cities", CityListAPIView.as_view(), name="city_list_api"),
    path("delivery-points", DeliveryPointsListAPIView.as_view(), name="delivery_points_api"),
    path("delivery-points/<int:pk>", DeliveryPointsRetrieveAPIView.as_view(), name="delivery_point_api"),

    # Chat REST API
    path("rooms/", ChatRoomListView.as_view(), name="chat_rooms"),
    path("rooms/get-or-create/<int:store_id>/", ChatRoomGetOrCreateView.as_view(), name="chat_room_init"),
    path("rooms//history/<int:room_id>", ChatHistoryView.as_view(), name="chat_history"),
    path("upload-image/", ImageUploadView.as_view(), name="chat_image_upload"),

    #Filter
    path("", ProductViewSet.as_view(), name="products_list"),
]
