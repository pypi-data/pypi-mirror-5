#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib.syndication.views import Feed
from django.contrib.sites.models import get_current_site
from django.shortcuts import get_object_or_404
from django.utils import timezone

from opps.articles.models import Article, Post, Album, Link
from opps.channels.models import Channel


class ArticleFeed(Feed):

    link = "/rss"

    def __call__(self, request, *args, **kwargs):
        self.site = get_current_site(request)
        return super(ArticleFeed, self).__call__(request, *args, **kwargs)

    def title(self):
        return "{0}'s news".format(self.site.name)

    def description(self):
        return "Latest news on {0}'s".format(self.site.name)

    def items(self):
        return Article.objects.filter(site=self.site).order_by(
            '-date_available').select_related('publisher')[:40]


class ChannelFeed(Feed):

    def __init__(self, model):
        _model = {'Post': Post, 'Album': Album, 'Link': Link}
        self.model = _model[model]

    def get_object(self, request, long_slug):
        self.site = get_current_site(request)
        return get_object_or_404(Channel,
                                 site=self.site,
                                 long_slug=long_slug)

    def link(self, obj):
        return "{0}RSS".format(obj.get_absolute_url())

    def title(self, obj):
        return u"{0}'s news on channel {1}".format(self.site.name, obj.name)

    def description(self, obj):
        return u"Latest news on {0}'s channel {1}".format(self.site.name,
                                                          obj.name)

    def items(self, obj):
        return self.model.objects.filter(
            site=self.site,
            channel_long_slug=obj.long_slug,
            date_available__lte=timezone.now(),
            published=True).order_by(
                '-date_available').select_related('publisher')[:40]
