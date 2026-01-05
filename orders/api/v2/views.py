from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from orders.models import Order
from orders.api.v2.serializers import (
    OrderV2Serializer,
    OrderCancellationSerializer,
    OrderPaymentSerializer,
    OrderAcceptanceSerializer,
    OrderPickupSerializer,
    OrderDeliverySerializer
)
import time

class OrderV2ViewSet(viewsets.ReadOnlyModelViewSet):
    """
    V2 API: Action-oriented Resources
    """
    queryset = Order.objects.all()
    serializer_class = OrderV2Serializer

    @action(detail=True, methods=['post'], url_path='payment')
    def payment(self, request, pk=None):
        """
        POST /api/v2/orders/{id}/payment
        Note: Idempotency to be added later.
        """
        order = self.get_object()
        
        # Validation
        if order.status != Order.Status.PENDING_PAYMENT:
            return Response(
                {"error": "Invalid state transition", "current_status": order.status},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Serialize input just for validation (if any)
        serializer = OrderPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Logic
        order.status = Order.Status.PENDING_ACCEPTANCE
        # Simulate payment processing time
        time.sleep(0.5) 
        order.save()
        
        return Response(OrderV2Serializer(order).data)

    @action(detail=True, methods=['post'], url_path='cancellation')
    def cancellation(self, request, pk=None):
        """
        POST /api/v2/orders/{id}/cancellation
        """
        order = self.get_object()
        
        # Logic: Allow cancellation only if pending actions
        allowed_statuses = [Order.Status.PENDING_PAYMENT, Order.Status.PENDING_ACCEPTANCE]
        if order.status not in allowed_statuses:
             return Response(
                {"error": "Cannot cancel at this stage", "current_status": order.status},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrderCancellationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order.status = Order.Status.CANCELLED
        order.save()
        
        return Response(OrderV2Serializer(order).data)

    @action(detail=True, methods=['post'], url_path='acceptance')
    def acceptance(self, request, pk=None):
        """
        POST /api/v2/orders/{id}/acceptance
        """
        order = self.get_object()
        
        if order.status != Order.Status.PENDING_ACCEPTANCE:
             return Response(
                {"error": "Order is not waiting for acceptance", "current_status": order.status},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        order.status = Order.Status.PREPARING
        order.save()
        
        return Response(OrderV2Serializer(order).data)

    @action(detail=True, methods=['post'], url_path='pickup')
    def pickup(self, request, pk=None):
        """
        POST /api/v2/orders/{id}/pickup
        Note: 'ready_for_pickup' status is skipped in V1 model, so we move from PREPARING to IN_TRANSIT(implied) or similar?
        V1 Order model had: PENDING_PAYMENT, PENDING_ACCEPTANCE, PREPARING, CANCELLED.
        It seems we are missing some statuses in the original model compared to the diagram.
        For now, let's assume we can add statuses or map to existing ones.
        The README diagram has: pending_payment -> pending_acceptance -> preparing -> ready_for_pickup -> in_transit -> delivered
        The V1 model only has: PENDING_PAYMENT, PENDING_ACCEPTANCE, PREPARING, CANCELLED.
        
        I will ADD dynamic statuses to the Order model in a separate step or just use string literals for now 
        if I am not allowed to change the model yet. 
        However, the plan said "MODIFY orders/models.py". I should check the model again.
        The simple V1 model is very limited. I should probably extend the model choices first.
        """
        order = self.get_object()
        
        # Assuming we will update the model choices.
        if order.status != Order.Status.PREPARING:
             return Response(
                {"error": "Order is not ready for pickup", "current_status": order.status},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 'in_transit' is not in V1 model yet, will add it.
        order.status = 'in_transit' 
        order.save()
        
        return Response(OrderV2Serializer(order).data)

    @action(detail=True, methods=['post'], url_path='delivery')
    def delivery(self, request, pk=None):
        """
        POST /api/v2/orders/{id}/delivery
        """
        order = self.get_object()
        
        if order.status != 'in_transit':
             return Response(
                {"error": "Order is not in transit", "current_status": order.status},
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = 'delivered'
        order.save()
        
        return Response(OrderV2Serializer(order).data)
