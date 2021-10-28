from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):

    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Entry(models.Model):

    class Meta:
        verbose_name_plural = "Entries"


    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        if len(self.title) > 20:
            return f"{self.title[:20]} ..."
        else:
            return self.title


class Like(models.Model):

  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"user:{self.user_id} entry:{self.entry_id}"


class DisLike(models.Model):

  entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  def __str__(self):
    return f"user:{self.user_id} entry:{self.entry_id}"