from social_networks.models import Entry
from social_networks.forms import CreateEntryForm
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound


def edit_entry_service(request, entry_id):
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