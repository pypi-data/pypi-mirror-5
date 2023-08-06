from django.utils.translation import ugettext_lazy as _
from models import Theme


def enable_theme(modeladmin, request, queryset):
    for t in Theme.objects.all():
        t.enabled = False
        t.save()
    for i in queryset:
        i.enabled = True
        i.debug = False
        i.save()
        break
enable_theme.short_description = _('Enable theme without debug')


def enable_theme_with_debug(modeladmin, request, queryset):
    for t in Theme.objects.all():
        t.enabled = False
        t.save()
    for i in queryset:
        i.enabled = True
        i.debug = True
        i.save()
        break
enable_theme_with_debug.short_description = _('Enable theme with debug')


def disable_theme(modeladmin, request, queryset):
    for i in queryset:
        i.enabled = False
        i.save()
disable_theme.short_description = _('Disable theme')
