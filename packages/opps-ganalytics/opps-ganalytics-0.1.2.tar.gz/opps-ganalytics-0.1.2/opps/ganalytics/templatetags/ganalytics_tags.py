# -*- coding: utf-8 -*-
from django import template
from opps.ganalytics.models import Report


register = template.Library()


@register.simple_tag
def get_top_read(number=10, channel_slug=None, child_class=None,
                 template_name='ganalytics/top_read.html'):

    top_read = Report.objects.filter(
        article__isnull=False
    ).order_by('-pageview')

    if channel_slug:
        top_read = top_read.filter(article__channel_long_slug=channel_slug)

    if child_class:
        top_read = top_read.filter(article__child_class=child_class)

    top_read = top_read.distinct()[:number]

    t = template.loader.get_template(template_name)

    return t.render(template.Context({'top_read': top_read,
                                      'channel_slug': channel_slug,
                                      'number': number}))
