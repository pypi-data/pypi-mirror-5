# -*- coding: utf-8 -*-


from django.conf import settings


AJAX_LIST_SETTINGS = {
    'SORT_ASC_ELEMENT': '    <span>+</span>',
    'SORT_DESC_ELEMENT':    '<span>-</span>',
    'PAGE_FIRST_ELEMENT':   '<span>&lt;&lt;</span>',
    'PAGE_PREVIOUS_ELEMENT':'<span>&lt;</span>',
    'PAGE_NEXT_ELEMENT':    '<span>&gt;</span>',
    'PAGE_LAST_ELEMENT':    '<span>&gt;&gt;</span>'
}


AJAX_LIST_SETTINGS.update( getattr(settings, 'AJAX_LIST_SETTINGS', lambda: {})() )