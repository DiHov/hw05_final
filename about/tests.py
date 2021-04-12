from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class TaskURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exists_at_desired_location(self):
        """Проверка доступности адреса"""
        static_url = (
            reverse('about:author'),
            reverse('about:tech'),
        )
        for url in static_url:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса"""
        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
