import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post


class ViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.test_user = User.objects.create_user(
            username='testuser',
            password='12345'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Текст тестового поста',
            author=cls.test_user,
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def post_at_page(self, response):
        if 'post' in response.context:
            first_object = response.context['post']
        else:
            first_object = response.context['page'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, self.post.author)
        self.assertEqual(post_text_0, self.post.text)
        self.assertEqual(post_group_0, self.post.group)
        self.assertEqual(post_image_0, self.post.image)

    def test_index_shows_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('index'))
        self.assertIn('page', response.context)
        self.post_at_page(response)

    def test_group_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': self.group.slug})
        )
        group = response.context['group']
        self.assertEqual(
            group.title,
            'Заголовок тестовой группы'
        )
        self.assertEqual(
            group.description,
            'Тестовое описание'
        )
        self.assertEqual(group.slug, self.group.slug)
        self.assertIn('page', response.context)
        self.post_at_page(response)

    def test_new_post_show_correct_context(self):
        """Шаблон post_new сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        """Шаблон edit_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post_edit', args=[self.test_user.username, self.post.id])
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('profile', args=[self.test_user.username])
        )
        self.assertEqual(response.context['author'].username, self.test_user)
        self.assertIn('page', response.context)
        self.post_at_page(response)

    def test_post_view_show_correct_context(self):
        """Шаблон post_view сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('post', args=[self.test_user.username, self.post.id])
        )
        self.assertEqual(response.context['author'].username, self.test_user)
        self.post_at_page(response)

    def test_404(self):
        '''Возвращает ли сервер код 404, если страница не найдена.'''
        response = self.guest_client.get('/unknownuser/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)