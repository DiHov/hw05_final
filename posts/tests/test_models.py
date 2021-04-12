from django.contrib.auth.models import User
from django.test import TestCase

from posts.models import Group, Post


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Заголовок тестовой группы',
            slug='test-slug',
            description='Тестовое описание'
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task = GroupModelTest.group
        field_verboses = {
            'title': 'Имя группы',
            'slug': 'Ссылка для группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = GroupModelTest.group
        field_help_texts = {
            'title': 'Дайте имя группе',
            'slug': 'Задайте ссылку',
            'description': 'Опишите сообщество',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_field(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))


class PostModelTest(TestCase):
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

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        task = PostModelTest.post
        field_verboses = {
            'text': 'Текс нового поста',
            'pub_date': 'date published',
            'author': 'Автор поста',
            'group': 'Группа поста',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        task = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст своей записи',
            'author': 'Авторство присваивается автоматически',
            'group': 'Выберите группу для поста',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    task._meta.get_field(value).help_text, expected)

    def test_object_name_is_text(self):
        """__str__  post - это строчка с содержимым text[:15]"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))
