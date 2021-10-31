from social_networks.models import Entry, Like, DisLike


def add_like_for_specific_entry(request, entry_id):
    """
    Adds uniqu like for specific_entry
    """

    entry = Entry.objects.get(id=entry_id)
    current_user = request.user
    current_user_id = current_user.id

    like = _get_like_from_current_user(entry_id, current_user_id)
    if not like:

        dislike = _get_dislike_from_current_user(entry_id, current_user_id)
        if dislike:
            dislike.delete()

        like = Like.objects.create(entry=entry, user=current_user)
        like.save()


def add_dislike_for_specific_entry(request, entry_id):
    """
    Adds uniqu dislike for specific_entry
    """

    entry = Entry.objects.get(id=entry_id)
    current_user = request.user
    current_user_id = current_user.id

    dislike = _get_dislike_from_current_user(entry_id, current_user_id)
    if not dislike:

        like = _get_like_from_current_user(entry_id, current_user_id)
        if like:
            like.delete()

        dislike = DisLike.objects.create(entry=entry, user=current_user)
        dislike.save()


def _get_like_from_current_user(entry_id, current_user_id):
    """
    Returns like from current user if like exists
    """

    try:
        like = Like.objects.get(entry=entry_id, user=current_user_id)
        return like
    except Like.DoesNotExist:
        return False


def _get_dislike_from_current_user(entry_id, current_user_id):
    """
    Returns dislike from current user if dislike exists
    """

    try:
        dislike = DisLike.objects.get(entry=entry_id, user=current_user_id)
        return dislike
    except DisLike.DoesNotExist:
        return False


def get_amount_likes_and_dislikes(entry_id):
    """
    Returns amount likes and dislikes for specific entry.
    """

    amount_likes = Like.objects.filter(entry=entry_id).count()
    amount_dislikes = DisLike.objects.filter(entry=entry_id).count()

    amount_likes_and_dislikes = {
    'amount_likes': amount_likes,
    'amount_dislikes': amount_dislikes,
    }

    return amount_likes_and_dislikes