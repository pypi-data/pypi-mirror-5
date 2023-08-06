from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import get_callable
from django.conf.urls.defaults import patterns, url

try:
    from feincms.admin.item_editor import ItemEditor
except ImportError:
    from feincms.admin.editor import ItemEditor

from feincms.content.application import models as app_models
from feincms.models import Base
from feincms.module.mixins import ContentModelMixin
from feincms.utils.managers import ActiveAwareContentManagerMixin


class ArticleManager(ActiveAwareContentManagerMixin, models.Manager):
    active_filters = {'simple-active': Q(active=True)}


class Article(ContentModelMixin, Base):
    active = models.BooleanField(_('active'), default=True)

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, help_text=_('This will be automatically generated from the name'), unique=True, editable=True)

    class Meta:
        ordering = ['title']
        unique_together = []
        verbose_name = _('article')
        verbose_name_plural = _('articles')

    objects = ArticleManager()

    @classmethod
    def get_urlpatterns(cls):
        import views
        return patterns('',
            url(r'^$', views.ArticleList.as_view(), name='article_index'),
            url(r'^(?P<slug>[a-z0-9_-]+)/$', views.ArticleDetail.as_view(), name='article_detail'),
        )

    @classmethod
    def remove_field(cls, f_name):
        """Remove a field. Effectively inverse of contribute_to_class"""
        # Removes the field form local fields list
        cls._meta.local_fields = [f for f in cls._meta.local_fields if f.name != f_name]

        # Removes the field setter if exists
        if hasattr(cls, f_name):
            delattr(cls, f_name)

    @classmethod
    def get_urls(cls):
        return cls.get_urlpatterns()

    def __unicode__(self):
        return u"%s" % (self.title)

    @app_models.permalink
    def get_absolute_url(self):
        return ('article_detail', 'articles.urls', (), {'slug': self.slug})

    @property
    def is_active(self):
        return Article.objects.active().filter(pk=self.pk).count() > 0


ModelAdmin = get_callable(getattr(settings, 'ARTICLE_MODELADMIN_CLASS', 'django.contrib.admin.ModelAdmin'))


class ArticleAdmin(ItemEditor, ModelAdmin):
    list_display = ['__unicode__', 'active',]
    list_filter = []
    search_fields = ['title', 'slug']
    filter_horizontal = []
    prepopulated_fields = {
        'slug': ('title',),
    }
    fieldsets = [
        (None, {
            'fields': ['active', 'title', 'slug']
        }),
        # <-- insertion point, extensions appear here, see insertion_index above
    ]

    # TODO: add_extension_options is copied from feincms.module.page.modeladmins.PageAdmin
    # When FeinCMS 1.7 is released it should be provided by extending feincms.extensions.ExtensionModelAdmin
    fieldset_insertion_index = 1
    @classmethod
    def add_extension_options(cls, *f):
        if isinstance(f[-1], dict):     # called with a fieldset
            cls.fieldsets.insert(cls.fieldset_insertion_index, f)
            f[1]['classes'] = list(f[1].get('classes', []))
            f[1]['classes'].append('collapse')
        else:   # assume called with "other" fields
            cls.fieldsets[1][1]['fields'].extend(f)
