from django.urls import path
from . import views

app_name = "comments" 


urlpatterns = [
# Clear mongodb
    path('delete/all/comments/mongodb', views.delete_all_comments_from_mongodb, 
        name="delete_all_comments_from_mongodb"),
        # Create comment.
    path('create/comment/xxx<int:topic_id>/xxx<int:entry_id>', 
        views.create_comment, name="create_comment"),
    # Delete specidic comment.
    path('delete/comment/xxx<int:entry_id>xxx/xxx<str:comment_id>', 
        views.delete_comment, name='delete_comment'),
    # Create subcomment for specific comment
    path('answer/on/comment/xxx<int:entry_id>/xxx<str:comment_id>/xxx<str:comment_answer_id>',
        views.add_subcomment,
        name='add_subcomment'),
    # Delete subcomment
    path('delete/answer/on/comment/xxx<int:entry_id>/xxx<str:comment_id>/xxx<str:answer_id>',
        views.delete_subcomment,
        name="delete_subcomment"),

]
