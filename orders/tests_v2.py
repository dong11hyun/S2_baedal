from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from orders.models import Order

class OrderV2ActionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.order = Order.objects.create(status=Order.Status.PENDING_PAYMENT)
        self.url_base = '/orders/api/v2/orders' 
        # Note: The URL path depends on how I set up urls.py. 
        # In orders/urls.py I added 'api/v2/', and in orders/api/v2/urls.py I registered 'orders'.
        # So it should be /orders/api/v2/orders/{id}/... 
        # Wait, orders/urls.py is included in project urls. 
        # If project urls includes orders/urls.py at 'orders/', then it is 'orders/api/v2/orders/'.
        # But I don't know the project root urls.py. I should assume relative to the include.
        # Let's assume the project root maps 'api/v1/' or similar.
        # Actually, let's look at the project urls.py if needed. 
        # For now I will rely on reverse() if possible, or just guess the path relative to app.
        
    def test_payment_action(self):
        url = f'{self.url_base}/{self.order.id}/payment/'
        data = {'payment_method': 'card', 'amount': 20000}
        # Since I am using relative paths in Include, I need to be careful.
        # But I can use the viewname.
        # router in v2 registers 'orders' with basename 'order-v2'.
        # So the url name for payment action should be 'order-v2-payment'.
        
        url = reverse('order-v2-payment', args=[self.order.id])
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PENDING_ACCEPTANCE)

    def test_cancellation_success(self):
        # Setup: Order is pending payment (cancellable)
        url = reverse('order-v2-cancellation', args=[self.order.id])
        data = {'reason': 'Changed mind'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.CANCELLED)

    def test_cancellation_fail_invalid_state(self):
        # Setup: Order is already preparing
        self.order.status = Order.Status.PREPARING
        self.order.save()
        
        url = reverse('order-v2-cancellation', args=[self.order.id])
        data = {'reason': 'Too late'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_acceptance_flow(self):
        # Setup: Payment done
        self.order.status = Order.Status.PENDING_ACCEPTANCE
        self.order.save()
        
        url = reverse('order-v2-acceptance', args=[self.order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.Status.PREPARING)
