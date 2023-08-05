import functools
import logging
from django.http import HttpResponse
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse
from django.views.decorators.cache import never_cache
from restlib2.http import codes
from preserialize.serialize import serialize
from avocado.events import usage
from avocado.models import DataContext
from avocado.conf import settings
from serrano.forms import ContextForm
from .base import BaseResource
from . import templates

log = logging.getLogger(__name__)

HISTORY_ENABLED = settings.HISTORY_ENABLED

def context_posthook(instance, data, request):
    uri = request.build_absolute_uri

    # If this context is explicitly tied to a model (via the `count`)
    # specify the object names.
    if instance.model:
        opts = instance.model._meta
        data['object_name'] = opts.verbose_name.format()
        data['object_name_plural'] = opts.verbose_name_plural.format()

    data['_links'] = {
        'self': {
            'href': uri(reverse('serrano:contexts:single', args=[instance.pk])),
        }
    }
    return data


class ContextBase(BaseResource):
    cache_max_age = 0
    private_cache = True

    model = DataContext
    template = templates.Context

    def prepare(self, request, instance, template=None):
        if template is None:
            template = self.template
        posthook = functools.partial(context_posthook, request=request)
        return serialize(instance, posthook=posthook, **template)

    def get_queryset(self, request, **kwargs):
        "Constructs a QuerySet for this user or session."

        if hasattr(request, 'user') and request.user.is_authenticated():
            kwargs['user'] = request.user
        elif request.session.session_key:
            kwargs['session_key'] = request.session.session_key
        else:
            # The only case where kwargs is empty is for non-authenticated
            # cookieless agents.. e.g. bots, most non-browser clients since
            # no session exists yet for the agent.
            return self.model.objects.none()

        return self.model.objects.filter(**kwargs)

    def get_default(self, request):
        default = self.model.objects.get_default_template()

        if not default:
            log.warning('No default template for context objects')
            return

        form = ContextForm(request, {'json': default.json, 'session': True})

        if form.is_valid():
            instance = form.save()
            return instance

        log.error('Error creating default context', extra=dict(form.errors))


class ContextsResource(ContextBase):
    "Resource of active (non-archived) contexts"
    def get(self, request):
        queryset = self.get_queryset(request, archived=False)

        # Only create a default if a session exists
        if request.session.session_key:
            queryset = list(queryset)

            if not len(queryset):
                default = self.get_default(request)
                if default:
                    queryset.append(default)

        return self.prepare(request, queryset)

    def post(self, request):
        form = ContextForm(request, request.data)

        if form.is_valid():
            instance = form.save(archive=HISTORY_ENABLED)
            usage.log('create', instance=instance, request=request)
            response = self.render(request, self.prepare(request, instance),
                status=codes.created)
        else:
            response = self.render(request, dict(form.errors),
                status=codes.unprocessable_entity)
        return response


class ContextsHistoryResource(ContextBase):
    "Resource of archived (non-active) contexts"
    def get(self, request):
        queryset = self.get_queryset(request, archived=True)
        return self.prepare(request, queryset)


class ContextResource(ContextBase):
    "Resource for accessing a single context"
    def get_object(self, request, pk=None, session=None, **kwargs):
        if not pk and not session:
            raise ValueError('A pk or session must used for the lookup')

        queryset = self.get_queryset(request, **kwargs)

        try:
            if pk:
                return queryset.get(pk=pk)
            else:
                return queryset.get(session=True)
        except self.model.DoesNotExist:
            pass

    def is_not_found(self, request, response, **kwargs):
        instance = self.get_object(request, **kwargs)
        if instance is None:
            return True
        request.instance = instance

    def get(self, request, **kwargs):
        usage.log('read', instance=instance, request=request)
        return self.prepare(request, request.instance)

    def put(self, request, **kwargs):
        instance = request.instance
        form = ContextForm(request, request.data, instance=instance)

        if form.is_valid():
            instance = form.save(archive=HISTORY_ENABLED)
            usage.log('update', instance=instance, request=request)
            response = self.render(request, self.prepare(request, instance))
        else:
            response = self.render(request, dict(form.errors),
                status=codes.unprocessable_entity)
        return response

    def delete(self, request, **kwargs):
        if request.instance.session:
            return HttpResponse(status=codes.bad_request)
        request.instance.delete()
        usage.log('delete', instance=instance, request=request)
        return HttpResponse(status=codes.no_content)


single_resource = never_cache(ContextResource())
active_resource = never_cache(ContextsResource())
history_resource = never_cache(ContextsHistoryResource())

# Resource endpoints
urlpatterns = patterns('',
    url(r'^$', active_resource, name='active'),
    url(r'^history/$', history_resource, name='history'),

    # Endpoints for specific contexts
    url(r'^(?P<pk>\d+)/$', single_resource, name='single'),
    url(r'^session/$', single_resource, {'session': True}, name='session'),
)
