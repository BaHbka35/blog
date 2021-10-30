from social_networks.models import Entry
from .mongodb_services import get_comments_collection
from datetime import datetime
from bson.objectid import ObjectId
from social_networks.forms import CommentForm, AnswerOnCommentForm
from django.http import Http404
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseNotFound



def create_comment_for_specific_entry(request, entry_id):
    """
    Create comment for specific entry, save it to mongodb 
    and return Json for dynamic changing on frontend.
    """
    
    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic_id

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            return _add_comment_to_mongodb_and_return_json_for_frontend(request, entry_id, comment_form)        

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


def _add_comment_to_mongodb_and_return_json_for_frontend(request, entry_id, comment_form):
    """
    Add comment to monogdb and return Json for dynamic changing on frontend.
    """

    comment_for_mongodb = _get_comment_format_for_mongodb(request, entry_id, comment_form)
        
    comments_collection = get_comments_collection()

    # Writing comment to mongodb; after that, comment_for_mongodb has field _id
    comments_collection.insert_one(comment_for_mongodb)

    if request.is_ajax():
        json_for_frontend = _send_json_response_on_create_comment_for_frontend(comment_for_mongodb)
        return json_for_frontend


def _get_comment_format_for_mongodb(request, entry_id, comment_form):
    """
    Create comment structure for adding to mongodb. 
    """

    comment_text = comment_form.cleaned_data['comment']
    comment_author = request.user.username
    datetime_now = datetime.now()

    # Comment format for mongodb
    comment_for_mongodb = {
        "entry_id": entry_id,
        "comment_author": comment_author,
        "comment_text": comment_text,
        "comment_time": datetime_now,
    }

    return comment_for_mongodb


def _send_json_response_on_create_comment_for_frontend(comment_for_mongodb):
    """
    Change field _id at comment_for_db that represent as ObjectId type to string representation;
    Send changed comment to frontend for dynamic representation
    """

    transformed_id = str(comment_for_mongodb["_id"])
    comment_for_mongodb["_id"] = transformed_id
    return JsonResponse({"comment": comment_for_mongodb})



def delete_main_comment_and_its_subcomment(request, entry_id, main_comment_id):
    """ 
    Delete comment that belong to specific entry.
    Delete all subcomments that belong to comment.
    """

    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id
    current_username = request.user.username

    return _delete_comment_if_user_is_author(topic_id, entry_id, main_comment_id, current_username)


def _delete_comment_if_user_is_author(topic_id, entry_id, main_comment_id, current_username):
    """
    If comment belongs to current user delete it.
    esle return message with text about it.
    """

    comments_collection = get_comments_collection()
    comment = comments_collection.find_one({"_id": ObjectId(main_comment_id), "comment_author": current_username})

    if comment:
        # Delete comment
        comments_collection.remove({"_id": ObjectId(main_comment_id)})
        return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)

    else:
        return HttpResponseNotFound("Вы не можете удалить комментарий")



def add_subcomment_for_specific_comment(request, entry_id, main_comment_id, comment_id_for_subcomment):
    """
    Add subcomment for specific comment. Can add subcomment for other subcomment.
    """

    form = AnswerOnCommentForm(request.POST)
    if form.is_valid():

        comment_text = form.cleaned_data['comment']
        comment_author = request.user.username
        datetime_now = datetime.now()

        main_comment_document = get_comments_collection().find_one({"_id": ObjectId(main_comment_id)})

        if 'subcomments' in main_comment_document:
            subcomments = main_comment_document['subcomments']

            _add_subcomment_for_main_comment_or_other_subcomment(subcomments, main_comment_id, comment_id_for_subcomment,
                                                        comment_author, comment_text, datetime_now)
            
        else:
            if _is_subcomment_for_main_comment(main_comment_id, comment_id_for_subcomment):

                _add_first_subcomment_for_main_comment(main_comment_id, comment_author, comment_text, datetime_now)
     

    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id

    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


def _is_subcomment_for_main_comment(main_comment_id, comment_id_for_subcomment):
    """
    Is checking is subcomment creating for main comment or not.
    """

    return ObjectId(main_comment_id) == ObjectId(comment_id_for_subcomment)


def _add_first_subcomment_for_main_comment(comment_id, comment_author, comment_text, datetime_now):
    """
    Add first subcomment for main comment.
    """
    first_subcomment = {
        "id": ObjectId(),
        "comment_author": comment_author,
        "comment_text": comment_text,
        'datetime_now': datetime_now,
        }

    get_comments_collection().update({"_id": ObjectId(comment_id)}, {"$set": {"subcomments": [first_subcomment]}})


def _add_subcomment_for_main_comment_or_other_subcomment(subcomments, main_comment_id, comment_id_for_subcomment,
    comment_author, comment_text, datetime_now):
    """
    Add subcomment to alrady existin subcomments for main comment or
    Add subcomment for other subcomment.
    """

    if _is_subcomment_for_main_comment(main_comment_id, comment_id_for_subcomment):

        updated_subcomments = subcomments + [{
            "id": ObjectId(),
            "comment_author": comment_author,
            "comment_text": comment_text,
            'datetime_now': datetime_now,
        }]

    else:
        updated_subcomments = _finds_needed_comment_and_add_subcomment_for_it(
            subcomments, comment_id_for_subcomment,
            comment_text, comment_author, datetime_now)
    
    get_comments_collection().update(
        {"_id": ObjectId(main_comment_id)},
        {"$set": {"subcomments": updated_subcomments}}
        )




def _finds_needed_comment_and_add_subcomment_for_it(subcomments, comment_id_for_subcomment,
    comment_text, comment_author, datetime_now):
    """
    Recursion for finding needed subcomment and adding subcomment for it.
    Takes every subcomment in subcomments list
    Is checking is subcomment id from list of subcomments equal id of needed subcomment.
    If true, add subcomment to list of existing comments or create list with only one subcommet
    """

    for subcomment in subcomments:
        if subcomment["id"] == ObjectId(comment_id_for_subcomment):

            if 'subcomments' in subcomment:
                
                existing_subcomments = subcomment["subcomments"]
                existing_subcomments += [{
                    "id": ObjectId(),
                    "comment_author": comment_author,
                    "comment_text": comment_text,
                    'datetime_now': datetime_now,
                }]
                break

            else:
                subcomment["subcomments"] = [{
                        "id": ObjectId(),
                        "comment_author": comment_author,
                        "comment_text": comment_text,
                        'datetime_now': datetime_now,
                    }]
                break
        else:
            if 'subcomments' in subcomments:
                existing_subcomments = subcomment["subcomments"]
                _finds_needed_comment_and_add_subcomment_for_it(existing_subcomments, comment_id_for_subcomment,
                    comment_text, comment_author, datetime_now)

    return subcomments


def delete_subcomment_and_its_subcomments(request, entry_id, main_comment_id, subcomment_id):
    """
    Deletes specific subcomments and its subcomments if they are existing
    """

    comments_collection = get_comments_collection()
    main_comment_document = comments_collection.find_one({"_id": ObjectId(main_comment_id)})

    username = request.user.username

    subcomments = main_comment_document["subcomments"]
    updated_subcomments = _find_and_delete_subcomment(subcomments, subcomment_id, username)

    comments_collection.update(
        {"_id": ObjectId(main_comment_id)},
        {"$set": {"subcomments": updated_subcomments}}
        )

    entry = Entry.objects.get(id=entry_id)
    topic_id = entry.topic.id
    return redirect('social_networks:entry_page', topic_id=topic_id, entry_id=entry_id)


def _find_and_delete_subcomment(subcomments, subcomment_id, username):
    """
    Recursion for finding needed subcomment and delete it.
    Takes every subcomment in subcomments list.
    Is checking is subcomment id from list of subcomments equal id of needed subcomment.
    If true, delete subcomment from list of subcomments
    """

    index = 0
    for subcomment in subcomments:
        if subcomment["id"] == ObjectId(subcomment_id):
            if subcomment["comment_author"] == username:
                subcomments.pop(index)
                break

            else:
                raise Http404

        else:
            try:
                existing_subcomments = subcomment["subcomments"]
                _find_and_delete_subcomment(existing_subcomments, subcomment_id, username)
            except KeyError:
                pass
        index += 1

    return subcomments