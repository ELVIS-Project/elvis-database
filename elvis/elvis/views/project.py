
'''
PROJECTS
'''
from django.shortcuts import render

from elvis.models.comment import Comment
from elvis.models.project import Project
from elvis.models.todo import Todo
from elvis.models.discussion import Discussion
from elvis.models.userprofile import UserProfile
from django.contrib.auth.models import User

from elvis.utils.helpers import partition, getRandomUsers, sendemails, removeBlanks

USER = UserProfile.objects.get(id=90)

def projects_list(request):
    if request.method == 'POST':
        emails = removeBlanks(request.POST.getlist("add-user"))
        existing = [user.email for user in User.objects.all()]
        correct = []
        wrong = []
        for email in emails:
            if email in existing:
                correct.append(email)
            else:
                wrong.append(email)
        subject = "ELVIS: " + USER.user.username + " would like to invite you to a project."
        message = ""
        sendemails(USER.user.email, correct, subject, message)
    projects = Project.objects.all()
    projects_list = partition(projects, 3)
    users = {}
    userDeco = partition(getRandomUsers(num=6), 3) 
    userDeco1 = userDeco[0]
    userDeco2 = userDeco[1]
    context = {'projects': projects_list, 
                'length':len(projects), 
                'users': users,
                'userDeco1':userDeco1, 
                'userDeco2':userDeco2}
    return render(request, 'project/project_list.html', context)

def project_view(request, pk):
    project = Project.objects.filter(pk=pk)[0]
    todos = Todo.objects.filter(project_id=pk)
    discussions = Discussion.objects.filter(project_id=pk)
    comments = {}
    for discussion in discussions:
        comments[discussion.id] = Comment.objects.filter(discussion_id=discussion.id).order_by('-created')
    context = {'content':project, 
                'todos': todos, 
                'discussions':discussions, 
                'comments':comments}
    return render(request, 'project/project_detail.html', context)

def project_participants(request, pk):
    project = Project.objects.filter(pk=pk)[0]
    return render(request, 'project/project_participants.html', {"content": project})

def project_discussions(request, pk):
    project = Project.objects.filter(pk=pk)[0]
    discussions = Discussion.objects.filter(project_id=pk)
    num_comments = {}
    for discussion in discussions:
        num_comments[discussion.id] = Comment.objects.filter(discussion_id=discussion.id).count()
    context = {"project": project, 
                "discussions": discussions,
                "comments": num_comments}
    return render(request, 'project/project_discussions.html', context)

def discussion_view(request, pk, did):
    if request.method == "POST":
        comment = request.POST.get('comment')
        obj = Comment(name='', text=comment, user_id=400, discussion_id=did)
        obj.save()
    project = Project.objects.get(pk=pk)
    discussion = Discussion.objects.get(pk=did)
    comments = Comment.objects.filter(discussion_id=did)
    context = {"project": project, "discussion": discussion, "comments": comments}
    return render(request, 'discussion/discussion_detail.html', context)