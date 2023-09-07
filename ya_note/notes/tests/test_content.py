from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestConntext(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='test',
            author=cls.author
        )
        cls.reader = User.objects.create(username='Читатель простой')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

    def test_check_list_for_diff_users(self):
        note_in_list = (
            (self.reader_client, False),
            (self.author_client, True),
        )

        for param_client, is_note_in_list in note_in_list:
            with self.subTest():
                url = reverse('notes:list')
                response = param_client.get(url)
                all_notes = response.context['object_list']
                self.assertEqual((self.notes in all_notes), is_note_in_list)

    def test_form_is_in_context(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
        )

        for name, args in urls:
            with self.subTest():
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
