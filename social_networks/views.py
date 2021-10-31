from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .services.services import render_page_with_topics_list, \
    render_page_with_entries_for_current_topic

from .services.entry_services import render_page_with_specific_entry, \
    edit_entry_and_save, create_entry_and_save, delete_entry_and_its_comments

from .services.like_dislike_services import add_like_for_specific_entry, \
    add_dislike_for_specific_entry, get_amount_likes_and_dislikes


def index(request):
    """ Renders index page."""

    return render(request, 'social_networks/index.html')


@login_required
def topics_list(request):
    """ Renders page with list of all topics."""
    
    return render_page_with_topics_list(request)


@login_required
def entries_list(request, topic_id):
    """ Renders page with all entries witch belongs to specific topic."""

    return render_page_with_entries_for_current_topic(request, topic_id)


@login_required
def entry_page(request, topic_id, entry_id):
    """ Render page with specific entry."""

    return render_page_with_specific_entry(request, topic_id, entry_id)


@login_required
def create_entry(request, topic_id):
    """ View for render page with clear form for create entry
    then process data from form and save if them is valid."""
    
    return create_entry_and_save(request, topic_id)


@login_required
def edit_entry(request, entry_id):
    """ View for render page with existing data then process
    data and save changes if they is valid."""
    
    return edit_entry_and_save(request, entry_id)


@login_required
def delete_entry(request, entry_id):
    """ Delete entry and all comments witch belongs to it"""

    return delete_entry_and_its_comments(request, entry_id)


@csrf_exempt
@login_required
def add_like(request, entry_id):
    """ Add like for specific entry and send amount likes 
    and dislikes on frontend for dynamic changing."""

    add_like_for_specific_entry(request, entry_id)
    amount_likes_and_dislikes = get_amount_likes_and_dislikes(entry_id)

    return JsonResponse(amount_likes_and_dislikes)


@csrf_exempt
@login_required
def add_dislike(request, entry_id):
    """ Add dislike for specific entry and send amount likes 
    and dislikes on frontend for dynamic changeing."""

    add_dislike_for_specific_entry(request, entry_id)
    amount_likes_and_dislikes = get_amount_likes_and_dislikes(entry_id)

    return JsonResponse(amount_likes_and_dislikes)


