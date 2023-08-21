from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.generic import ListView,CreateView, DetailView,UpdateView,View
from django.shortcuts import render,get_object_or_404,redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse,reverse_lazy
from .models import User,Post,Like,UserProfile,Follow
from .forms import PostForm
 

class PostListView(ListView):

    def get(self, request):
        posts = Post.objects.all()[::-1]
        paginator = Paginator(posts, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        form = PostForm()
        return render(request, 'network/post_list.html', {'page_obj': page_obj, 'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return JsonResponse({'success': True, 'message': 'Post created successfully.', 'content': post.content})
        else:
            return JsonResponse({'success': False, 'message': 'Error creating post.'})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'network/post_form.html'
    success_url = reverse_lazy('post-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)   
 
class PostDetailView(DetailView):
    model = Post
    template_name = 'network/post_detail.html'
    context_object_name = 'post'  


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'network/post_form.html'

class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        return JsonResponse({'success': True, 'count': post.likes.count()})


def follow_user(request, user_id):
    if request.method == 'POST' and request.is_ajax():
        user_to_follow = get_object_or_404(User, id=user_id)
        user_profile = request.user.userprofile

        if user_to_follow != request.user:  # Don't follow yourself
            user_profile.following.add(user_to_follow)
            return JsonResponse({'message': 'User followed successfully'})
        else:
            return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

class UserProfileView(View):
    template_name = 'network/user_profile.html'

    def get(self, request, user_id):
        profile_user = get_object_or_404(User, id=user_id)

        try:
            user_profile = UserProfile.objects.get(user=profile_user)
            followers_count = user_profile.followers.count()
            following_count = user_profile.following.count()
            followers = user_profile.followers.all()
        except UserProfile.DoesNotExist:
            followers_count = 0
            following_count = 0
            followers = []

        user_posts = profile_user.posts.all()[::-1]
        context = {
            'profile_user': profile_user,
            'user_posts': user_posts,
            'followers': followers,
            'followers_count': followers_count,
            'following_count': following_count,
        }

        return render(request, self.template_name, context)

@login_required
def follow_user(request, user_id):
    followed_user = get_object_or_404(User, id=user_id)
    follower = request.user

    if Follow.objects.filter(follower=follower, followed_user=followed_user).exists():
        Follow.objects.filter(follower=follower, followed_user=followed_user).delete()
    else:
        Follow.objects.create(follower=follower, followed_user=followed_user)

    return redirect('user-profile', user_id=user_id)

def user_list(request):
    users_list = User.objects.all()
    return render(request, 'network/users_list.html', {'users_list': users_list})


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("list"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("list"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("list"))
    else:
        return render(request, "network/register.html")
