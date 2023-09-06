from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

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

    def test_pages_availability(self):
        urls = (
            ('users:login', None, self.client),
            ('users:logout', None, self.client),
            ('users:signup', None, self.client),
            ('notes:home', None, self.client),
            ('notes:list', None, self.reader_client),
            ('notes:success', None, self.reader_client),
            ('notes:add', None, self.reader_client),
            ('notes:edit', (self.notes.slug,), self.author_client),
            ('notes:delete', (self.notes.slug,), self.author_client),
            ('notes:detail', (self.notes.slug,), self.author_client),
        )
        for name, args, param_client in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = param_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', (self.notes.slug,)),
            ('notes:delete', (self.notes.slug,)),
            ('notes:detail', (self.notes.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
