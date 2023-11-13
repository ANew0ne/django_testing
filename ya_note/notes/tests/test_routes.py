from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед запуском тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.user = User.objects.create(
            username='Незарегистрированный пользователь'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test_slug',
            author=cls.author
        )
        cls.home_url = reverse('notes:home')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.success_url = reverse('notes:success')
        cls.add_url = reverse('notes:add')
        cls.list_url = reverse('notes:list')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_pages_availability(self):
        """Проверяет, что все страницы доступны анонимным пользователям."""
        urls = (
            self.home_url, self.login_url, self.logout_url, self.signup_url
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_auth_user(self):
        """
        Проверяет, что страницы добавления, списка заметок и успешного
        добавления заметки доступны только авторизованным пользователям.
        """
        urls = (self.success_url, self.add_url, self.list_url)
        for name in urls:
            with self.subTest(name=name):
                response = self.auth_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_author(self):
        """
        Проверяет, что страницы редактирования и удаления заметок
        доступны автору заметки.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (self.edit_url, self.delete_url, self.detail_url):
                with self.subTest(user=user, name=name):
                    response = self.client.get(name)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """
        Проверяет, что анонимные пользователи перенаправляются
        на страницу входа, когда пытаются открыть
        страницы редактирования и удаления заметок.
        """
        urls = (
            self.edit_url, self.delete_url, self.detail_url,
            self.add_url, self.list_url, self.success_url
        )
        for name in urls:
            with self.subTest(name=name):
                redirect_url = f'{self.login_url}?next={name}'
                response = self.client.get(name)
                self.assertRedirects(response, redirect_url)
