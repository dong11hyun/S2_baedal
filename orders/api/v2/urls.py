from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderV2ViewSet

router = DefaultRouter()
router.register(r'orders', OrderV2ViewSet, basename='order-v2')

urlpatterns = [
    path('', include(router.urls)),
]
