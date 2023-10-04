from blog.models import Post
from django.db.models import Count
from django.utils import timezone


def all_query():
    query_set = (
        Post.objects.select_related(
            "category",
            "location",
            "author",
        )
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )
    return query_set


def is_published_query():
    query_set = all_query().filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    )
    return query_set
