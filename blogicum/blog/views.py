import pytz
from datetime import datetime

from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    ListView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.db.models import Count

from blog.models import Category, Post, Comment
from blog.forms import PostForm, CommentForm
from blog.mixins import PostDispatchMixin
from blog.constants import POSTS_PER_PAGE


User = get_user_model()
NOW = pytz.utc.localize(datetime.now())


class PostListView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"
    paginate_by = POSTS_PER_PAGE

    def get_queryset(self):
        queryset = (
            Post.objects.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=NOW,
            )
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )
        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user}
        )


class PostUpdateView(PostDispatchMixin, LoginRequiredMixin, UpdateView):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.object.pk}
        )


class PostDeleteView(PostDispatchMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    pk_url_kwarg = "post_id"
    success_url = reverse_lazy("blog:index")


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    pk_url_kwarg = "post_id"
    template_name = "blog/detail.html"

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        if post.author != self.request.user:
            if any(
                [
                    post.pub_date > NOW,
                    not post.is_published,
                    not post.category.is_published,
                ]
            ):
                raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related("author")
        return context


def user_profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = profile.posts.annotate(comment_count=Count("comments")).order_by(
        "-pub_date"
    )
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "profile": profile,
    }
    return render(request, "blog/profile.html", context)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = "blog/user.html"
    fields = ["username", "first_name", "last_name", "email"]

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    post_instance = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = "post_id"
    template_name = "blog/comment.html"

    def dispatch(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_instance
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.post_instance.pk}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs.get("comment_id"))
        if request.user != instance.author:
            return redirect("blog:post_detail", self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    pk_url_kwarg = "comment_id"
    template_name = "blog/comment.html"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("comment_id"))
        if self.request.user != comment.author:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs.get("post_id")}
        )


def category_posts(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    if not category.is_published:
        raise Http404
    post_list = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=NOW,
    ).order_by("-pub_date")
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, "blog/category.html", context)
