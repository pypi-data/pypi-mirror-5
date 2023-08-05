from django.db import models
from django.contrib.contenttypes import generic
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType


class MetaTag(models.Model):
    url = models.CharField(_('URL-path'), max_length=100, blank=True)
    content_type = models.ForeignKey(ContentType, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = generic.GenericForeignKey()
    title = models.CharField(_('title'), max_length=80, blank=True)
    keywords = models.CharField(_('keywords'), max_length=250, blank=True)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        ordering = ('id',)
        db_table = 'meta_tags'
        unique_together = ('content_type', 'object_id')
        verbose_name = _('meta tags')
        verbose_name_plural = _('meta tags')

    def __unicode__(self):
        return force_unicode(self.content_object)
