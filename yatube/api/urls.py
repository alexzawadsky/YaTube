from django.urls import include, path
from rest_framework.authtoken import views as authtokenviews
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()

router.register('posts', views.PostViewSet)
router.register('groups', views.GroupViewSet)
router.register(
    'posts/(?P<post_id>\\d+)/comments',
    views.CommentViewSet, basename='comment')

urlpatterns = [
    path('v1/api-token-auth/',
         authtokenviews.obtain_auth_token, name='api_token_auth'),
    path('v1/', include(router.urls)),
]
