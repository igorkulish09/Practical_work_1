from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .utils import send_notification_email

class CustomUser(AbstractUser):
    groups = models.ManyToManyField(Group, related_name="custom_users")
    user_permissions = models.ManyToManyField(Permission, related_name="custom_users")

    def __str__(self):
        return self.username


class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()  # Додайте це поле
    short_description = models.TextField(max_length=200, default=timezone.now)
    full_description = models.TextField(default='', blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"Comment by {self.author} on {self.post}"


@receiver(post_save, sender=Post)
def send_post_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'Новий пост створено'
        message = f'Заголовок посту: {instance.title}\nАвтор: {instance.author}\nДата створення: {instance.created_at}'
        send_notification_email(subject, message)


@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        subject = 'Новий коментар створено'
        message = f'Коментар автора {instance.author} до посту: {instance.post.title}\nТекст коментаря: {instance.text}'
        send_notification_email(subject, message)

