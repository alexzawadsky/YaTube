from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='auth1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.post1 = Post.objects.create(
            author=cls.user1,
            text='Тестовый пост 1',
        )

    def setUp(self):
        user = PostsUrlTests.user
        group = PostsUrlTests.group
        post = PostsUrlTests.post

        self.authorized_client = Client()
        self.authorized_client.force_login(user)

        self.url_status_guest = {
            '/': 200,
            f'/group/{group.slug}/': 200,
            f'/profile/{user.username}/': 200,
            f'/posts/{post.id}/': 200,
            f'/posts/{post.id}/edit/': 302,
            f'/posts/{post.id}/comment/': 302,
            '/create/': 302,
            '/unexisting_page': 404,
        }

        self.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{group.slug}/': 'posts/group_list.html',
            f'/profile/{user.username}/': 'posts/profile.html',
            f'/posts/{post.id}/': 'posts/post_detail.html',
            f'/posts/{post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def test_pages_guest_client(self):
        """Тестирует urls с неавторизованным пользователем"""
        for adress, status_code in self.url_status_guest.items():
            with self.subTest(adress=adress):
                response = self.client.get(adress)
                if status_code != 302:
                    self.assertEqual(
                        response.status_code,
                        status_code,
                        (f'Адрес {adress} выдал статус {response.status_code}'
                         f', ожидался {status_code}')
                    )
                else:
                    self.assertRedirects(
                        response,
                        (f'/auth/login/?next={adress}')
                    )

    def test_pages_authorized_client(self):
        """Тестирует urls с авторизованным пользователем"""
        post = PostsUrlTests.post

        self.url_status_guest['/create/'] = 200
        self.url_status_guest[f'/posts/{post.id}/edit/'] = 200

        for adress, status_code in self.url_status_guest.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    status_code,
                    (f'Адрес {adress} выдал статус {response.status_code}'
                     f', ожидался {status_code}')
                )

    def test_edit_post_authorized_client(self):
        """Тестирует невозможность редактирования поста другим юзером"""
        post1 = PostsUrlTests.post1

        response = self.authorized_client.get(f'/posts/{post1.id}/edit/')
        self.assertRedirects(
            response,
            (f'/posts/{post1.id}/')
        )

    def test_urls_posts_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
