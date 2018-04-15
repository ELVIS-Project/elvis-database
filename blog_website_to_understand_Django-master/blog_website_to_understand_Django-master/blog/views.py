from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
# with (), we can import as many modules as we want when changing the line
# Create your views here.


class AboutView(TemplateView):  # show about page
    template_name = 'about.html'


class PostListView(ListView):  # home page: show a list of post
    model = Post  # what do you want to show in this list: post, so model = Post

    def get_queryset(self):  # Pythonese SQL query
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        # sort with publishing date
        # Grab Post model, filter the object based on the conditions
        # SQL like query: field__lookuptyle = value. lte: less than or equal to


class PostDetailView(DetailView):  # show the content of the post when clicking
    model = Post  #


class CreatePostView(LoginRequiredMixin,CreateView): # This function searches for post_form page!
    # you cannot create a post unless logged in
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'  # save the new post, and it redirects to post_detail page

    form_class = PostForm  # This creates a new PostForm, and PostForm already specifies which fields we need to create
    model = Post


class PostUpdateView(LoginRequiredMixin, UpdateView):  # this is the same with creating one (the view)
    login_url = '/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm
    model = Post


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')  # when manage to delete the post, go back to post_list view


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'blog/post_list.html'
    model = Post

    def get_queryset(self):  # without this line, it is literally the same with PostDetailView
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')  # filter out all published


########################################

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post,pk=pk)
    post.publish()
    return redirect('post_detail',pk=pk)


@login_required  # login required, if not, go to the login page
# @ this is a decorator, and login_required is a function, but using @ to use it quickly
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)  # locate the post first
    if request.method == 'POST':  # when submitting a comment, it will send a POST back to the server
        form = CommentForm(request.POST)  # user submit a comment form, the content is in request.Post
        if form.is_valid():  # form validation
            comment = form.save(commit=False)  # get the comments
            comment.post = post  # this comments attach to this post
            comment.save() # save this example of the comment
            return redirect('post_detail', pk=post.pk)  # return to this post when comment is successfully submitted
    else:  # if ths form is invalid
        form = CommentForm()
    return render(request, 'blog/comment_form.html',{'form':form})

@login_required
def comment_approve(request,pk):
    comment = get_object_or_404(Comment, pk=pk)  # get that comment
    comment.approve()  # approve it
    return redirect('post_detail', pk=comment.post.pk)  # return to the post which the comment is attached to

@login_required
def comment_remove(request,pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)  # return to the post which the comment is attached to
