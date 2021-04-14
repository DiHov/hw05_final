import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, Comment


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.user = User.objects.create_user(
            username='testuser1',
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
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_guest_create(self):
        '''Проверка создания поста без авторизации'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Текст тестового поста',
            'image': self.uploaded
        }
        response = self.guest_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('login') + '?next=' + reverse('new_post')
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_create_post(self):
        '''Проверка создание нового поста'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Текст тестового поста',
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), post_count + 1)
        last_object = Post.objects.last()
        self.assertEqual(last_object.text, form_data['text'])
        self.assertEqual(last_object.author, self.user)
        self.assertEqual(last_object.group.id, form_data['group'])
        # self.assertEqual(last_object.image, self.uploaded)

    def test_edit_post(self):
        '''Проверка редактирования поста'''
        post = Post.objects.create(
            text='Текст тестового поста',
            author=self.user,
            group=self.group
        )
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Редактированный текст поста',
        }
        response = self.authorized_client.post(
            reverse('post_edit', args=[self.user.username, post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('post', args=[self.user.username, post.id])
        )
        self.assertEqual(Post.objects.count(), post_count)
        last_object = Post.objects.last()
        self.assertEqual(last_object.text, form_data['text'])
        self.assertEqual(last_object.author, self.user)
        self.assertEqual(last_object.group.id, form_data['group'])

    def test_add_guest_comment(self):
        '''Проверка создания коммента без авторизации'''
        post = Post.objects.create(
            text='Текст тестового поста',
            author=self.user,
            group=self.group
        )
        count = Comment.objects.count()
        form_data = {
            'text': 'Текст тестового коммента',
        }
        url_add = reverse('add_comment', args=[self.user.username, post.id])
        response = self.guest_client.post(
            url_add,
            data=form_data,
            follow=True
        )
        url_login = reverse('login')
        self.assertRedirects(
            response,
            f'{url_login}?next={url_add}'
        )
        self.assertEqual(Comment.objects.count(), count)


class FormFieldsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    def test_title_label(self):
        '''Проверка полей labels формы'''
        labels = {
            'group': 'Сообщество',
            'text': 'Текст записи',
        }
        for value, label in labels.items():
            with self.subTest():
                self.assertEqual(self.form.fields[value].label, label)

    def test_title_help_text(self):
        '''Проверка полей help_text формы'''
        help_texts = {
            'group': 'Выберите сообщество',
            'text': 'Введите о чем хотите написать',
        }
        for value, text in help_texts.items():
            with self.subTest():
                self.assertEqual(self.form.fields[value].help_text, text)
