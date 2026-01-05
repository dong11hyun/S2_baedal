from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderV1ViewSet

router = DefaultRouter()
router.register(r'orders', OrderV1ViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('v2/', include('orders.api.v2.urls')),
]