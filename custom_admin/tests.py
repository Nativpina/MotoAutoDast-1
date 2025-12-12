from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from MainApp.models import Compra, Cliente
from datetime import date

class AdminPagosViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='adminpassword'
        )
        self.regular_user = User.objects.create_user(
            username='user', email='user@example.com', password='userpassword'
        )
        self.pagos_url = reverse('pagos')

        # Create a client and some purchases for testing
        self.test_client_obj = Cliente.objects.create(
            nombre_cliente='Test Client', email='test@example.com', num=12345
        )
        self.compra1 = Compra.objects.create(
            fecha_compra=date(2023, 1, 1), cliente=self.test_client_obj, estado='pendiente', monto=100.00
        )
        self.compra2 = Compra.objects.create(
            fecha_compra=date(2023, 1, 2), cliente=self.test_client_obj, estado='enviado', monto=250.50
        )

    def test_pagos_view_redirects_if_not_logged_in(self):
        """
        The pagos view should redirect unauthenticated users to the login page.
        """
        response = self.client.get(self.pagos_url)
        self.assertRedirects(response, f'/accounts/login/?next={self.pagos_url}')

    def test_pagos_view_redirects_if_not_superuser(self):
        """
        The pagos view should redirect regular authenticated users to the home page.
        """
        self.client.login(username='user', password='userpassword')
        response = self.client.get(self.pagos_url)
        self.assertRedirects(response, '/')

    def test_pagos_view_accessible_by_superuser(self):
        """
        The pagos view should be accessible by superusers.
        """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(self.pagos_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/pagos.html')

    def test_pagos_view_context_data(self):
        """
        The pagos view should pass the correct Compra objects to the template context.
        """
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(self.pagos_url)
        self.assertIn('pagos', response.context)
        self.assertEqual(len(response.context['pagos']), 2)
        self.assertIn(self.compra1, response.context['pagos'])
        self.assertIn(self.compra2, response.context['pagos'])
        # Check ordering (most recent first)
        self.assertEqual(list(response.context['pagos']), [self.compra2, self.compra1])

    def test_pagos_view_no_purchases(self):
        """
        The pagos view should handle cases where there are no purchases.
        """
        Compra.objects.all().delete() # Remove existing purchases
        self.client.login(username='admin', password='adminpassword')
        response = self.client.get(self.pagos_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/pagos.html')
        self.assertIn('pagos', response.context)
        self.assertEqual(len(response.context['pagos']), 0)
