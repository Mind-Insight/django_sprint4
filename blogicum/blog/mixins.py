from django.shortcuts import redirect, get_object_or_404

from blog.models import Post


class PostDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Post,
            pk=kwargs.get("post_id"),
        )
        if instance.author != request.user:
            return redirect("blog:post_detail", self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)
