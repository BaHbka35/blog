from social_networks.models import Entry, Like, DisLike


def add_like_for_specific_entry(request, entry_id):
    entry = Entry.objects.get(id=entry_id)
    user = request.user
    user_id = user.id

    is_like = []
    try:
        is_like = Like.objects.get(entry=entry_id, user=user_id)
    
    except:
        if is_like:
            pass
        else:
            is_dislike = []
            try:
                is_dislike = DisLike.objects.get(entry=entry_id, user=user_id)
            except:
                pass

            if is_dislike:
                is_dislike.delete()

            like = Like.objects.create(entry=entry, user=user)
            like.save()


def add_dislike_for_specific_entry(request, entry_id):

    entry = Entry.objects.get(id=entry_id)
    user = request.user
    user_id = user.id

    is_dislike = []
    try:
        is_dislike = DisLike.objects.get(entry=entry_id, user=user_id)

    except:
        if is_dislike:
            pass
        else:
            is_like = []
            try:
                is_like = Like.objects.get(entry=entry_id, user=user_id)
            except:
                pass

            if is_like:
                is_like.delete()

            dislike = DisLike.objects.create(entry=entry, user=user)
            dislike.save()


def get_amount_likes_and_dislikes(entry_id):

    amount_likes = Like.objects.filter(entry=entry_id).count()
    amount_dislikes = DisLike.objects.filter(entry=entry_id).count()

    amount_likes_and_dislikes = {
    'amount_likes': amount_likes,
    'amount_dislikes': amount_dislikes,
    }

    return amount_likes_and_dislikes