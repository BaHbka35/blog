from django.contrib import admin
from .models import Topic, Entry, Like, DisLike

admin.site.register(Topic)
admin.site.register(Entry)
admin.site.register(Like)
admin.site.register(DisLike)