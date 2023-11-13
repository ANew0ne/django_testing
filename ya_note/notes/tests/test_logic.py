from http import HTTPStatus

import pytils
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class NoteCreationTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создает тестовые данные перед запуском тестов."""
        cls.author = User.objects.create(username='Комментатор')
        cls.form_data = {
            'text': 'Новый текст',
            'title': 'Новый заголовок',
            'slug': 'new_slug',
        }
        cls.form_empty_slug_data = {
            'text': 'Новый текст',
            'title': 'Новый заголовок',
        }
        cls.user = User.objects.create(
            username='Незарегистрированный пользователь'
        )
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='new_slug',
            author=cls.author
        )

    def test_logged_in_user_can_create_note(self):
        """Проверяет, что авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(
            reverse('notes:add'), data=self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cannot_create_note(self):
        """Проверяет, что анонимный пользователь не может создать заметку."""
        notes_count = Note.objects.count()
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={reverse("notes:add")}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), notes_count)

    def test_not_unique_slug(self):
        """
        Проверяет, что при попытке создать заметку с
        неуникальным slug выводится ошибка.
        """
        notes_count = Note.objects.count()
        self.auth_client.post(reverse('notes:add'), data=self.form_data)
        response = self.auth_client.post(
            reverse('notes:add'), data=self.form_data
        )
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), notes_count)

    def test_empty_slug(self):
        """
        Проверяет, что если при создании заметки не указан slug,
        он будет автоматически сгенерирован на основе заголовка заметки.
        """
        Note.objects.all().delete()
        self.auth_client.post(
            reverse('notes:add'), data=self.form_empty_slug_data
        )
        new_note = Note.objects.get()
        expected_slug = pytils.translit.slugify(new_note.title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Проверяет, что автор заметки может ее отредактировать."""
        response = self.author_client.post(
            reverse('notes:edit', args=(self.note.slug,)), self.form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """
        Проверяет, что другой пользователь не может
        отредактировать чужую заметку.
        """
        response = self.auth_client.post(
            reverse('notes:edit', args=(self.note.slug,)), self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Проверяет, что автор заметки может ее удалить."""
        response = self.author_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        notes_count = Note.objects.count()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), notes_count)

    def test_other_user_cant_delete_note(self):
        """
        Проверяет, что другой пользователь
        не может удалить чужую заметку.
        """
        notes_count = Note.objects.count()
        response = self.auth_client.post(
            reverse('notes:delete', args=(self.note.slug,))
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count)
