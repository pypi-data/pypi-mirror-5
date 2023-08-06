=========
Changelog
=========

0.2.1
=====

* Add method ``get_http_absolute_url`` on channel model class
* Fix sitemap
* Remove contrib/db_backend , move to opps/db/backends #240
* Fix migrate run on postgresql - articles
* Add ChannelListFilter on HideContainerAdmin list_filter
* Add lazy translation on child_class list_display on HideContainerAdmin
* Add OPPS_CONTAINERS_BLACKLIST config on HideContainerAdmin
* Fix: image crop example
* Used get_descendants (mptt) on generic base view
* changing datetime.now to timezone.now on search index
* Fix unicode treatment JSONField rendering
* Write test on ``opps.db._redis``
* Set dynamic db int, on db drive
* Fix: get_child recursivelly on template tag ``get_container_by_channel``
* Changelog organize
* Fix docs organize
* Remove Opps theme docs, used default Read the Docs

0.2.0
=====

* Content type (Container)
* Isoled boxes application
* ContainerBox, generic box (concept)
* Used Container in all application
* Archives, file manager
* Images used archives
* Used RST on README, pypi compatibility
* Add contrib pattern (like django)
* Upgrade haystack to 2.0 (stable)
* Opps Generic Views
* New view format, used to URLs pattern
* Add Grappelli dependence of the project
* Create Opps DB (NoSQL Database architecture)
* Add redis support (Opps BD)
* Contrib notification, central message exchange between container
* * websocket support
* * sse support
* * long pulling support
* Add field highlight on ContainerBox option
* Fix bug generic view list, get recursive channel list
* Dynamic fields on container, via JSONField
* * Text
* * Textarea
* * Checkbox
* * Radio
* Fix template tag ``image_obj``
* Add optional container filtering by child_class in ListView
* fix flatpage url
* Adding .html in containers url

0.1.9
=====

0.1.8
=====

* Queryset cache on generic view
* Add image thumb on ArticleBox
* Send current site to template ``{{ SITE }}``
* In /rss feed, filter channels by **published** and **include_in_main_rss**
* RSS Feed now renders in a template
* Flatpage is content type Article
* **Hotfix** fix *memory leak* (articles generic view)
* Chekc OPPS_PAGINATE_NOT_APP app not used PAGINATE_SUFFIX
* Used cache page

0.1.7
=====

0.1.6
=====

0.1.5
=====

0.1.4
=====

0.1.3
=====

0.1.0
=====

* Initial release
