from social_networks.models import Entry, Like, DisLike
from social_networks.forms import CommentForm, AnswerOnCommentForm
from .services_mongodb import get_comments 

def get_content_for_entry_page(request, topic_id, entry_id):

    entry = Entry.objects.get(id=entry_id)
    author = entry.author
    topic = entry.topic

    author = entry.author
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

    return content