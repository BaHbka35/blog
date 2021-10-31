from social_networks.models import Topic, Entry
from django.shortcuts import render, redirect

def render_page_with_topics_list(request):
    """ Renders page with all topics"""
    
    topics = Topic.objects.all()

    return render(request, 'social_networks/topics_list.html', {'topics': topics})


def render_page_with_entries_for_current_topic(request, topic_id):
    """
    Renders page with all entries for current topic.
    """

    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.all()

    content = {'topic': topic, 'entries': entries}
    return render(request, 'social_networks/entries.html', content)


def redirect_to_entry_page(entry_id):
    """
    Does redirect to specific entry page.
    """

    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic_id

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)
