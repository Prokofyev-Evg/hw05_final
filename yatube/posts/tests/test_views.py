import shutil
import tempfile

from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django import forms

from ..models import Post, Group, User, Follow, Comment


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='UserName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test_group",
            description="Описание тестовой группы"
        )
        cls.post = Post.objects.create(
            text='Заголовок тестового поста',
            group=cls.group,
            author=cls.user,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_pages_use_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'newpost.html': reverse('new_post'),
            'group.html': (
                reverse('group', kwargs={'slug': self.group.slug})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        self.check_post_context_on_page(response.context['page'][0])

    def test_index_paginator(self):
        batch_size = settings.PAGINATOR_PER_PAGE_VAL * 2
        objs = (Post(
            text='Test %s' % i,
            group=self.group,
            author=self.user
        ) for i in range(batch_size))
        Post.objects.bulk_create(objs, batch_size)
        response = self.authorized_client.get(reverse('index'))
        self.assertEqual(
            len(response.context['page']),
            settings.PAGINATOR_PER_PAGE_VAL
        )

    def test_group_correct_context(self):
        response = self.authorized_client.get((
            reverse('group', kwargs={'slug': self.group.slug})
        ))
        self.check_post_context_on_page(response.context['page'][0])

    def test_new_post_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_new_group_has_not_post(self):
        new_group = Group.objects.create(
            title="Новая тестовая группа",
            slug="new_group",
            description="Описание новой тестовой группы"
        )
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': new_group.slug})
        )
        self.assertEqual(response.context['page'].paginator.count, 0)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            )
        )
        self.check_post_context_on_page(response.context['post'])

    def test_profile_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.check_post_context_on_page(response.context['page'][0])

    def test_post_correct_context(self):
        response = self.authorized_client.get(
            reverse('post', kwargs={
                'username': self.user.username,
                'post_id': self.post.id
            })
        )
        self.check_post_context_on_page(response.context['post'])
        self.assertEqual(response.context['user'], self.user)

    def check_post_context_on_page(self, post_object):
        self.assertEqual(post_object.author, self.user)
        self.assertEqual(post_object.text, self.post.text)
        self.assertEqual(post_object.group, self.post.group)
        self.assertEqual(post_object.image, self.post.image)

    def test_cache(self):
        index_page = self.authorized_client.get(reverse('index')).content
        self.authorized_client.post(reverse('new_post'), {'text': 'Новый пост'})
        page_before = self.authorized_client.get(reverse('index')).content
        self.assertEqual(page_before, index_page)
        cache.clear()
        page_after = self.authorized_client.get(reverse('index')).content
        self.assertNotEqual(page_after, index_page)

    def test_follow(self):
        follower = User.objects.create_user(username='follower')
        client = Client()
        client.force_login(follower)
        response = client.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertContains(
            response,
            reverse(
                'profile_follow',
                kwargs={'username': self.user.username}
            )
        )
        # Check follow function
        response = client.get(
            reverse(
                'profile_follow',
                kwargs={'username': self.user.username}
            )
        )
        self.assertTrue(Follow.objects.filter(
            user=follower,
            author=self.user
        ).exists())
        response = client.get(reverse('follow_index'))
        self.assertIn(self.post, response.context['page'])

    def test_unfollow(self):
        follower = User.objects.create_user(username='follower')
        client = Client()
        client.force_login(follower)
        response = client.get(
            reverse(
                'profile_follow',
                kwargs={'username': self.user.username}
            )
        )
        response = client.get(
            reverse(
                'profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertContains(
            response,
            reverse(
                'profile_unfollow',
                kwargs={'username': self.user.username}
            )
        )

        # Check unfollow function
        response = client.get(
            reverse(
                'profile_unfollow',
                kwargs={'username': self.user.username}
            )
        )
        self.assertFalse(Follow.objects.filter(
            user=follower,
            author=self.user
        ).exists())
        response = client.get(reverse('follow_index'))
        self.assertNotIn(self.post, response.context['page'])
