# Define URL patterns for social_networks

from django.urls import path
from . import views

app_name = 'social_networks'

urlpatterns = [
    # Home page.
    path('', views.index, name='index'),
    # Page with list of topics.
    path('topics_list', views.topics_list, name='topics_list'),
    # Page with entries which belong specific topic.
    path('entries/xxx<int:topic_id>', views.entries, name="entries"),
    # Page of specific entry.
    path('entry/page/xxx<int:topic_id>/xxx<int:entry_id>', views.entry_page, name="entry_page"),
    # Page for creating new entries for specific topic.
    path('create/entry/xxx<int:topic_id>', views.create_entry, name='create_entry'),
    # Page for editin existing entry.
    path('edit/entry/xxx<int:entry_id>', views.edit_entry, name='edit_entry'),
    # Delete entry
    path('delete/entry/xxx<int:entry_id>', views.delete_entry, name="delete_entry"),
    #Delete specidic comment.
    path('delete/comment/xxx<int:entry_id>xxx/xxx<str:comment_id>', views.delete_comment, name='delete_comment')
]