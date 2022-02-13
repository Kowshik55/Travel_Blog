from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from .models import *
from .forms import *
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin

now = timezone.now()
def post_list(request):

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    object_list = Post.objects.all().order_by('-publish')
    # Pagination
    paginator = Paginator(object_list, 6)  # 6 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)
    return render(request,
                  'journey/post_list.html',
                  {'page': page,
                   'num_visits': num_visits,
                   'posts': posts})


#to view details of the post from the application
@login_required
def post_detail(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    posts = Post.objects.all()
    return render(request, 'journey/post_detail.html',
                  {'num_visits': num_visits, 'posts': posts})


#to add new post from the application
@login_required
def post_new(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.created_date = timezone.now()
            post.save()
            return redirect('journey:post_list')
    else:
        form = PostForm()
    return render(request, 'journey/post_new.html', {'num_visits': num_visits,'form': form})


#to edit the post from the application



@login_required
def post_edit(request, pk):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        # update
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.updated_date = timezone.now()
            post.save()
            if request.user.is_superuser:
                return redirect('journey:post_detail')
            else:
                newrequest = HttpRequest()
                newrequest.method = 'GET'
                newrequest.user = request.user
                return travelblog_post(newrequest, post.pk)
    else:
        # edit
        form = PostForm(instance=post)
    return render(request, 'journey/post_edit.html', {'num_visits': num_visits,'form': form})


#to delete the post from the application
@login_required
def post_delete(request, pk):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    if request.user.is_superuser:
        return redirect('journey:post_detail')
    else:
        return redirect('journey:post_list')



def travelblog_post(request, post_id):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    post = get_object_or_404(Post, id=post_id)
    # List of active comments for this post
    comments = post.comments.filter()
    new_comment = None
    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            new_comment.name = request.user.first_name
            new_comment.email = request.user.email
            # Save the comment to the database
            new_comment.save()
            comment_form = CommentForm()
    else:
        comment_form = CommentForm()
    return render(request, 'journey/travelblog_post.html',
                  {'post': post, 'num_visits': num_visits, 'comments': comments,
                   'comment_form': comment_form})




#comment list view from the application
@login_required
def comment_list(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    comments = Comment.objects.all()
    return render(request, 'journey/comment_list.html',
              {'num_visits': num_visits, 'comments': comments})


#to edit the comment from the application
@login_required
def comment_edit(request, pk):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    comment = get_object_or_404(Comment, pk=pk)
    if request.method == "POST":
        # update
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.updated_date = timezone.now()
            comment.save()
            return redirect('journey:comment_list')
    else:
        # edit
        form = CommentForm(instance=comment)
    return render(request, 'journey/comment_edit.html', {'num_visits': num_visits, 'form': form})



#to delete the comment from the application
@login_required
def comment_delete(request, pk):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('journey:comment_list')

def signup(request):
    if request.method == 'POST':
        user_form = CreateUserAccountForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            username = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect("journey:post_list")
    else:
        user_form = CreateUserAccountForm()
    return render(request, 'journey/signup.html', {'user_form': user_form})



