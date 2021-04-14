from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.test_user = User.objects.create_user(
            username='testuser1',
            password='12345'
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.test_user,
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)
        cache.clear()

    def test_urls_status_200(self):
        """Проверка доступности адреса"""
        static_url = (
            reverse('index'),
            reverse('group', args=[self.group.slug]),
            reverse('profile', args=[self.test_user.username]),
            reverse('post', args=[self.test_user.username, self.post.id]),
        )
        for url in static_url:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_status_302(self):
        """Проверка доступности адреса"""
        static_url = (
            reverse('new_post'),
            reverse(
                'post_edit',
                args=[self.test_user.username, self.post.id]
            ),
        )
        for url in static_url:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_authorized_urls_status_200(self):
        """Проверка доступности адреса"""
        static_url = (
            reverse('new_post'),
            reverse(
                'post_edit',
                args=[self.test_user.username, self.post.id]
            ),
        )
        for url in static_url:
            with self.subTest():
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_url_uses_correct_template(self):
        """Проверка шаблона для адреса"""
        templates_url_names = {
            'index.html': reverse('index'),
            'group.html': reverse('group', args=[self.group.slug]),
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('new_post'): 'new_post.html',
            reverse(
                'post_edit',
                args=[self.test_user.username, self.post.id]
            ): 'new_post.html',
        }
        for reverse_name, template in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

