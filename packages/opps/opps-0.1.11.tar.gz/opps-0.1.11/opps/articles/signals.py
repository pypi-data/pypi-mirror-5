#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.redirects.models import Redirect
from googl.short import GooglUrlShort


def redirect_generate(sender, instance, created, **kwargs):
    obj, create = Redirect.objects.get_or_create(
        old_path=instance.get_absolute_url(),
        site=instance.site,
        new_path=instance.url)
    obj.save()


def shorturl_generate(sender, instance, created, **kwargs):
    if not instance.short_url:
        instance.short_url = GooglUrlShort(
            instance.get_http_absolute_url()
        ).short()
        instance.save()


def delete_article(sender, instance, using, **kwargs):
    """
    Ensure objects are deleted from mother class Article
    when deleted from child class
    """
    try:
        instance.__class__.objects.filter(
            child_class=instance.child_class,
            slug=instance.slug,
            channel=instance.channel,
            site=instance.site
        ).delete()
    except instance.__class__.DoesNotExist:
        # object not exists
        pass
