from blog.forms import CommentForm, PostForm, UserForm
from blog.models import Category, Comment, Post
from blog.querysets import all_query, is_published_query
from blog.mixins import PostMixinView

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

OBJECTS_PER_PAGE = 10
USERNAME_KWARG = 'username'
PK_KWARG = 'pk'
CATEGORY_KWARG = 'category'


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    queryset = is_published_query()
    paginate_by = OBJECTS_PER_PAGE


class UserEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={USERNAME_KWARG: username})


class UserPostsView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    queryset = is_published_query()
    author = None
    paginate_by = OBJECTS_PER_PAGE

    def get_queryset(self):
        username = self.kwargs.get(USERNAME_KWARG)
        if not username:
            raise Http404
        self.author = get_object_or_404(User, username=username)
        if self.author == self.request.user:
            return all_query().filter(author=self.author)
        return super().get_queryset().filter(author=self.author)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'page_obj'
    paginate_by = OBJECTS_PER_PAGE

    def get_queryset(self):
        category_slug = self.kwargs.get(CATEGORY_KWARG)
        category = get_object_or_404(
            Category, slug=category_slug, is_published=True
        )
        queryset = is_published_query().filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get(CATEGORY_KWARG)
        context[CATEGORY_KWARG] = get_object_or_404(
            Category, slug=category_slug, is_published=True)
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        url = reverse(
            'blog:profile',
            args=(self.request.user.get_username(),)
        )
        return url


class PostUpdateView(PostMixinView, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        url = reverse('blog:post_detail', args=(self.post_id,))
        return url


class PostDeleteView(PostMixinView, DeleteView):
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = PK_KWARG
    slug_field = PK_KWARG
    slug_url_kwarg = PK_KWARG

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs[PK_KWARG])
        queryset = all_query(
            annotate_comment_count=False
            ) if self.request.user == post.author else is_published_query(
                annotate_comment_count=False)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all().select_related(
            'author')
        return context


@login_required
def add_comment(request, pk):
    post = get_object_or_404(
        Post,
        pub_date__lte=timezone.now(),
        is_published=True,
        pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, comment_id, post_id):
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    form = CommentForm(request.POST or None, instance=instance)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    context = {
        'form': form,
        'comment': instance
    }

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, comment_id, post_id):
    instance = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=post_id)
    return render(request, 'blog/comment.html', context)
