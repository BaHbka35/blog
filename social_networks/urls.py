# Define URL patterns for social_networks
from django.contrib.auth.decorators import login_required

from django.urls import path
from . import views

app_name = 'social_networks'

urlpatterns = [
    # Clear mongodb
    path('delete/all/comments/mongodb', views.delete_all_comments_from_mongodb, 
        name="delete_all_comments_from_mongodb"),
    # Home page.
    path('', views.index, name='index'),
    # Page with list of topics.
    path('topics_list', views.topics_list, name='topics_list'),
    # Page with entries which belong specific topic.
    path('entries/xxx<int:topic_id>', views.entries_list, name="entries_list"),
    # Page of specific entry.
    path('entry/page/xxx<int:topic_id>/xxx<int:entry_id>', views.entry_page, name="entry_page"),
    # Create comment.
    path('create/comment/xxx<int:topic_id>/xxx<int:entry_id>', views.create_comment, name="create_comment"),
    # Page for creating new entries for specific topic.
    path('create/entry/xxx<int:topic_id>', views.create_entry, name='create_entry'),
    # Page for editin existing entry.
    path('edit/entry/xxx<int:entry_id>', views.edit_entry, name='edit_entry'),
    # Delete entry.
    path('delete/entry/xxx<int:entry_id>', views.delete_entry, name="delete_entry"),
    # Delete specidic comment.
    path('delete/comment/xxx<int:entry_id>xxx/xxx<str:comment_id>', views.delete_comment, name='delete_comment'),
    # Create subcomment for specific comment
    path('answer/on/comment/xxx<int:entry_id>/xxx<str:comment_id>/xxx<str:comment_answer_id>',
        views.add_subcomment,
        name='add_subcomment'),
    # Delete subcomment
    path('delete/answer/on/comment/xxx<int:entry_id>/xxx<str:comment_id>/xxx<str:answer_id>',
        views.delete_subcomment,
        name="delete_subcomment"),
    # Add like
    path('add_like/xxx<int:entry_id>/', views.add_like, name="add_like"),
    # Add dislike
    path('add_dislike/xxx<int:entry_id>/', views.add_dislike, name="add_dislike"),
]