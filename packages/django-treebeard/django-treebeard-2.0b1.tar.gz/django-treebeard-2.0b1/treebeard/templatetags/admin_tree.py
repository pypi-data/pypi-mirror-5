# -*- coding: utf-8 -*-
"""
Templatetags for django-treebeard to add drag and drop capabilities to the
nodes change list - @jjdelc

"""

import sys

from django.db import models
from django.conf import settings
from django.contrib.admin.templatetags.admin_list import (
    _boolean_icon, result_headers, result_hidden_fields)
from django.contrib.admin.util import display_for_field, lookup_field
from django.contrib.admin.views.main import EMPTY_CHANGELIST_VALUE
from django.core.exceptions import ObjectDoesNotExist
from django.template import Library
from django.utils.html import conditional_escape, escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


register = Library()

if sys.version_info >= (3, 0):
    from django.utils.encoding import force_str, smart_str
    from urllib.parse import urljoin
else:
    from django.utils.encoding import force_unicode as force_str
    from django.utils.encoding import smart_unicode as smart_str
    from urlparse import urljoin

from treebeard.templatetags import needs_checkboxes


def items_for_result(cl, result, form):
    """
    Generates the actual list of data.

    @jjdelc:
    This has been shamelessly copied from original
    django.contrib.admin.templatetags.admin_list.items_for_result
    in order to alter the dispay for the first element
    """
    first = True
    pk = cl.lookup_opts.pk.attname
    for field_name in cl.list_display:
        row_class = ''
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except (AttributeError, ObjectDoesNotExist):
            result_repr = EMPTY_CHANGELIST_VALUE
        else:
            if f is None:
                if getattr(attr, 'boolean', False):
                    allow_tags = True
                    result_repr = _boolean_icon(value)
                else:
                    allow_tags = getattr(attr, 'allow_tags', False)
                    result_repr = smart_str(value)
                if allow_tags:
                    result_repr = mark_safe(result_repr)
                else:
                    # strip HTML tags
                    result_repr = escape(result_repr)
            else:
                if isinstance(f.rel, models.ManyToOneRel):
                    result_repr = escape(getattr(result, f.name))
                else:
                    result_repr = display_for_field(value, f)
                if isinstance(f, (models.DateField, models.TimeField)):
                    row_class = ' class="nowrap"'
        if force_str(result_repr) == '':
            result_repr = mark_safe('&nbsp;')
        # If list_display_links not defined, add the link tag to the
        # first field
        if (
            (first and not cl.list_display_links) or
            field_name in cl.list_display_links
        ):
            table_tag = {True: 'th', False: 'td'}[first]

            # This spacer indents the nodes based on their depth
            if first:
                spacer = '<span class="spacer">&nbsp;</span>' * (
                    result.get_depth() - 1)
            else:
                spacer = ''

            # This shows a collapse or expand link for nodes with childs
            if result.get_children_count():
                collapse = ('<a href="#" title="" class="collapse expanded">'
                            '-</a>')
            else:
                collapse = '<span class="collapse">&nbsp;</span>'

            # Add a <td/> before the first col to show the drag handler
            drag_handler = ''

            if first:
                drag_handler = ('<td class="drag-handler">'
                                '<span>&nbsp;</span></td>')

            first = False
            url = cl.url_for_result(result)
            # Convert the pk to something that can be used in Javascript.
            # Problem cases are long ints (23L) and non-ASCII strings.
            if cl.to_field:
                attr = str(cl.to_field)
            else:
                attr = pk
            value = result.serializable_value(attr)
            result_id = repr(force_str(value))[1:]
            onclickstr = (
                ' onclick="opener.dismissRelatedLookupPopup(window, %s);'
                ' return false;"')
            yield mark_safe(
                '%s<%s%s>%s %s <a href="%s"%s>%s</a></%s>' % (
                    drag_handler, table_tag, row_class, spacer, collapse, url,
                    (cl.is_popup and onclickstr % result_id or ''),
                    conditional_escape(result_repr), table_tag))
        else:
            # By default the fields come from ModelAdmin.list_editable, but
            # if we pull the fields out of the form instead of
            # list_editable custom admins can provide fields on a per
            # request basis
            if form and field_name in form.fields:
                bf = form[field_name]
                result_repr = mark_safe(
                    force_str(bf.errors) + force_str(bf))
            else:
                result_repr = conditional_escape(result_repr)
            yield mark_safe('<td%s>%s</td>' % (row_class, result_repr))
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield mark_safe(
            '<td>%s</td>' % force_str(form[cl.model._meta.pk.name]))


def get_parent_id(node):
    """Return the node's parent id or 0 if node is a root node."""
    if node.is_root():
        return 0
    return node.get_parent().pk


def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield (res.pk, get_parent_id(res), res.get_depth(),
                   res.get_children_count(),
                   list(items_for_result(cl, res, form)))
    else:
        for res in cl.result_list:
            yield (res.pk, get_parent_id(res), res.get_depth(),
                   res.get_children_count(),
                   list(items_for_result(cl, res, None)))


def check_empty_dict(GET_dict):
    """
    Returns True if the GET querstring contains on values, but it can contain
    empty keys.
    This is better than doing not bool(request.GET) as an empty key will return
    True
    """
    empty = True
    for k, v in GET_dict.items():
        # Don't disable on p(age) or 'all' GET param
        if v and k != 'p' and k != 'all':
            empty = False
    return empty


@register.inclusion_tag(
    'admin/tree_change_list_results.html', takes_context=True)
def result_tree(context, cl, request):
    """
    Added 'filtered' param, so the template's js knows whether the results have
    been affected by a GET param or not. Only when the results are not filtered
    you can drag and sort the tree
    """

    # Here I'm adding an extra col on pos 2 for the drag handlers
    headers = list(result_headers(cl))
    headers.insert(1 if needs_checkboxes(context) else 0, {
        'text': '+',
        'sortable': True,
        'url': request.path,
        'tooltip': _('Return to ordered tree'),
        'class_attrib': mark_safe(' class="oder-grabber"')
    })
    return {
        'filtered': not check_empty_dict(request.GET),
        'result_hidden_fields': list(result_hidden_fields(cl)),
        'result_headers': headers,
        'results': list(results(cl)),
    }


def get_static_url():
    """Return a base static url, always ending with a /"""
    path = getattr(settings, 'STATIC_URL', None)
    if not path:
        path = getattr(settings, 'MEDIA_URL', None)
    if not path:
        path = '/'
    if not path.endswith('/'):
        path += '/'
    return path


@register.simple_tag
def treebeard_css():
    """
    Template tag to print out the proper <link/> tag to include a custom .css
    """
    LINK_HTML = """<link rel="stylesheet" type="text/css" href="%s"/>"""
    css_file = urljoin(get_static_url(), 'treebeard/treebeard-admin.css')
    return LINK_HTML % css_file


@register.simple_tag
def treebeard_js():
    """
    Template tag to print out the proper <script/> tag to include a custom .js
    """
    path = get_static_url()
    SCRIPT_HTML = """<script type="text/javascript" src="%s"></script>"""
    js_file = '/'.join([path.rstrip('/'), 'treebeard', 'treebeard-admin.js'])

    # Jquery UI is needed to call disableSelection() on drag and drop so
    # text selections arent marked while dragging a table row
    # http://www.lokkju.com/blog/archives/143
    JQUERY_UI = """
    <script>
      (function($){jQuery = $.noConflict(true);})(django.jQuery);
    </script>
    <script type="text/javascript" src="%s"></script>
    """
    jquery_ui = urljoin(path, 'treebeard/jquery-ui-1.8.5.custom.min.js')

    scripts = [SCRIPT_HTML % 'jsi18n',
               SCRIPT_HTML % js_file,
               JQUERY_UI % jquery_ui]
    return ''.join(scripts)
