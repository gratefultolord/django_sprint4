from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.views import View

from blog.models import Post


class PostMixinView(UserPassesTestMixin, View):
    model = Post
    template_name = 'blog/create.html'

    def test_func(self):
        try:
            self.post_id = self.kwargs['pk']
        except KeyError:
            return False
        post = self.get_object()
        return post.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', pk=self.post_id)
