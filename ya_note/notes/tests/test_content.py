from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesList(TestCase):
    """Тесты для списка заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед запуском тестов."""
        cls.author = User.objects.create(username='Комментатор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug_for_args',
            author=cls.author
        )

    def test_notes_list_for_different_users(self):
        """
        Проверяет доступность списка заметок для авторизованного
        и неавторизованного пользователей.
        """
        users_statuses = (
            (self.author, True),
            (self.reader, False),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual((self.note in object_list), status)


class TestNoteForm(TestCase):
    """Тесты для формы добавления/редактирования заметки."""

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед запуском тестов."""
        cls.author = User.objects.create(username='Автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug_for_args',
            author=cls.author
        )

    def test_add_page_contains_form(self):
        """Проверяет, что на странице добавления заметки есть форма."""
        self.client.force_login(self.author)
        url = reverse('notes:add')
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_edit_page_contains_form(self):
        """Проверяет, что на странице редактирования заметки есть форма."""
        self.client.force_login(self.author)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertIsInstance(response.context['form'], NoteForm)
