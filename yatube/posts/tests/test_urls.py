from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Post, Group, User
from http import HTTPStatus


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest = User.objects.create_user(username='guest')
        cls.user = User.objects.create_user(username='user')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test",
            description="Описание тестовой группы"
        )
        cls.userpost = Post.objects.create(
            text='Заголовок тестового поста авторизованного пользователя',
            group=cls.group,
            author=cls.user
        )
        cls.guestpost = Post.objects.create(
            text='Заголовок тестового поста неавторизованного пользователя',
            group=cls.group,
            author=cls.guest
        )

    def test_pages_access_all_users(self):
        urls_list = [
            reverse('index'),
            reverse('group', kwargs={'slug': self.group.slug}),
            reverse('profile', kwargs={'username': self.user.username}),
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.userpost.id
            }),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_access_authorized_users(self):
        urls_list = [
            reverse('new_post'),
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.userpost.id
            }),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_access_non_authorized_users(self):
        urls_list = [
            reverse('new_post'),
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.userpost.id
            }),
        ]
        for url in urls_list:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}"
                )

    def test_edit_post_access_anonymous_users(self):
        response = self.guest_client.get(
            reverse('post_edit', kwargs={
                'username': self.guest.username,
                'post_id': self.userpost.id
            }),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_post_access_authorized_author(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.userpost.id
            }),
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_post_access_authorized_non_author(self):
        response = self.authorized_client.get(
            reverse('post_edit', kwargs={
                'username': self.guest.username,
                'post_id': self.guestpost.id
            }),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            ('index.html', reverse('index')),
            ('group.html', reverse('group', kwargs={
                'slug': 'test'
            })),
            ('newpost.html', reverse('new_post')),
            ('newpost.html', reverse('post_edit', kwargs={
                'username': self.user.username,
                'post_id': self.userpost.id
            })),
        ]
        for template, reverse_name in templates_url_names:
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
