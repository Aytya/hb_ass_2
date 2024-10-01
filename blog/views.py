from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .forms import PostForm, CommentForm
from .models import Post, User, RoundRobinMiddleware
from django.contrib.auth import get_user_model
User = get_user_model()

load_balancer = RoundRobinMiddleware()

# Create your views here.
def index(request):
    #return HttpResponse('Hello, world. You\'re at the blogs index.')
    return render(request, 'blog/post.html')

@cache_page(60)
def post_list(request):
    server = load_balancer.get_next_server()
    print(f"Routing to server: {server}")

    posts = Post.objects.select_related('author').prefetch_related('comments')
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'blog/post_list.html', {'posts': page_obj, 'page_obj': page_obj})

@cache_page(60)
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_count = cache.get(f'post_{post.pk}_comment_count')

    if comment_count is None:
        comment_count = post.comments.count()
        cache.set(f'post_{post.pk}_comment_count', comment_count, timeout=120)

    recent_comments = post.comments.all().order_by('-created_at')[:5]
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()

            cache.delete(f'post_{post.pk}_comment_count')

            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'blog/post_detail.html', {'post': post, 'recent_comments': recent_comments, 'comment_form': form, 'comment_count': comment_count})


@login_required
def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = User.objects.get(pk=request.user.pk)
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()

    return render(request, 'blog/post_add.html', {'form': form})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'blog/post_edit.html', {'form': form, 'post': post})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if post.author != request.user:
        return HttpResponseForbidden("You are not allowed to delete this post.")

    if request.method == "POST":
        post.delete()
        return redirect('post_list')

    return render(request, 'blog/post_delete.html', {'post': post})

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            print(request.user)
            comment.author = request.user
            comment.save()
            return JsonResponse({'message': 'Comment added successfully.'})

    return JsonResponse({'error': 'Invalid request method.'})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'message': 'User registered successfully.'})
    else:
        form = UserCreationForm()

    return render(request, 'blog/register.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful.'})
        else:
            return JsonResponse({'error': 'Invalid credentials.'}, status=400)

    return render(request, 'blog/login.html')

class CustomLoginView(LoginView):
    template_name = 'blog/login.html'

def health(request):
    return JsonResponse({'status': 'OK'}, status=200)

