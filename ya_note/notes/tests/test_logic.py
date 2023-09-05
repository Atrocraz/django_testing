# news/tests/test_logic.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

from django.test import Client, TestCase

User = get_user_model()

NOTE_ADD_URL = 'notes:add'
NOTE_CREATE_URL = 'notes:success'
NOTE_DELETE_URL = 'notes:delete'
NOTE_EDIT_URL = 'notes:edit'
LOGIN_URL = 'users:login'

NOTE_DATA = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

NEW_DATA = {
            'title': 'New header',
            'text': 'New text',
            'slug': 'super-new-slug'
        }


class TestNoteCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Читатель простой')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.author)
        cls.url = reverse(NOTE_ADD_URL)
        cls.success_url = reverse(NOTE_CREATE_URL)
        cls.note_data = NOTE_DATA

    def test_anonimous_user_cant_creaste_note(self):
        response = self.client.post(self.url, data=self.note_data)
        login_url = reverse(LOGIN_URL)
        expected_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_authorized_user_can_creaste_note(self):
        response = self.auth_user.post(self.url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.note_data['title'])
        self.assertEqual(new_note.text, self.note_data['text'])
        self.assertEqual(new_note.slug, self.note_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_empty_slug_slugify(self):
        self.note_data.pop('slug')
        response = self.auth_user.post(self.url, data=self.note_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)

        new_note = Note.objects.get()
        expected_slug = slugify(self.note_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.author)
        cls.notes = Note.objects.create(
            title=NOTE_DATA['title'],
            text=NOTE_DATA['text'],
            slug=NOTE_DATA['slug'],
            author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_user_2 = Client()
        cls.auth_user_2.force_login(cls.reader)

    def test_slug_not_unique(self):
        response = self.auth_user.post(reverse(NOTE_ADD_URL), data=NOTE_DATA)

        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.notes.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        url = reverse(NOTE_EDIT_URL, args=(self.notes.slug,))
        response = self.auth_user.post(url, NEW_DATA)
        self.assertRedirects(response, reverse(NOTE_CREATE_URL))

        self.notes.refresh_from_db()
        self.assertEqual(self.notes.title, NEW_DATA['title'])
        self.assertEqual(self.notes.text, NEW_DATA['text'])
        self.assertEqual(self.notes.slug, NEW_DATA['slug'])

    def test_other_user_cant_edit_note(self):
        url = reverse(NOTE_EDIT_URL, args=(self.notes.slug,))
        response = self.auth_user_2.post(url, NEW_DATA)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.notes.id)
        self.assertEqual(self.notes.title, note_from_db.title)
        self.assertEqual(self.notes.text, note_from_db.text)
        self.assertEqual(self.notes.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        url = reverse(NOTE_DELETE_URL, args=(self.notes.slug,))
        response = self.auth_user.post(url)
        self.assertRedirects(response, reverse(NOTE_CREATE_URL))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        url = reverse(NOTE_DELETE_URL, args=(self.notes.slug,))
        response = self.auth_user_2.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
