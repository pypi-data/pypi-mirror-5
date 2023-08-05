#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.cache import cache_page

from .views import PostDetail, PostList, AlbumList, AlbumDetail, TagList
from .views import Search
from .views.feed import ArticleFeed, ChannelFeed


urlpatterns = patterns(
    '',
    url(r'^$', PostList.as_view(), name='home'),
    url(r'^(rss|feed)$', cache_page(60 * 2)(ArticleFeed()), name='feed'),
    url(r'^search/', Search(), name='search'),

    # ALBUM
    url(r'^album/(?P<long_slug>[\w\b//-]+)/(rss|feed)$',
        cache_page(60 * 2)(ChannelFeed(model='Album')),
        name='album_feed'),
    url(r'^album/(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(60 * 2)(AlbumDetail.as_view()), name='album_open'),
    url(r'^album/(?P<channel__long_slug>[\w\b//-]+)/$',
        cache_page(60 * 2)(AlbumList.as_view()), name='album_channel'),

    # TAGs
    url(r'^tag/(?P<tag>[\w//-]+)$',
        cache_page(60 * 2)(TagList.as_view()), name='tag_open'),

    # POST
    url(r'^(?P<long_slug>[\w\b//-]+)/(rss|feed)$',
        cache_page(60 * 2)(ChannelFeed(model='Post')), name='channel_feed'),
    url(r'^(?P<channel__long_slug>[\w//-]+)/(?P<slug>[\w-]+)$',
        cache_page(60 * 2)(PostDetail.as_view()), name='open'),
    url(r'^(?P<channel__long_slug>[\w\b//-]+)/$',
        cache_page(60 * 2)(PostList.as_view()), name='channel'),
)
