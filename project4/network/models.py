from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db import models


class User(AbstractUser):
 username = models.CharField(max_length = 50, blank = True, null = True, unique = True)
 email = models.EmailField(_('email address'), unique = True ,null=True)
 phone_no = models.CharField(max_length = 10,null=True)

def __str__(self) -> str:
    return self.username


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='likes')


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    followers = models.ManyToManyField(User, related_name='following')

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

models.signals.post_save.connect(create_user_profile, sender=User)

class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follow', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    
    class Meta:
      unique_together = ('follower', 'followed_user')