from tendenci.core.rss.feedsmanager import SubFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import PUBLIC_FILTER
from tendenci.core.sitemaps import TendenciSitemap

from staff.models import Staff

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Staff' % get_setting('site','global','sitedisplayname')
    link =  "/staff/"
    description =  "Latest Staff by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = Staff.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.name

    def item_description(self, item):
        return item.biography

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class StaffSitemap(TendenciSitemap):
    """ Sitemap information for staff """
    changefreq = "monthly"
    priority = 0.5
    
    def items(self):
        items = Staff.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.update_dt
