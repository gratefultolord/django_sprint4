from blog.models import Post
from django.db.models import Count
from django.utils import timezone


def all_query(annotate_comment_count=True):
    query_set = (
        Post.objects.select_related(
            'category',
            'location',
            'author',
        )
        .order_by('-pub_date')
    )
    if annotate_comment_count:
        query_set = query_set.annotate(comment_count=Count('comments'))
    return query_set


def is_published_query(annotate_comment_count=True):
    query_set = all_query(annotate_comment_count).filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-pub_date')
    return query_set
