from django.shortcuts import redirect

from django.conf import settings
import pymongo


# Function for get collection with contains comments
def get_comments_collection():
    client = pymongo.MongoClient(settings.MONGODB_LINK_API)
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


def delete_comments_from_mongodb():

    collection = get_comments_collection()
    collection.remove()
    return redirect('social_networks:index')