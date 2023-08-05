# -*- coding: utf-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.contrib.admin import SimpleListFilter

from .models import Image
from .forms import ImageModelForm
from .generate import image_url
from opps.core.admin import PublishableAdmin
from opps.core.admin import apply_opps_rules

User = get_user_model()


class UserListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _(u'User')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        # filter only users with images
        qs = User.objects.filter(image__isnull=False).distinct()
        if qs:
            return set([(item.username,
                         u"{0} ({1})".format(item.get_full_name(), item.email))
                       for item in qs])

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value() == "nouser":
            queryset = queryset.filter(user__isnull=True)
        elif self.value():
            queryset = queryset.filter(user__username=self.value())

        return queryset


@apply_opps_rules('images')
class ImagesAdmin(PublishableAdmin):
    form = ImageModelForm
    prepopulated_fields = {"slug": ("title",)}
    list_display = ['image_thumb', 'title', 'date_available', 'published']
    list_filter = [UserListFilter, 'date_available', 'published']
    search_fields = ['title']
    raw_id_fields = ['source']
    readonly_fields = ['image_thumb']
    exclude = ('user',)

    fieldsets = (
        (_(u'Identification'), {
            'fields': ('site', 'title', 'slug', 'image')}),
        (_(u'Crop'), {
            'fields': ('flip', 'flop', 'halign', 'valign', 'fit_in',
                       'smart', 'crop_x1', 'crop_x2', 'crop_y1', 'crop_y2',
                       'crop_example')}),
        (_(u'Content'), {
            'fields': ('description', 'tags', 'source')}),
        (_(u'Publication'), {
            'classes': ('extrapretty'),
            'fields': ('published', 'date_available')}),
    )

    def save_model(self, request, obj, form, change):
        if not change and len(form.more_image()) >= 1:
            [Image.objects.create(
                site=get_current_site(request),
                image=img,
                title=obj.title,
                slug=u"{0}-{1}".format(obj.slug, i),
                description=obj.description,
                published=obj.published,
                user=User.objects.get(pk=request.user.pk))
                for i, img in enumerate(form.more_image(), 1)]
        super(ImagesAdmin, self).save_model(request, obj, form, change)

    def image_thumb(self, obj):
        if obj.image:
            return u'<img width="60px" height="60px" src="{0}" />'.format(
                image_url(obj.image.url, width=60, height=60))
        return _(u'No Image')
    image_thumb.short_description = _(u'Thumbnail')
    image_thumb.allow_tags = True

admin.site.register(Image, ImagesAdmin)
