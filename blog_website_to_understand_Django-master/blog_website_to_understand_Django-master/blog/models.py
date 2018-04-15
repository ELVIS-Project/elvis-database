from django.db import models
from django.utils import timezone
from django.urls import reverse
# Create your models here.


class Post(models.Model):  # what do you want a post to be? Define it here
    author = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)  # author connects the superuser on the website
    # , which will pop out a menu for you to choose which superuser
    title = models.CharField(max_length=200)
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    published_date = models.DateTimeField(blank=True, null=True)

    def publish(self):
        self.published_date = timezone.now()
        self.save()  # if you change the attribute of the class, you need to save it

    def approve_comments(self):
        return self.comments.filter(approved_comment=True)

    def get_absolute_url(self):
        return reverse("post_detail", kwargs={'pk': self.pk})  # After creating a post, go to 'post_detail' page,
        # with the primary key you just created

    def __str__(self):
        return self.title


class Comment(models.Model):  # this model is related with post model, some connections are needed
    post = models.ForeignKey('blog.Post', related_name='comments', on_delete=models.DO_NOTHING)
    author = models.CharField(max_length=200)  # If user is defined this way, you can just put a name into the text area
    text = models.TextField()
    created_date = models.DateTimeField(default=timezone.now)
    approved_comment = models.BooleanField(default=False)

    def approve(self):
        self. approved_comment = True  # if the comment is approved, save it
        self.save()

    def get_absolute_url(self):
        return reverse('post_list')  # When you commented, go back to the post list

    def __str__(self):
        return self.text
