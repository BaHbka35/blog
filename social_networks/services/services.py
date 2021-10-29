from social_networks.models import Topic
from django.shortcuts import render

def render_page_with_topics_list(request):
    """ Renders page with all topics"""
    
    topics = Topic.objects.all()

    return render(request, 'social_networks/topics_list.html', {'topics': topics})


def render_page_with_entries_for_current_topic(request, topic_id):

    topic = Topic.objects.get(id=topic_id)
    entries = topic.entry_set.all()

    content = {'topic': topic, 'entries': entries}
    return render(request, 'social_networks/entries.html', content)