from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View

from blog.models import Post


class PostMixinView(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Post
    template_name = 'blog/create.html'

    def test_func(self):
        self.post_id = self.kwargs['pk']
        post = self.get_object()
        return post.author == self.request.user

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return redirect('blog:post_detail', pk=self.post_id)
        return super().dispatch(request, *args, **kwargs)
