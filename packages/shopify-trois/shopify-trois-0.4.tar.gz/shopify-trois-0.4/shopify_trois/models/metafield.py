# -*- coding: utf-8 -*-
"""
    shopify_trois.models.metafield

    Shopify-Trois Metafield

    :copyright: (c) 2013 by Martin Samson
    :license: MIT, see LICENSE for more details.
"""

from .model import Model


class Metafield(Model):
    """MetaField
    http://docs.shopify.com/api/metafield
    """

    resource = "metafields"

    supported = [
        "count", "create", "delete", "index", "update", "view"
    ]

    properties = [
        "created_at", "description", "id", "key", "namespace", "owner_id",
        "updated_at", "value", "value_type", "owner_resource"
    ]
