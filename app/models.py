from django.db import models
from ckeditor.fields import RichTextField
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Model custom more information for user
    """
    achievement = models.IntegerField(default=0)
    point = models.FloatField(default=0)
    avatar_link = models.CharField(max_length=1024, default="")
    phone = models.CharField(max_length=10, default="")
    count_violated = models.IntegerField(default=0)
    time_banned = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username


class ReportUser(models.Model):
    """
    Model representing a report user
    """
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reporter')
    reported_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reported_user')
    reason = models.CharField(max_length=1024)
    time = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, choices=((True, 'Resolved'), (False, 'Not resolved')))

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.reporter.username + " reported " + self.reported_user.username + " for " + self.reason


class Follow(models.Model):
    """
    Model representing a follow
    """
    follower = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='follower')
    followed = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='followed')
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.follower.username + " followed " + self.followed.username


class Post(models.Model):
    """
    Model representing a post
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    categories = models.ManyToManyField('Category')
    hashtags = models.ManyToManyField('HashTag', blank=True, null=True)
    content = RichTextField()
    mode = models.IntegerField(default=0, choices=((0, _('Public')), (1, _('Private'))))
    status = models.IntegerField(default=0, choices=((0, _('Draft')), (1, _('Normal')), (2, _('Deleted')), (3, _('Banned'))))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    view_count = models.FloatField(default=0)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " posted " + self.title


class Category(models.Model):
    """
    Model representing a category
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.name


class HashTag(models.Model):
    """
    Model representing a hashtag
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.name


class PostPaid(models.Model):
    """
    Model representing a post paid
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " paid for " + self.post.title


class PostReaction(models.Model):
    """
    Model representing a post reaction
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    feedback_value = models.IntegerField(choices=((1, 'Upvote'), (-1, 'Downvote')))
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " reacted " + self.post.title


class ReportPost(models.Model):
    """
    Model representing a report post
    """
    reporter = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reporter_post')
    reported_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reported_post')
    reason = models.CharField(max_length=1024)
    time = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False, choices=((True, _('Resolved')), (False, _('Not resolved'))))

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.reporter.username + " reported " + self.reported_post.title + " for " + self.reason


class Comment(models.Model):
    """
    Model representing a comment
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None)
    content = models.CharField(max_length=10000)
    is_edited = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " commented " + self.post.title


class Bookmark(models.Model):
    """
    Model representing a bookmark
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " bookmarked " + self.post.title


class Notification(models.Model):
    """
    Model representing a notification
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.CharField(max_length=1000)
    is_read = models.BooleanField(default=False)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String for representing the Model object.
        """
        return self.user.username + " got notification " + self.content
