from django import forms
from django.conf import settings
from django.template.loader import render_to_string


class MultipleUpload(forms.FileInput):
    def render(self, name, value, attrs=None):
        _value = ""
        _height = ""
        _width = ""
        if value:
            _value = "{}{}".format(settings.MEDIA_URL, value)
            _height = value.height
            _width = value.width
        return render_to_string("admin/opps/images/multiupload.html",
                                {"name": name, "value": _value,
                                 'height': _height,
                                 'width': _width,
                                 "STATIC_URL": settings.STATIC_URL})


class CropExample(forms.TextInput):
    def render(self, name, value, attrs=None):
        return render_to_string(
            "admin/opps/images/cropexample.html",
            {"name": name, "value": value,
             'STATIC_URL': settings.STATIC_URL,
             "THUMBOR_SERVER": settings.THUMBOR_SERVER,
             "THUMBOR_MEDIA_URL": settings.THUMBOR_MEDIA_URL})
