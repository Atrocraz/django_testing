from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
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

    def test_pages_availability(self):
        urls = (
            ('users:login', None, None),
            ('users:logout', None, None),
            ('users:signup', None, None),
            ('notes:home', None, None),
            ('notes:list', None, self.reader),
            ('notes:success', None, self.reader),
            ('notes:add', None, self.reader),
            ('notes:edit', (self.notes.slug,), self.author),
            ('notes:delete', (self.notes.slug,), self.author),
            ('notes:detail', (self.notes.slug,), self.author),
        )
        for name, args, user in urls:
            if user is not None:
                self.client.force_login(user)

            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
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
