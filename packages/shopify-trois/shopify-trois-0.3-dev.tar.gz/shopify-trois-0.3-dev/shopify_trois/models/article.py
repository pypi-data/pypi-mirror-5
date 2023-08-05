# -*- coding: utf-8 -*-
"""
    shopify_trois.models.article

    Shopify-Trois Article

    :copyright: (c) 2013 by Martin Samson
    :license: MIT, see LICENSE for more details.
"""

from .model import Model
from .blog import Blog


class Article(Model):
    """Article
    http://docs.shopify.com/api/article
    """

    resource = "articles"
    is_subresource_of = Blog

    supported = ["index", "count", "view", "create", "update", "delete"]

    properties = [
        "author", "blog_id", "body_html", "created_at", "id", "published_at",
        "summary_html", "template_suffix", "title", "updated_at", "user_id",
        "tags"
    ]
