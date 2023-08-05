import logging

from django.conf.urls.defaults import patterns, url
from django.contrib.gis import admin
from django.contrib.messages.api import get_messages
from django.contrib.sites.models import Site
from django.template.response import TemplateResponse

from location.models import LocationSnapshot, LocationSource, LocationSourceType

logger = logging.getLogger('location.admin')

class LocationSourceAdmin(admin.options.OSMGeoAdmin):
    list_display = (
                'created',
                'name',
                'type',
                'active'
            )
    list_filter = [
        'type'
    ]
    ordering = ['-created']

    def get_urls(self):
        urls = super(LocationSourceAdmin, self).get_urls()

        urls = patterns('location.views',
                url(
                    'configure-accounts/', 
                    self.admin_site.admin_view(self.configure_accounts),
                    name='location_configure_accounts'
                    )
                ) + urls
        return urls

    def configure_accounts(self, request):
        logger.info(self.model._meta)
        logger.info(self.model._meta.app_label)
        return TemplateResponse(
                    request,
                    'location/configure.html', {
                            'messages': get_messages(request),
                            'title': 'Configure Accounts',
                            'domain': Site.objects.get_current().domain
                        }
                )

class LocationSnapshotAdmin(admin.options.OSMGeoAdmin):
    list_display = (
                'date',
                'neighborhood',
                'nearest_city',
                'user',
            )
    date_hierarchy = 'date'
    raw_id_fields = ('source', )
    list_per_page = 25
    ordering = ['-date']
    list_filter = [
        'source__type'
    ]

    def nearest_city(self, obj):
        nearest = obj.find_nearest_city()
        if nearest.distance != None:
            return "%s (%d mi away)" % (
                        nearest,
                        nearest.distance.mi
                    )
        return nearest


admin.site.register(LocationSourceType)
admin.site.register(LocationSource, LocationSourceAdmin)
admin.site.register(LocationSnapshot, LocationSnapshotAdmin)
