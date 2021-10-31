from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound

from .services.comments_sevices import create_comment_for_specific_entry, \
    delete_main_comment_and_its_subcomment,\
    add_subcomment_for_specific_comment, \
    delete_subcomment_and_its_subcomments

from .services.mongodb_services import delete_comments_from_mongodb


@login_required
def create_comment(request, topic_id, entry_id):
    """ Create comment for specific entry and writes them to mongodb"""

    return create_comment_for_specific_entry(request, entry_id)


@login_required
def delete_comment(request, entry_id, comment_id):
    """ Delete specific comment for entry and its subcomments."""
   
    return delete_main_comment_and_its_subcomment(request, entry_id, comment_id)


@login_required
def add_subcomment(request, entry_id, comment_id, comment_answer_id):
    """ Add subcomment for specific comment and write it to mongodb"""

    return add_subcomment_for_specific_comment(request, entry_id, comment_id, comment_answer_id)


@login_required
def delete_subcomment(request, entry_id, comment_id, answer_id):
    """ Delete subcomment and its subcomments."""

    return delete_subcomment_and_its_subcomments(request, entry_id, comment_id, answer_id)


@login_required
def delete_all_comments_from_mongodb(request):
    """ Delete all comments from mongodb if 
    user is superuser and redirect on index page"""

    if request.user.is_superuser:
        return delete_comments_from_mongodb()
    else:
        return HttpResponseNotFound("Вы не можете удалять дб")