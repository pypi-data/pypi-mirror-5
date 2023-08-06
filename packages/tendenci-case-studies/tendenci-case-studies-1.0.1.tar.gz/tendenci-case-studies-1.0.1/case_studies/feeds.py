from tendenci.core.rss.feedsmanager import SubFeed
from tendenci.core.site_settings.utils import get_setting
from tendenci.core.perms.utils import PUBLIC_FILTER
from tendenci.core.sitemaps import TendenciSitemap

from case_studies.models import CaseStudy

class LatestEntriesFeed(SubFeed):
    title =  '%s Latest Case Studies' % get_setting('site','global','sitedisplayname')
    link =  "/case-studies/"
    description =  "Latest Case Studies by %s" % get_setting('site','global','sitedisplayname')

    def items(self):
        items = CaseStudy.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')[:20]
        return items

    def item_title(self, item):
        return item.client

    def item_description(self, item):
        return item.overview

    def item_pubdate(self, item):
        return item.create_dt

    def item_link(self, item):
        return item.get_absolute_url()

class CaseStudySitemap(TendenciSitemap):
    """ Sitemap information for case studies """
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        items = CaseStudy.objects.filter(**PUBLIC_FILTER).order_by('-create_dt')
        return items

    def lastmod(self, obj):
        return obj.create_dt
