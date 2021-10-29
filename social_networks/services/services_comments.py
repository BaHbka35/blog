from .services_mongodb import get_comments_collection
from datetime import datetime
from bson.objectid import ObjectId
from social_networks.forms import CommentForm, AnswerOnCommentForm
from django.http import Http404

import json
from bson import json_util



def parse_json(data):
    return json.loads(json_util.dumps(data))

def create_comment_service(request, entry_id):

    if request.method == "POST":
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comments_collection = get_comments_collection()

            comment_text = comment_form.cleaned_data['comment']
            comment_author = request.user.username
            datetime_now = datetime.now()

            # Comment format for mongodb
            comment_for_db = {
                "entry_id": entry_id,
                "comment_author": comment_author,
                "comment_text": comment_text,
                "comment_time": datetime_now,
            }
            # Writing comment to mongodb
            comments_collection.insert_one(comment_for_db).inserted_id

            if request.is_ajax():
                correct_id = parse_json(comment_for_db["_id"])
                comment_for_db["_id"] = correct_id
                return comment_for_db
    
    return False


def finds_specific_comment_and_add_answer(answers, answer_id, comment_text, comment_author):

    for answer in answers:
        if answer["id"] == ObjectId(answer_id):
            datetime_now = datetime.now()

            # if answer has answers
            try:
                answers_low_lvl = answer["answers"]
                answers_low_lvl += [{
                    "id": ObjectId(),
                    "comment_author": comment_author,
                    "comment_text": comment_text,
                    'datetime_now': datetime_now,
                }]
                break
            # if answer doesn't have answers. Create answers list with one answer
            except KeyError:
                answer["answers"] = [{
                        "id": ObjectId(),
                        "comment_author": comment_author,
                        "comment_text": comment_text,
                        'datetime_now': datetime_now,
                    }]
                break
        else:
            try:
                answers_low_lvl = answer["answers"]
                add_answer_on_comment(answers_low_lvl, answer_id, comment_text, comment_author)
            except KeyError:
                pass
    return answers



def add_answer_on_comment(request, comment_id, comment_answer_id):

    # Form with answer
    form = AnswerOnCommentForm(request.POST)
    if form.is_valid():

        comment_text = form.cleaned_data['comment']
        comment_author = request.user.username
        comments_collection = get_comments_collection()

        entire_document = comments_collection.find_one({"_id": ObjectId(comment_id)})
        datetime_now = datetime.now()

        # if main comment has answers
        try:
            answers = entire_document['answers']
            # If answer for main comment
            if ObjectId(comment_id) == ObjectId(comment_answer_id):
                answers_edited = answers + [{
                    "id": ObjectId(),
                    "comment_author": comment_author,
                    "comment_text": comment_text,
                    'datetime_now': datetime_now,
                }]
            # If answer for not main comment
            else:
                answers_edited = finds_specific_comment_and_add_answer(
                    answers,
                    comment_answer_id,
                    comment_text,
                    comment_author)
            
            # Update document in mongodb
            comments_collection.update(
                {"_id": ObjectId(comment_id)},
                {"$set": {"answers": answers_edited}}
                )

        # If main comment doesn't have answers
        except KeyError:
            # If answer for main comment. If not pass
            if ObjectId(comment_id) == ObjectId(comment_answer_id):
                comments_collection.update(
                    {"_id": ObjectId(comment_id)},
                    {"$set": {"answers": [{
                        "id": ObjectId(),
                        "comment_author": comment_author,
                        "comment_text": comment_text,
                        'datetime_now': datetime_now,
                    }]}}
                )



def find_and_delete_comment_answer(answers, answer_id, username):
    index = 0
    for answer in answers:
        if answer["id"] == ObjectId(answer_id):
            if answer["comment_author"] == username:
                answers.pop(index)
                break

            else:
                raise Http404

        else:
            try:
                answers_low_lvl = answer["answers"]
                find_and_delete_comment_answer(answers_low_lvl, answer_id, username)
            except KeyError:
                pass
        index += 1

    return answers



def delete_comment_answer_service(request, comment_id, answer_id):

    comments_collection = get_comments_collection()
    entire_document = comments_collection.find_one({"_id": ObjectId(comment_id)}) # recive entire document
    answers = entire_document["answers"]

    username = request.user.username

    answers_edited = find_and_delete_comment_answer(answers, answer_id, username)

    comments_collection.update(
        {"_id": ObjectId(comment_id)},
        {"$set": {"answers": answers_edited}}
        )