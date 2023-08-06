from django.conf import settings
from django.views.decorators.csrf import requires_csrf_token
from django.shortcuts import render, redirect

from .utils import get_ab_template, find_template


SIMPLE_TEMPLATES_DIR = getattr(settings, 'SIMPLE_TEMPLATES_DIR', 'simple_templates')


class SimplePageFallbackMiddleware(object):
    def process_response(self, request, response):
        # No need to check for a simple template for non-404 responses.
        if response.status_code != 404:
            return response

        # set up the location where this template should reside
        template = u"{0}/{1}.html".format(SIMPLE_TEMPLATES_DIR, request.path.strip('/') or u'_homepage_')

        # if it doesn't exist, continue with the 404 response
        if not find_template(template):
            return response

        # if the template exists, ensure the trailing slash is present and redirect if necessary
        if not request.path.endswith(u'/') and settings.APPEND_SLASH:
            url = request.path + u"/"
            qs = request.META.get('QUERY_STRING')
            if qs:
                url += u'?' + qs
            return redirect(url, permanent=True)

        @requires_csrf_token
        def protect_render(request):
            # check for the presence of an a/b test template page
            return render(request, get_ab_template(request, template))

        return protect_render(request)