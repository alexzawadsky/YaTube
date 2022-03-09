import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='auth')
        cls.group = Group.objects.create(
            title='Тестовое название',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        user = PostsFormTests.user
        post = PostsFormTests.post

        self.authorized_client = Client()
        self.authorized_client.force_login(user)

        self.url_names_response = {
            'post_create': reverse('posts:post_create'),
            'profile':
                reverse('posts:profile', kwargs={'username': user.username}),
            'post_edit':
                reverse('posts:post_edit', kwargs={'post_id': post.id}),
            'post_detail':
                reverse('posts:post_detail', kwargs={'post_id': post.id}),
            'add_comment':
                reverse('posts:add_comment', kwargs={'post_id': post.id}),
        }

        self.post_text_create = 'Тестовый текст 1'
        self.post_text_edit = '*измененный*'

        self.post_comment_text_create = 'Новый комментарий'

        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.gif_name = 'small.gif'
        self.new_gif_name = 'new.gif'
        self.uploaded = SimpleUploadedFile(
            name=self.gif_name,
            content=self.small_gif,
            content_type='image/gif'
        )
        self.new_uploaded = SimpleUploadedFile(
            name=self.new_gif_name,
            content=self.small_gif,
            content_type='image/gif'
        )

    def test_create_post(self):
        group = PostsFormTests.group
        posts_count = Post.objects.count()

        form_data = {
            'text': self.post_text_create,
            'group': group.id,
            'image': self.uploaded,
        }

        response = self.authorized_client.post(
            self.url_names_response['post_create'],
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.url_names_response['profile'],
        )

        post = Post.objects.order_by('-id')[:1][0]
        self.assertEqual(post.text, self.post_text_create)
        self.assertEqual(post.group.id, group.id)
        self.assertEqual(post.image.name, f'posts/{self.gif_name}')
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_create_comment(self):
        post = PostsFormTests.post
        comment_count = Comment.objects.count()

        form_data = {
            'post': post.id,
            'text': self.post_comment_text_create
        }
        response = self.authorized_client.post(
            self.url_names_response['add_comment'],
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.url_names_response['post_detail'],
        )

        comment = Comment.objects.order_by('-id')[:1][0]
        self.assertEqual(comment.text, self.post_comment_text_create)
        self.assertEqual(comment.post.id, post.id)
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_edit_post(self):
        post = PostsFormTests.post
        group = PostsFormTests.group
        posts_count = Post.objects.count()

        form_data = {
            'text': self.post_text_edit,
            'group': group.id,
            'image': self.new_uploaded,
        }
        response = self.authorized_client.post(
            self.url_names_response['post_edit'],
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            self.url_names_response['post_detail'],
        )
        post = Post.objects.get(id=post.id)
        self.assertEqual(post.text, self.post_text_edit)
        self.assertEqual(post.group.id, group.id)
        self.assertEqual(post.image.name, f'posts/{self.new_gif_name}')
        self.assertEqual(Post.objects.count(), posts_count)
