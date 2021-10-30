from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from social_networks.models import Topic, Entry, Like, DisLike
from social_networks.forms import CreateEntryForm, CommentForm, AnswerOnCommentForm

from .mongodb_services import get_comments, get_comments_collection

def edit_entry_and_save(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    user_id = request.user.id
    
    if entry.author.id == user_id:
        if request.method == 'GET':
            form = CreateEntryForm(instance=entry)

        else:
            form = CreateEntryForm(instance=entry, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('social_networks:entry_page', topic.id, entry_id)

    else:
        return HttpResponseNotFound("Вы не можете удалить эту запись")

    content = {'form': form, 'entry_id': entry_id}
    return render(request, 'social_networks/edit_entry.html', content)


def render_page_with_specific_entry(request, topic_id, entry_id):

    entry = Entry.objects.get(id=entry_id)
    author = entry.author
    topic = entry.topic

    author = entry.author.id
    user = request.user.id
    amount_likes = Like.objects.filter(entry=entry_id).count()
    amount_dislikes = DisLike.objects.filter(entry=entry_id).count()
    is_author = False 
    if author == user:
        is_author = True

    
    comment_form = CommentForm()
    comments_list = get_comments(entry_id)

    answer_comment_form = AnswerOnCommentForm()
    content = {
        'topic_id': topic.id,
        'amount_likes': amount_likes,
        'amount_dislikes': amount_dislikes,
        'entry': entry,
        'is_author': is_author,
        'comment_form': comment_form,
        'comments': comments_list,
        'answer_comment_form':answer_comment_form,
    }

    return render(request, 'social_networks/entry_page.html', content)


def create_entry_and_save(request, topic_id):
    
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


def delete_entry_and_its_comments(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    user_id = request.user.id

    if entry.author.id == user_id:
        comments_collection = get_comments_collection()
        # Delete comments that belong current entry
        comments_collection.remove({'entry_id': entry_id})
        entry.delete()

        return redirect('social_networks:entries_list', topic_id=topic.id)

    else:
        return HttpResponseNotFound("Вы не можете удалить эту запись")