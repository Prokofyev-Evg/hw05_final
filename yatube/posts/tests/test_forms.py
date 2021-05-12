import shutil
import tempfile

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.models import Group, Post, User, Comment


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='leo')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post_authorized(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        post = Post.objects.last()
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.name.split('/')[-1],
                         form_data['image'].name)
        self.assertEqual(post.author, self.user)

    def test_create_post_nonauthorized(self):
        posts_count = Post.objects.count()
        client = Client()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'image': self.uploaded,
        }
        response = client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("new_post")}'
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post(self):
        post = Post.objects.create(
            text='Текст поста',
            group=self.group,
            author=self.user
        )
        new_form_data = {
            'text': 'Новый текст поста',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit', kwargs={
                    'username': post.author.username,
                    'post_id': post.id
                }
            ),
            data=new_form_data,
            follow=True
        )
        post = Post.objects.last()
        self.assertRedirects(response, reverse('post', kwargs={
            'username': post.author.username,
            'post_id': post.id
        }))
        self.assertEqual(post.text, new_form_data['text'])
        self.assertEqual(post.group, self.group)
        self.assertEqual(post.author, self.user)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Заголовок тестового поста',
            group=cls.group,
            author=cls.user
        )

    def test_comments_nonauthorized(self):
        client = Client()
        comment = 'Hello, world!'
        comments_count = Comment.objects.count()
        client.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            {'text': comment}
        )
        self.assertEqual(Comment.objects.count(), comments_count)

    def test_comments_authorized(self):
        commentator = User.objects.create_user(username='commentator')
        client = Client()
        comment = 'Hello, world!'
        client.force_login(commentator)
        comments_count = Comment.objects.count()
        client.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': self.user.username,
                    'post_id': self.post.id
                }
            ),
            {'text': comment}
        )
        last_comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(last_comment.text, comment)
        self.assertEqual(last_comment.author, commentator)
        self.assertEqual(last_comment.post, self.post)
