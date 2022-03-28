from django.urls import path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'Forum'
urlpatterns = [
        #  GET forums, POST forum
        path('', views.forum, name='forum'),

        # GET forum, DELETE forum
        path('<forum_id>', views.forum_detail, name='forum_detail'),

        # POST forum vote
        path('<forum_id>/vote', views.forum_vote, name='forum_vote'),

        # GET all comments, POST comment
        path('<forum_id>/comment', views.comment, name='comment'),

        # GET comment, DELETE comment
        path('<forum_id>/<comment_id>', views.comment_detail, name='comment_detail'),

        # POST comment vote
        path('<forum_id>/<comment_id>/vote', views.comment_vote, name='comment_vote'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
