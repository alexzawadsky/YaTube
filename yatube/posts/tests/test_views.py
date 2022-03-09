import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from yatube.settings import PAGINATOR_OBJECTS_ON_PAGE

from ..models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsWiewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.gif_name = 'small.gif'
        cls.uploaded = SimpleUploadedFile(
            name=cls.gif_name,
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

        user = PostsWiewsTests.user
        post = PostsWiewsTests.post
        group = PostsWiewsTests.group

        self.authorized_client = Client()
        self.authorized_client.force_login(user)

        self.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:groups'): 'posts/groups.html',
            reverse('posts:post_create'): 'posts/create_post.html',

            reverse('posts:group_number', kwargs={'slug': group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': user.username}):
                'posts/profile.html',
            reverse('posts:post_edit', kwargs={'post_id': post.id}):
                'posts/create_post.html',
            reverse('posts:post_detail', kwargs={'post_id': post.id}):
                'posts/post_detail.html',
        }
        self.templates_pages_names_errors = {
            '/unexisting_page': 'core/404.html'
        }
        self.url_names_response_forms_check = {
            'post_create':
                self.authorized_client.get(reverse('posts:post_create')),
            'post_edit':
                self.authorized_client.get(
                    reverse('posts:post_edit', kwargs={'post_id': post.id})
                ),
        }
        self.url_names_response_context_check = {
            'index': self.authorized_client.get(reverse('posts:index')),
            'group_number':
                self.authorized_client.get(
                    reverse('posts:group_number', kwargs={'slug': group.slug})
            ),
            'profile':
                self.authorized_client.get(
                    reverse(
                        'posts:profile', kwargs={'username': user.username}
                    )
            ),
        }
        self.url_names_response_groups = {
            'groups': self.authorized_client.get(reverse('posts:groups')),
        }

    def test_pages_posts_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_castom_errors_pages_correct_templates(self):
        """URL-адрес использует соответствующий шаблон ошибки."""
        for adress, template in self.templates_pages_names_errors.items():
            with self.subTest(reverse_name=adress):
                response = self.client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_pages_posts_correct_form_fields(self):
        """Шаблоны posts сформированы с правильным полями формы"""
        for response in self.url_names_response_forms_check.values():
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField,
            }

            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_pages_posts_show_correct_context(self):
        """Шаблоны posts сформированы с правильными контекстами"""
        post = PostsWiewsTests.post
        user = PostsWiewsTests.user
        gif_name = PostsWiewsTests.gif_name

        for response in self.url_names_response_context_check.values():
            first_object = response.context['page_obj'][0]
            post_text_0 = first_object.text
            post_id_0 = first_object.id
            post_author_username_0 = first_object.author.username
            post_group_id_0 = first_object.group.id
            post_image_name_0 = first_object.image.name
            self.assertEqual(post_text_0, post.text)
            self.assertEqual(post_id_0, post.id)
            self.assertEqual(post_author_username_0, user.username)
            self.assertEqual(post_group_id_0, post.id)
            self.assertEqual(post_image_name_0, f'posts/{gif_name}')

    def test_page_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        post = PostsWiewsTests.post
        user = PostsWiewsTests.user
        group = PostsWiewsTests.group
        gif_name = PostsWiewsTests.gif_name
        comment = PostsWiewsTests.comment

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post.id})
        )

        self.assertEqual(response.context.get('post').text, post.text)
        self.assertEqual(response.context.get('post').author.id, user.id)
        self.assertEqual(response.context.get('post').group.id, group.id)
        self.assertEqual(
            response.context.get('post').image.name,
            f'posts/{gif_name}'
        )

        self.assertEqual(
            response.context.get('comments')[:1][0].text,
            comment.text
        )
        self.assertEqual(
            response.context.get('comments')[:1][0].author.id,
            user.id
        )

    def test_subscribe(self):
        """Проверка возможности подписаться на пользователя"""
        user = PostsWiewsTests.user
        user_follow = User.objects.create_user(username='follow')

        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': user_follow.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=user,
                author=user_follow
            ).exists()
        )
        user_follow.delete()

    def test_unsubscribe(self):
        """Проверка возможности отподписаться от пользователя"""
        user = PostsWiewsTests.user
        user_follow = User.objects.create_user(username='follow')

        Follow.objects.create(
            user=user,
            author=user_follow
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': user_follow.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=user,
                author=user_follow
            ).exists()
        )
        user_follow.delete()

    def test_subscribe_to_yourself(self):
        """Проверка возможности подписаться на самого себя."""
        user = PostsWiewsTests.user
        follow_count = Follow.objects.count()

        respones = self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': user.username})
        )
        self.assertRedirects(
            respones,
            reverse('posts:profile', kwargs={'username': user.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=user,
                author=user
            ).exists()
        )
        self.assertEqual(follow_count, Follow.objects.count())

    def test_subscribe_to_yourself(self):
        """Проверка возможности подписаться несколько раз."""
        user_follow = User.objects.create_user(username='follow')

        follow_count = Follow.objects.count()

        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': user_follow.username})
        )
        respones_1 = self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': user_follow.username})
        )
        self.assertRedirects(
            respones_1,
            reverse('posts:profile', kwargs={'username': user_follow.username})
        )
        self.assertNotEqual(follow_count, Follow.objects.count() + 2)

    def test_follow_index(self):
        user = User.objects.create_user(username='user')
        user_follow = User.objects.create_user(username='user_follow')
        author = User.objects.create_user(username='author')

        user_authorized = Client()
        user_authorized.force_login(user)
        user_follow_authorized = Client()
        user_follow_authorized.force_login(user_follow)

        post = Post.objects.create(
            text='Пост для проверки подписки',
            author=author
        )
        Follow.objects.create(
            user=user_follow,
            author=author
        )
        response = user_authorized.get(reverse('posts:follow_index'))
        response_follow = user_follow_authorized.get(
            reverse('posts:follow_index')
        )
        self.assertFalse(
            response.context['posts_exist']
        )
        self.assertEqual(
            response_follow.context['page_obj'][0].id,
            post.id
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

        for i in range(2, 14):
            Group.objects.create(
                title=f'Тестовая группа {i}',
                slug=i,
                description=f'Тестовое описание {i}',
            )
        for i in range(2, 14):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )

    def setUp(self):
        user = PaginatorViewsTest.user
        group = PaginatorViewsTest.group

        self.authorized_client = Client()
        self.authorized_client.force_login(user)

        self.url_names_response_page_1 = {
            'index': self.client.get(reverse('posts:index')),
            'group_number':
                self.client.get(
                    reverse('posts:group_number', kwargs={'slug': group.slug})
            ),
            'profile':
                self.client.get(
                    reverse(
                        'posts:profile', kwargs={'username': user.username}
                    )
            ),
            'groups': self.client.get(reverse('posts:groups')),
        }

        self.url_names_response_page_2 = {
            'index': self.client.get(reverse('posts:index') + '?page=2'),
            'group_number':
                self.client.get(
                    reverse(
                        'posts:group_number',
                        kwargs={'slug': group.slug}) + '?page=2'
            ),
            'profile':
                self.client.get(
                    reverse(
                        'posts:profile', kwargs={'username': user.username}
                    ) + '?page=2'
            ),
            'groups': self.client.get(reverse('posts:groups') + '?page=2'),
        }

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        for response in self.url_names_response_page_1.values():
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']),
                    PAGINATOR_OBJECTS_ON_PAGE
                )

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        paginator_objects_on_last_page = (
            Post.objects.count() % PAGINATOR_OBJECTS_ON_PAGE
        )
        for response in self.url_names_response_page_2.values():
            with self.subTest(response=response):
                self.assertEqual(
                    len(response.context['page_obj']),
                    paginator_objects_on_last_page
                )
