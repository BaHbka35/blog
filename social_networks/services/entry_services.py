from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound

from social_networks.models import Topic, Entry, Like, DisLike
from social_networks.forms import CreateEntryForm

from comments.forms import CommentForm, AnswerOnCommentForm
from comments.services.mongodb_services import get_comments, \
    get_comments_collection

from .like_dislike_services import get_amount_likes_and_dislikes


def edit_entry_and_save(request, entry_id):
    """
    Edits entry, process data, save edited entry.
    """

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    current_user_id = request.user.id
    
    if entry.author.id == current_user_id:
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
    """
    Renders page with specific entry that has comments, likes, dislikes
    """

    content_for_entry_page = _get_content_for_entry_page(request, entry_id)    

    return render(request, 'social_networks/entry_page.html', content_for_entry_page)


def _get_content_for_entry_page(request, entry_id):
    """
    Return content for entry page.
    """

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    author = entry.author
    amount_likes_and_dislikes = get_amount_likes_and_dislikes(entry_id)
    comments_list = get_comments(entry_id)

    answer_comment_form = AnswerOnCommentForm()
    comment_form = CommentForm()


    author = entry.author.id
    current_user = request.user.id
    
    # Needs for display button delete entry and edit entry for creator of entry
    is_author = False
    if author == current_user:
        is_author = True

    content_for_entry_page = {
        'topic_id': topic.id,
        'entry': entry,
        'amount_likes_and_dislikes': amount_likes_and_dislikes,
        'comments': comments_list,
        'comment_form': comment_form,
        'answer_comment_form':answer_comment_form,
        'is_author': is_author,
    }

    return content_for_entry_page


def create_entry_and_save(request, topic_id):
    """
    Creates entry, process data, save new entry.
    """
    
    topic = Topic.objects.get(id=topic_id)

    if request.method == "GET":
        form = CreateEntryForm()

    else:
        form = CreateEntryForm(request.POST)
        if form.is_valid():
            
            current_user = request.user

            data = form.save(commit=False)
            data.topic_id = topic.id
            data.author = current_user
            data.save()
            
            return redirect('social_networks:entries_list', topic.id)

    content = {'topic': topic, 'form': form}
    return render(request, 'social_networks/create_entry.html', content)


def delete_entry_and_its_comments(request, entry_id):
    """
    Deletes entry and its all comments from mongodb.
    """

    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    current_user_id = request.user.id

    if entry.author.id == current_user_id:
        comments_collection = get_comments_collection()
        comments_collection.remove({'entry_id': entry_id})
        entry.delete()

        return redirect('social_networks:entries_list', topic_id=topic.id)

    else:
        return HttpResponseNotFound("Вы не можете удалить эту запись")