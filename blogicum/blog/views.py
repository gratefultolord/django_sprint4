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
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin

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

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={USERNAME_KWARG: username})


class UserPostsView(SingleObjectMixin, ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = OBJECTS_PER_PAGE
    queryset = is_published_query()

    def get(self, request, *args, **kwargs):
        username = self.kwargs.get(USERNAME_KWARG)
        if not username:
            raise Http404('Ошибка 404')
        self.object = get_object_or_404(User, username=username)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context

    def get_queryset(self):
        if self.object == self.request.user:
            return all_query().filter(author=self.object)
        return super().get_queryset().filter(author=self.object)


class CategoryPostsView(SingleObjectMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    paginate_by = OBJECTS_PER_PAGE
    queryset = is_published_query()

    def get(self, request, *args, **kwargs):
        category = self.kwargs.get(CATEGORY_KWARG)
        if not category:
            raise Http404('Ошибка 404')
        self.object = get_object_or_404(
            Category, slug=category, is_published=True)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.object
        context[CATEGORY_KWARG] = category
        return context

    def get_queryset(self):
        return super().get_queryset().filter(category=self.object)


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


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = PK_KWARG

    def get_object(self, queryset=None):
        object = super().get_object(queryset=queryset)
        # Проверка на авторство
        if self.request.user == object.author:
            return object
        # В случае провала - проверка на 'is published'
        if object.is_published:
            return object
        # В случае провала обоих проверок - ошибка 404
        else:
            raise Http404('Ошибка 404')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all().select_related(
            'author')
        return context


@login_required
def add_comment(request, pk):
    if request.user.is_authenticated:
        post = get_object_or_404(Post, pk=pk)
    else:
        post = get_object_or_404(
            is_published_query(annotate_comment_count=False), pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=pk)


@login_required
def edit_comment(request, comment_id, pk):
    instance = get_object_or_404(Comment, id=comment_id, post_id=pk)
    form = CommentForm(request.POST or None, instance=instance)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    context = {
        'form': form,
        'comment': instance
    }

    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', pk=pk)
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, comment_id, pk):
    instance = get_object_or_404(Comment, id=comment_id, post_id=pk)
    if instance.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    context = {'comment': instance}
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', pk=pk)
    return render(request, 'blog/comment.html', context)
