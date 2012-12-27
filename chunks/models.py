# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

class Chunk(models.Model):
    """
    A Chunk is a piece of content associated
    with a unique key that can be inserted into
    any template with the use of a special template
    tag
    """
    key         = models.CharField(_(u'Key'), help_text=_(u"A unique name for this chunk of content"), blank=False, max_length=255)
    content     = models.TextField(_(u'Content'), blank=True)
    description = models.CharField(_(u'Description'), blank=True, max_length=64, help_text=_(u"Short Description"))
    site        = models.ForeignKey(Site, default=Site.objects.get_current())

    objects = Manager()
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name = _(u'site content block')
        verbose_name_plural = _(u'site content blocks')

    def __unicode__(self):
        return u"%s" % (self.key,)
