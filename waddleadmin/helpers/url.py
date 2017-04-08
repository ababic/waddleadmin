from __future__ import unicode_literals

from django.contrib.admin.utils import quote
from django.core.urlresolvers import reverse
from django.utils.http import urlquote

from wagtail.contrib.modeladmin.helpers import (
    AdminURLHelper as WagtailAdminURLHelper,
    PageAdminURLHelper as WagtailPageAdminURLHelper
)

wagtailadmin_page_actions = (
    'add', 'edit', 'delete', 'copy', 'move', 'preview', 'view_draft',
    'unpublish', 'revisions_index', 'add_subpage'
)


class AdminURLHelper(WagtailAdminURLHelper):

    def get_action_url_for_obj(self, action, obj, *args):
        if obj is None:
            return self.get_action_url(action, *args)
        args = (quote(getattr(obj, self.opts.pk.attname)),) + args
        return self.get_action_url(action, *args)


class PageAdminURLHelper(WagtailPageAdminURLHelper, AdminURLHelper):

    def get_action_url(self, action, *args, **kwargs):
        # Note: 'add' is used below, because that's the terminology used by
        # wagtail's page editing urls / views. For pages, if the action is
        # 'create', this method should supply the URL for `ChooseParentView`,
        # rather than going straight to 'wagtailadmin_pages:add'
        if action in wagtailadmin_page_actions:
            url_name = 'wagtailadmin_pages:%s' % action
            target_url = reverse(url_name, args=args, kwargs=kwargs)
            return '%s?next=%s' % (target_url, urlquote(self.index_url))
        return super(PageAdminURLHelper, self).get_action_url(action, *args,
                                                              **kwargs)
