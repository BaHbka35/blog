from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import CreateEntryForm, CommentForm

import pymongo
from .mongodb_data import mongodb_link

from bson.objectid import ObjectId


# Function for get collection with contains comments
def get_comments_collection():
    client = pymongo.MongoClient(mongodb_link)
    db = client.App
    collection = db.comments

    return collection


# Function for get comments from mongodb
def get_comments(entry_id):
  # Connection to mongodb
  comments_collection = get_comments_collection()

  comments_from_db = comments_collection.find({"entry_id": entry_id})
  comments_list = []

  for comment in comments_from_db:
    comment_id = comment["_id"]
    text = comment['comment_text']
    comments_list.append({
        "comment_id": comment_id,
        "text": text,
        })

  return comments_list


def index(request):

    return render(request, 'social_networks/index.html')


def topics_list(request):
    topics = Topic.objects.all()

    content = {"topics": topics}
    return render(request, 'social_networks/topics_list.html', content)


def entries(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.all()

    content = {'topic': topic, 'entries': entries}
    return render(request, 'social_networks/entries.html', content)


def entry_page(request, topic_id, entry_id):
  # Page with specific entry that has abilities for endit entry ...
  # Page has comments

    entry = Entry.objects.get(id=entry_id)

    if request.method == "GET":
      # Emtpy form for comment
      form = CommentForm()

      comments_list = get_comments(entry_id)
      

    else:
      # Form with data that contain a comment
      form = CommentForm(request.POST)
      if form.is_valid():
        # Connection to mongodb
        comments_collection = get_comments_collection()

        # Get comment from form
        comment_text = form.cleaned_data['comment']

        # Comment format for mongodb
        comment_for_db = {
          "entry_id": entry_id,
          "comment_text": comment_text,
        }
        # Writing comment to mongodb
        comment_id = comments_collection.insert_one(comment_for_db).inserted_id

        comments_list = get_comments(entry_id)

        form = CommentForm()

    content = {'topic_id': topic_id, "entry": entry, "form": form, 'comments': comments_list,}
    return render(request, 'social_networks/entry_page.html', content)


def create_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    if request.method == "GET":
        # Create empty form
        form = CreateEntryForm()

    else:
        # Sent data; Processing data.
        form = CreateEntryForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.topic_id = topic.id
            data.save()
            
            return redirect('social_networks:entries', topic.id)

    content = {'topic': topic, 'form': form}
    return render(request, 'social_networks/create_entry.html', content)


def edit_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    
    if request.method == 'GET':
        # Create form with existing entry
        form = CreateEntryForm(instance=entry)

    else:
        form = CreateEntryForm(instance=entry, data=request.POST)
        if form.is_valid:
            form.save()
            return redirect('social_networks:entry_page', topic.id, entry_id)

    content = {'form': form, 'entry_id': entry_id}
    return render(request, 'social_networks/edit_entry.html', content)


def delete_entry(request, entry_id):

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic

    comments_collection = get_comments_collection()
    comments_collection.remove({'entry_id': entry_id})

    entry.delete()

    return redirect('social_networks:entries', topic_id=topic.id)


def delete_comment(request, entry_id, comment_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    comments_collection = get_comments_collection()
    comments_collection.remove({"_id": ObjectId(comment_id)})

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)

# def delete_comment(request, entry_id):
#     pass