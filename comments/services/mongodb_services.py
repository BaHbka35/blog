import pymongo

from django.shortcuts import redirect
from django.conf import settings


def get_comments_collection():
    """
    Gets collection fo comments from mongodb
    """

    client = pymongo.MongoClient(settings.MONGODB_LINK_API)
    db = client.App
    collection = db.comments
    
    return collection



def get_comments(entry_id):
    """
    Gets all comments for specific entry and change 
    field _id on id for more easy access to field id.
    """

    comments_collection = get_comments_collection()
    comments_for_entry = comments_collection.find({"entry_id": entry_id,})
    
    comments_list_for_entry = []
    for comment in comments_for_entry:
        comment["id"] = comment["_id"]
        del comment["_id"]
        comments_list_for_entry.append(comment)

    return comments_list_for_entry


def delete_comments_from_mongodb():
    """
    Deletes all comments from mongodb.
    """

    collection = get_comments_collection()
    collection.remove()
    return redirect('social_networks:index')