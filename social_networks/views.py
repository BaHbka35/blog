from django.shortcuts import render, redirect
from .models import Topic, Entry, Like
from .forms import CreateEntryForm, CommentForm, AnswerOnCommentForm

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import pymongo
from .mongodb_data import MONGODB_LINK

from bson.objectid import ObjectId

from datetime import datetime

from django.http import Http404, HttpResponseNotFound, JsonResponse

from django.views.generic import TemplateView, ListView

import json
from bson import json_util


# Function for get collection with contains comments
def get_comments_collection():
    client = pymongo.MongoClient(MONGODB_LINK)
    db = client.App
    collection = db.comments
    
    # Return collection from mongodb that contain all documents with comments.
    return collection


# Function for get comments from mongodb
def get_comments(entry_id):
    # Connection to mongodb
    comments_collection = get_comments_collection()

    # Recive main comments
    comments_from_db = comments_collection.find({"entry_id": entry_id,})
    
    # Will contein structure with main comments with their id and subcomments
    comments_list = []
    for comment in comments_from_db:
        comment["id"] = comment["_id"]
        del comment["_id"]
        comments_list.append(comment)

    return comments_list


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

    entry = Entry.objects.get(id=entry_id)
    author = entry.author
    topic = entry.topic

    author = entry.author
    user = request.user.id
    likes = entry.likes
    is_author = False 
    if author == user:
        is_author = True

    
    comment_form = CommentForm()
    comments_list = get_comments(entry_id)

    answer_comment_form = AnswerOnCommentForm()
    content = {
        'topic_id': topic.id,
        'likes': likes,
        'entry': entry,
        'is_author': is_author,
        'comment_form': comment_form,
        'comments': comments_list,
        'answer_comment_form':answer_comment_form,
    }

    return render(request, 'social_networks/entry_page.html', content)


def parse_json(data):
    return json.loads(json_util.dumps(data))


@login_required
def create_comment(request, topic_id, entry_id):
    print("I'm here")

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comments_collection = get_comments_collection()

            comment_text = comment_form.cleaned_data['comment']
            comment_author = request.user.username
            datetime_now = datetime.now()

            # Comment format for mongodb
            comment_for_db = {
                "entry_id": entry_id,
                "comment_author": comment_author,
                "comment_text": comment_text,
                "comment_time": datetime_now,
            }
            # Writing comment to mongodb
            comments_collection.insert_one(comment_for_db).inserted_id

            if request.is_ajax():
                correct_id = parse_json(comment_for_db["_id"])
                comment_for_db["_id"] = correct_id
                return JsonResponse({"comment": comment_for_db})

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


@login_required
def create_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    if request.method == "GET":
        form = CreateEntryForm()

    else:
        # Sent data; Processing data. Form with data of record
        form = CreateEntryForm(request.POST)
        if form.is_valid():
            
            user = request.user

            data = form.save(commit=False)
            data.topic_id = topic.id
            data.author = user
            data.likes = 0
            data.save()
            
            return redirect('social_networks:entries', topic.id)

    content = {'topic': topic, 'form': form}
    return render(request, 'social_networks/create_entry.html', content)


@login_required
def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    user_id = request.user.id
    
    if entry.author.id == user_id:
        if request.method == 'GET':
            # Create form with existing entry
            form = CreateEntryForm(instance=entry)

        else:
            # Form with edited data
            form = CreateEntryForm(instance=entry, data=request.POST)
            if form.is_valid:
                form.save()
                return redirect('social_networks:entry_page', topic.id, entry_id)
    else:
        print(entry.author, user_id)
        return HttpResponseNotFound("Вы не можете удалить эту запись")

    content = {'form': form, 'entry_id': entry_id}
    return render(request, 'social_networks/edit_entry.html', content)


@login_required
def delete_entry(request, entry_id):

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    user_id = request.user.id

    if entry.author.id == user_id:
        comments_collection = get_comments_collection()
        # Delete comments that belong current entry
        comments_collection.remove({'entry_id': entry_id})
        entry.delete()

        return redirect('social_networks:entries', topic_id=topic.id)

    else:
        return HttpResponseNotFound("Вы не можете удалить эту запись")


@login_required
def delete_comment(request, entry_id, comment_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    comments_collection = get_comments_collection()
    username = request.user.username
    comment = comments_collection.find_one({"_id": ObjectId(comment_id), "comment_author": username})
    if comment:
        # Delete comment
        comments_collection.remove({"_id": ObjectId(comment_id)})
        return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)

    else:
        return HttpResponseNotFound("Вы не можете удалить комментарий")


def add_answer_on_comment(answers, answer_id, comment_text, comment_author):

    for answer in answers:
        if answer["id"] == ObjectId(answer_id):
            datetime_now = datetime.now()

            # if answer has answers
            try:
                answers_low_lvl = answer["answers"]
                answers_low_lvl += [{
                    "id": ObjectId(),
                    "comment_author": comment_author,
                    "comment_text": comment_text,
                    'datetime_now': datetime_now,
                }]
                break
            # if answer doesn't have answers. Create answers list with one answer
            except KeyError:
                answer["answers"] = [{
                        "id": ObjectId(),
                        "comment_author": comment_author,
                        "comment_text": comment_text,
                        'datetime_now': datetime_now,
                    }]
                break
        else:
            try:
                answers_low_lvl = answer["answers"]
                add_answer_on_comment(answers_low_lvl, answer_id, comment_text, comment_author)
            except KeyError:
                pass
    return answers


@login_required
def answer_on_comment(request, entry_id, comment_id, comment_answer_id):

    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    # Form with answer
    form = AnswerOnCommentForm(request.POST)
    if form.is_valid():

        comment_text = form.cleaned_data['comment']
        comment_author = request.user.username
        comments_collection = get_comments_collection()

        entire_document = comments_collection.find_one({"_id": ObjectId(comment_id)})
        datetime_now = datetime.now()

        # if main comment has answers
        try:
            answers = entire_document['answers']
            # If answer for main comment
            if ObjectId(comment_id) == ObjectId(comment_answer_id):
                answers_edited = answers + [{
                    "id": ObjectId(),
                    "comment_author": comment_author,
                    "comment_text": comment_text,
                    'datetime_now': datetime_now,
                }]
            # If answer for not main comment
            else:
                answers_edited = add_answer_on_comment(answers, comment_answer_id, comment_text, comment_author)
            
            # Update document in mongodb
            comments_collection.update(
                {"_id": ObjectId(comment_id)},
                {"$set": {"answers": answers_edited}}
                )

        # If main comment doesn't have answers
        except KeyError:
            # If answer for main comment. If not pass
            if ObjectId(comment_id) == ObjectId(comment_answer_id):
                comments_collection.update(
                    {"_id": ObjectId(comment_id)},
                    {"$set": {"answers": [{
                        "id": ObjectId(),
                        "comment_author": comment_author,
                        "comment_text": comment_text,
                        'datetime_now': datetime_now,
                    }]}}
                )   
  
    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)



def find_and_delete_answer(answers, answer_id, username):
    index = 0
    for answer in answers:
        if answer["id"] == ObjectId(answer_id):
            if answer["comment_author"] == username:
                answers.pop(index)
                break

            else:
                raise Http404

        else:
            try:
                answers_low_lvl = answer["answers"]
                find_and_delete_answer(answers_low_lvl, answer_id, username)
            except KeyError:
                pass
        index += 1

    return answers


@login_required
def delete_comment_answer(request, entry_id, comment_id, answer_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    comments_collection = get_comments_collection()
    entire_document = comments_collection.find_one({"_id": ObjectId(comment_id)}) # recive entire document
    answers = entire_document["answers"]

    username = request.user.username

    answers_edited = find_and_delete_answer(answers, answer_id, username)

    comments_collection.update(
        {"_id": ObjectId(comment_id)},
        {"$set": {"answers": answers_edited}}
        )

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


@csrf_exempt
def add_like(request, entry_id):
  if request.method == "POST":
    entry = Entry.objects.get(id=entry_id)
    user = request.user
    user_id = user.id
    amount_likes = entry.likes
    
    is_like = []
    try:
      print("Я тут")
      is_like = Like.objects.get(entry_id=entry_id, user_id=user_id)
      
    except:
      if is_like:
        pass
      else:
        
        amount_likes += 1
        entry.likes = amount_likes
        print(amount_likes)
        
        entry.save()
        like = Like.objects.create(entry_id=entry, user_id=user)
        like.save()

    content = {
      'amount_likes': amount_likes,
    }

  return JsonResponse(content)

@login_required
def clear_mongodb(request):
    print(request.user.is_superuser)
    if request.user.is_superuser:
        # Function delete all documents in monogdb
        collection = get_comments_collection()
        collection.remove()
        return redirect('social_networks:index')
    else:
        return HttpResponseNotFound("Вы не можете удалять дб")