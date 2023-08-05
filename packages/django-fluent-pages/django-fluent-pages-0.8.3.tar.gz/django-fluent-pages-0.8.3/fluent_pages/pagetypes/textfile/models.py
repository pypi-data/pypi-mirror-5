from django.db import models
from django.utils.translation import ugettext_lazy as _
from fluent_pages.models import Page


class TextFile(Page):
    """
    A plain text node.
    """
    CONTENT_TYPE_CHOICES = (
        ('text/plain', _("Plain text")),
        ('text/xml', _("XML")),
        ('text/html', _("HTML")),
    )
    UTF8_TYPES = (
        'text/html', 'text/xml',
    )

    content = models.TextField(_("File contents"))
    content_type = models.CharField(_("File type"), max_length=100, default='text/plain', choices=CONTENT_TYPE_CHOICES)

    class Meta:
        verbose_name = _("Plain text file")
        verbose_name_plural = _("Plain text files")

