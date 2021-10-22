from django.shortcuts import render, redirect
from .models import Topic, Entry
from .forms import CreateEntryForm, CommentForm, AnswerOnCommentForm

import pymongo
from .mongodb_data import MONGODB_LINK

from bson.objectid import ObjectId

from datetime import datetime


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
    comments_from_db = comments_collection.find({"comment_lvl": 1 ,"entry_id": entry_id,})
    
    # Will contein structure with main comments with their id and subcomments
    comments_list = []
    for comment in comments_from_db:
        comment["id"] = comment["_id"]
        del comment["_id"]
        comments_list.append(comment)

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
        comment_form = CommentForm()
        # Recive comments and their subcomments
        comments_list = get_comments(entry_id)
      
    else:
      # Form with data that contain a comment.
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
        
            comments_collection = get_comments_collection()

            # Get comment from form
            comment_text = comment_form.cleaned_data['comment']
            # Get current datetime
            datetime_now = datetime.now()

            # Comment format for mongodb
            comment_for_db = {
                "comment_lvl": 1,
                "entry_id": entry_id,
                "comment_author": 'xxx',
                "comment_text": comment_text,
                "comment_time": datetime_now,
            }
            # Writing comment to mongodb
            comments_collection.insert_one(comment_for_db).inserted_id
            
            comments_list = get_comments(entry_id)
            comment_form = CommentForm()

    answer_comment_form = AnswerOnCommentForm()
    content = {
        'topic_id': topic_id,
        'entry': entry,
        'comment_form': comment_form,
        'comments': comments_list,
        'answer_comment_form':answer_comment_form,
    }
    return render(request, 'social_networks/entry_page.html', content)


def create_entry(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    if request.method == "GET":
        form = CreateEntryForm()

    else:
        # Sent data; Processing data. Form with data of record
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
        # Form with edited data
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
    # Delete comments that belong current entry
    comments_collection.remove({'entry_id': entry_id})
    entry.delete()

    return redirect('social_networks:entries', topic_id=topic.id)


def delete_comment(request, entry_id, comment_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    comments_collection = get_comments_collection()
    # Delete comment
    comments_collection.remove({"_id": ObjectId(comment_id)})
    
    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


def answer_on_comment_lvl_1(request, entry_id, comment_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    # Form with answer on main comment.
    form = AnswerOnCommentForm(request.POST)
    if form.is_valid():

        comment_text = form.cleaned_data['comment']
        comments_collection = get_comments_collection()
        comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
        datetime_now = datetime.now()

        # If comment_lvl_1 has key 'answers'
        try:
            answers = comment['answers']
            # Inserts document that should be inserted to existing document
            answers = answers + [{
                "id": ObjectId(),
                "comment_lvl": 2,
                "comment_author": "yyy",
                "comment_text": comment_text,
                'datetime_now': datetime_now,
                }]
            comments_collection.update(
                {"_id": ObjectId(comment_id)},
                {"$set": {"answers": answers}
                })

        # If comment_lvl_1 doesn't have key 'answers'
        except KeyError:
            comments_collection.update(
                {"_id": ObjectId(comment_id)},
                {"$set": {"answers": [{
                    "id": ObjectId(),
                    "comment_lvl": 2,
                    "comment_author": "yyy",
                    "comment_text": comment_text,
                    'datetime_now': datetime_now,
                }]}}
            )

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


def answer_on_comment_lvl_2(request, entry_id, comment_id, comment_answer_id):
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    # Form with answer on main comment.
    form = AnswerOnCommentForm(request.POST)
    if form.is_valid():

        comment_text = form.cleaned_data['comment']
        comments_collection = get_comments_collection()

        entire_document = comments_collection.find_one({"_id": ObjectId(comment_id)})
        answers_high_lvl = entire_document['answers']

        datetime_now = datetime.now()
        
        answers_high_lvl = entire_document['answers']
        for answer in answers_high_lvl:
            if answer["id"] == ObjectId(comment_answer_id):
                # If comment_lvl_x has key 'answers'
                try:
                    answers_lov_lvl = answer["answers"]
                    # Inserts document that should be inserted to existing document
                    answers_lov_lvl = answers_lov_lvl + [{
                        "id": ObjectId(),
                        "comment_lvl": 3,
                        "comment_author": "yyy",
                        "comment_text": comment_text,
                        'datetime_now': datetime_now,
                        }]

                    answer['answers'] = answers_lov_lvl
                    comments_collection.update(
                        {"_id": ObjectId(comment_id)},
                        {"$set": {"answers": answers_high_lvl}
                        })
                    # If comment_lvl_x doesn't have key 'answers'
                except KeyError:
                    answer["answers"] = [{
                            "id": ObjectId(),
                            "comment_lvl": 3,
                            "comment_author": "yyy",
                            "comment_text": comment_text,
                            'datetime_now': datetime_now,
                        }]

                    comments_collection.update(
                        {"_id": ObjectId(comment_id)},
                        {"$set": {"answers": answers_high_lvl}}
                    )
    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)



def find_and_delete_answer(answers, answer_id):
    index = 0
    for answer in answers:
        if answer["id"] == ObjectId(answer_id):
            answers.pop(index)
            break
        else:
            try:
                answers_1 = answer["answers"]
                find_and_delete_answer(answers_1, answer_id)
                break
            except KeyError:
                pass
        index += 1

    return answers


def delete_comment_answer(request, entry_id, comment_id, answer_id):
    # http://127.0.0.1:8000/delete/answer/on/comment/xxx3/xxx6172bc072288b5231cba0fe8/xxx6172bc202288b5231cba0ff4
    
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    comments_collection = get_comments_collection()
    entire_document = comments_collection.find_one({"_id": ObjectId(comment_id)}) # recive entire document

    answers = entire_document["answers"]
    answers_edited = find_and_delete_answer(answers, answer_id)

    comments_collection.update(
        {"_id": ObjectId(comment_id)},
        {"$set": {"answers": answers_edited}}
        )

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)





def clear_mongodb(request):
    # Function delete all documents in monogdb
    collection = get_comments_collection()
    collection.remove()
    return redirect('social_networks:index')