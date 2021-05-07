from django.test import TestCase
from posts.models import Post, Group, User


class PostsModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test",
            description="Описание тестовой группы"
        )
        cls.user = User.objects.create_user(username='Author')
        cls.post = Post.objects.create(
            text='Заголовок тестовой задачи',
            group=cls.group,
            author=cls.user
        )

    def test_verbose_name(self):
        post = PostsModelsTest.post
        field_verboses = {
            'text': 'Текст',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        post = PostsModelsTest.post
        field_help_texts = {
            'text': 'Текст поста',
            'group': 'Дайте короткое название группы'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_str(self):
        post = PostsModelsTest.post
        self.assertEqual(str(post), f'{post.author} | {post.text[:15]}')

    def test_group_str(self):
        group = PostsModelsTest.group
        self.assertEqual(str(group), group.title)
