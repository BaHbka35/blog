from django.shortcuts import render, redirect
from .models import Topic, Entry, Like, DisLike
from .forms import CreateEntryForm, CommentForm, AnswerOnCommentForm

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import pymongo


from bson.objectid import ObjectId

from datetime import datetime

from django.http import Http404, HttpResponseNotFound, JsonResponse

from django.views.generic import TemplateView, ListView

import json
from bson import json_util


from .services.services_mongodb import get_comments_collection, get_comments
from .services.services_comments import create_comment_service,  add_answer_on_comment, delete_comment_answer_service, delete_comment_service

from .services.services_like_dislike import add_like_service, add_dislike_service
from .services.services_entry import edit_entry_service, get_content_for_entry_page, create_entry_service, delete_entry_service


class IndexView(ListView):
    model = Entry
    template_name = "social_networks/index.html"
    context_object_name = "entries"

    def get_context_data(self, **kwargs):
        entries = Entry.objects.order_by('-id')
        return {"entries": entries}



@method_decorator(login_required, name="dispatch")
class TopicsListView(ListView):
    
    model = Topic
    template_name = 'social_networks/topics_list.html'
    context_object_name = "topics"


@login_required
def entries(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.all()

    content = {'topic': topic, 'entries': entries}
    return render(request, 'social_networks/entries.html', content)


@login_required
def entry_page(request, topic_id, entry_id):

    content = get_content_for_entry_page(request, topic_id, entry_id)
    return render(request, 'social_networks/entry_page.html', content)


@login_required
def create_comment(request, topic_id, entry_id):

    return create_comment_service(request, entry_id)


@login_required
def create_entry(request, topic_id):
    
    return create_entry_service(request, topic_id)


@login_required
def edit_entry(request, entry_id):
    
    return edit_entry_service(request, entry_id)


@login_required
def delete_entry(request, entry_id):

    return delete_entry_service(request, entry_id)


@login_required
def delete_comment(request, entry_id, comment_id):
   
    return delete_comment_service(request, entry_id, comment_id)


@login_required
def answer_on_comment(request, entry_id, comment_id, comment_answer_id):
    
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    add_answer_on_comment(request, comment_id, comment_answer_id)   
  
    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


@login_required
def delete_comment_answer(request, entry_id, comment_id, answer_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    delete_comment_answer_service(request, comment_id, answer_id)

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


@csrf_exempt
@login_required
def add_like(request, entry_id):
  if request.method == "POST":

    add_like_service(request, entry_id)
    
    amount_likes = Like.objects.filter(entry=entry_id).count()
    amount_dislikes = DisLike.objects.filter(entry=entry_id).count()

    content = {
      'amount_likes': amount_likes,
      'amount_dislikes': amount_dislikes,
    }

    return JsonResponse(content)


@csrf_exempt
@login_required
def add_dislike(request, entry_id):
    add_dislike_service(request, entry_id)

    amount_likes = Like.objects.filter(entry=entry_id).count()
    amount_dislikes = DisLike.objects.filter(entry=entry_id).count()

    content = {
    'amount_likes': amount_likes,
    'amount_dislikes': amount_dislikes,
    }

    return JsonResponse(content)



@login_required
def clear_mongodb(request):
    if request.user.is_superuser:
        collection = get_comments_collection()
        collection.remove()
        return redirect('social_networks:index')
    else:
        return HttpResponseNotFound("Вы не можете удалять дб")