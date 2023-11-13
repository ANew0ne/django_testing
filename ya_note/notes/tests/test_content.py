from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesList(TestCase):
    """Тесты для списка заметок и формы редактирования заметки"""

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
            with self.subTest(user=user):
                self.client.force_login(user)
                url = reverse('notes:list')
                response = self.client.get(url)
                self.assertIn('object_list', response.context)
                object_list = response.context['object_list']
                self.assertIs((self.note in object_list), status)

    def test_pages_contains_form(self):
        """
        Проверяет, что на страницах добавления и
        редактирования заметки есть форма.
        """
        self.client.force_login(self.author)
        urls = (
            reverse('notes:add', None),
            reverse('notes:edit', args=(self.note.slug,)),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIsInstance(response.context.get('form'), NoteForm)
