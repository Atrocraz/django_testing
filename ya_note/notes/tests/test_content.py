# news/tests/test_content.py
from django.contrib.auth import get_user_model
from django.test import TestCase
# Импортируем функцию reverse(), она понадобится для получения адреса страницы.
from django.urls import reverse

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

    def test_check_list_for_diff_users(self):
        note_in_list = (
            (self.reader, False),
            (self.author, True),
        )

        for param_client, is_note_in_list in note_in_list:
            self.client.force_login(param_client)
            url = reverse('notes:list')
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertEqual((self.notes in object_list), is_note_in_list)

    def test_form_is_in_context(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
        )
        self.client.force_login(self.author)

        for name, args in urls:
            url = reverse(name, args=args)
            response = self.client.get(url)
            self.assertIn('form', response.context)
