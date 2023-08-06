Django Template tag for building alphabetical index.
===================================================

Builds alpabetic index to navigate through collection sorted by firstletter.
Supports **english** and **russian** groups of alphabets.

Usage
=====

**view.py**::

    from django.views.generic.list_detail import object_list
    from alphabetic.utils import alphabetic_setup
    from .models import MyModel

        def myview(request):
            ...
            queryset = MyModel.objects.all()
            return object_list(request, alphabetic_setup(request, queryset, 'last_name'), template_name=template)

pp
**template.html**::

    {% show_alphabetic_filter %}


1. **alphabetic_setup(request, queryset, 'last_name')** - returns sorted queryset in alphabetical order by firstletter of
the attribute name, e.g. **last_name** or whatever attribute of the model you specified.
2. **show_alphabetic_filter** - template tag shows clickable alphabet in the template.

Clicking on the letter produce GET request to the current url with a tail **?firstletter=X**,
where **X** is the clicked letter.


Written by the development team of Arpaso company: http://arpaso.com
