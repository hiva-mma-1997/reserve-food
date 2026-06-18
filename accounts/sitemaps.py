from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemaps(sitemaps.Sitemap):
    priority=0.5
    changefreq='weekly'

    def items(self):
        return['login','reserve','logout']
    
    def location(self, item):
        return reverse(item)