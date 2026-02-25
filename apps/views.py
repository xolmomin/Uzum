# from django_filters.rest_framework import DjangoFilterBackend
# from rest_framework.filters import SearchFilter
# from rest_framework.generics import ListAPIView, RetrieveAPIView
#
# from apps.models import City, DeliveryPoint
# from apps.serializer import CityListModelSerializer, DeliveryPointsListModelSerializer, \
#     DeliveryPointsRetrieveModelSerializer
#
#
# # Create your views here.
#
# class CityListAPIView(ListAPIView):
#     queryset = City.objects.all()
#     serializer_class = CityListModelSerializer
#     filter_backends = [SearchFilter]
#     search_fields = ['name']
#
#
# class DeliveryPointsListAPIView(ListAPIView):
#     queryset = DeliveryPoint.objects.only('address', 'has_dressing_room', 'location')
#     serializer_class = DeliveryPointsListModelSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['city']
#
#
# class DeliveryPointsRetrieveAPIView(RetrieveAPIView):
#     queryset = DeliveryPoint.objects.only('address', 'has_dressing_room', 'location', 'order_retention_period')
#     serializer_class = DeliveryPointsRetrieveModelSerializer

import uuid

from django.core.cache import cache
from django.core.files.storage import default_storage
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.db.models import Prefetch, Count, Q
from django.db.models.aggregates import Min
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from apps.consumers.CustomPagination import ChatHistoryPagination
from apps.filters import ProductFilter
from apps.models import City, DeliveryPoint, User, Message, Product, ProductVariantModel, ChatRoom
from apps.models.users import Store
from apps.serializers import (
    CityListModelSerializer,
    DeliveryPointsListModelSerializer,
    DeliveryPointsRetrieveModelSerializer, QRLoginStatusResponseSerializer, QRLoginRequestResponseSerializer,
    QRLoginAuthorizeRequestSerializer, MessageSerializer, ProductListFilterSerializer, ChatRoomListSerializer,
)
from utils import _generate_qr_image_base64

signer = TimestampSigner()


@extend_schema(tags=["User"])
class CityListAPIView(ListAPIView):
    queryset = City.objects.all()
    serializer_class = CityListModelSerializer
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["User"])
class DeliveryPointsListAPIView(ListAPIView):
    queryset = DeliveryPoint.objects.only("address", "has_dressing_room", "location")
    serializer_class = DeliveryPointsListModelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["city"]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["User"])
class DeliveryPointsRetrieveAPIView(RetrieveAPIView):
    queryset = DeliveryPoint.objects.only(
        "address", "has_dressing_room", "location", "order_retention_period"
    )
    serializer_class = DeliveryPointsRetrieveModelSerializer

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


@extend_schema(tags=["Auth"])
class QRCodeLoginRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        raw_token = uuid.uuid4().hex
        signed_token = signer.sign(raw_token)

        cache.set(f"auth:qr:{raw_token}", {"status": "pending", "created_at": timezone.now().isoformat()},
                  timeout=120, )

        qr_image = _generate_qr_image_base64(signed_token)

        data = {"token": raw_token, "qr_image": qr_image}
        serializer = QRLoginRequestResponseSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=["Auth"])
class QRCodeLoginAuthorizeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = QRLoginAuthorizeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        signed_token = serializer.validated_data["token"]
        try:
            raw_token = signer.unsign(signed_token, max_age=120)
        except (SignatureExpired, BadSignature):
            return Response({"detail": "QR kod eskirgan yoki noto'g'ri."}, status=400)

        key = f"auth:qr:{raw_token}"
        payload = cache.get(key)

        if not payload:
            return Response({"detail": "Token topilmadi yoki eskirgan."}, status=400)

        cache.set(key, {"status": "approved", "user_id": request.user.id}, timeout=60)
        return Response({"status": "Success"}, status=200)


@extend_schema(tags=["Auth"])
class QRCodeLoginStatusView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        token = request.query_params.get("token")
        if not token:
            return Response({"detail": "token is required"}, status=400)

        key = f"auth:qr:{token}"
        payload = cache.get(key)

        if not payload:
            return Response({"status": "expired"}, status=200)

        if payload.get("status") == "approved":
            user_id = payload.get("user_id")

            user = User.objects.get(id=user_id)

            refresh = RefreshToken.for_user(user)
            cache.delete(key)

            serializer = QRLoginStatusResponseSerializer(
                {"status": "approved", "access": str(refresh.access_token), "refresh": str(refresh), })
            return Response(serializer.data, status=200)

        return Response({"status": "pending"}, status=200)


@extend_schema(tags=["Chat"], )
class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MessageSerializer

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get("image")
        if not file_obj:
            return Response({"detail": "No image file provided."}, status=status.HTTP_400_BAD_REQUEST)

        path = default_storage.save(f"consumers/{file_obj.name}", file_obj)
        image_url = default_storage.url(path)

        return Response({"image_url": image_url}, status=status.HTTP_201_CREATED)


@extend_schema(tags=["Chat"])
class ChatRoomListView(ListAPIView):
    serializer_class = ChatRoomListSerializer

    def get_queryset(self):
        user = self.request.user
        qs = ChatRoom.objects.filter(Q(buyer=user) | Q(store__owner=user))

        qs = qs.annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
            )
        )

        return qs.prefetch_related(
            Prefetch(
                'messages',
                queryset=Message.objects.order_by('-timestamp'),
                to_attr='latest_message'
            )
        ).select_related('buyer', 'store')


@extend_schema(tags=["Chat"])
class ChatRoomGetOrCreateView(GenericAPIView):

    def post(self, request, store_id):
        user = request.user
        try:
            store = Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            return Response({"error": "Store topilmadi"}, status=status.HTTP_404_NOT_FOUND)

        room, created = ChatRoom.objects.get_or_create(buyer=user, store=store)

        return Response({"room_id": room.id, "is_new": created}, status=status.HTTP_200_OK)


@extend_schema(tags=["Chat"])
class ChatHistoryView(ListAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ChatHistoryPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    queryset = Message.objects.all()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        room_id = self.kwargs["room_id"]
        qs = Message.objects.filter(room_id=room_id).select_related("chat", "sender")

        before_id = self.request.query_params.get("before_id")
        if before_id:
            qs = qs.filter(id__lt=before_id)

        return qs.order_by("-timestamp")


@extend_schema(tags=["Filter"])
class ProductViewSet(ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListFilterSerializer
    filterset_class = ProductFilter

    def get_queryset(self):
        qs = super().get_queryset()

        qs = qs.annotate(starting_price=Min('variants__price'))

        return qs.select_related('brand', 'category').prefetch_related(
            Prefetch(
                'variants',
                queryset=ProductVariantModel.objects.all(),
                to_attr='all_variants'
            ),
            Prefetch(
                'variants',
                queryset=ProductVariantModel.objects.order_by('price'),
                to_attr='cheapest_variant'
            )
        )
