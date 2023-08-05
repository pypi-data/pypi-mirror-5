"""
Views to display Metric data.

Note on Implementation: Since this app doesn't really use django's Models,
the views here are extended from ``TemplateView`` in order to keep things
simple.

"""
from datetime import datetime

from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.views.generic import TemplateView

from .models import R
from .forms import AggregateMetricForm, MetricCategoryForm


class ProtectedTemplateView(TemplateView):
    """Ensures that Users are authenticated and that they're staff users. This
    is used as a parent class for the rest of the views in this app."""

    _logged_in_staff = lambda u: u.is_authenticated() and u.is_staff

    @method_decorator(user_passes_test(_logged_in_staff))
    def dispatch(self, *args, **kwargs):
        return super(ProtectedTemplateView, self).dispatch(*args, **kwargs)


class ProtectedFormView(FormView):
    """Ensures that Users are authenticated and that they're staff users. This
    is used as a parent class for the rest of the views in this app."""

    _logged_in_staff = lambda u: u.is_authenticated() and u.is_staff

    @method_decorator(user_passes_test(_logged_in_staff))
    def dispatch(self, *args, **kwargs):
        return super(ProtectedFormView, self).dispatch(*args, **kwargs)


class MetricsListView(ProtectedTemplateView):
    template_name = "redis_metrics/metrics_list.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(MetricsListView, self).get_context_data(**kwargs)
        r = R()
        # Metrics organized by category, like so:
        # { <category_name>: [ <slug1>, <slug2>, ... ]}
        data['metrics'] = r.metric_slugs_by_category()

        # Include gauges in the default View. They're *technically* a list
        # of metrics, too!
        gauges = {
            'slugs': list(r.gauge_slugs()),
            'data': {}
        }
        if gauges['slugs']:
            for slug in gauges['slugs']:
                gauges['data'][slug] = r.get_gauge(slug)
        data['gauges'] = gauges
        return data


class MetricDetailView(ProtectedTemplateView):
    template_name = "redis_metrics/metric_detail.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(MetricDetailView, self).get_context_data(**kwargs)
        data['slug'] = kwargs['slug']
        data['metrics'] = R().get_metric(kwargs['slug'])
        return data


class MetricHistoryView(ProtectedTemplateView):
    template_name = "redis_metrics/metric_history.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(MetricHistoryView, self).get_context_data(**kwargs)
        try:
            # Accept GET query params for ``since``
            since = self.request.GET.get('since', None)
            if since and len(since) == 10:  # yyyy-mm-dd
                since = datetime.strptime(since, "%Y-%m-%d")

            data.update({
                'slug': kwargs['slug'],
                'granularity': kwargs['granularity'],
                'metric_history': R().get_metric_history(
                    slugs=kwargs['slug'],
                    since=since,
                    granularity=kwargs['granularity']
                )
            })
        except KeyError:
            raise Http404
        return data


class AggregateFormView(ProtectedFormView):
    """Allow viewing multiple metrics at once. Displays a form for entering
    the metrics that you want to view, and displays them all on POST."""
    template_name = "redis_metrics/aggregate.html"
    form_class = AggregateMetricForm

    def get_success_url(self):
        """Reverses the ``redis_metric_aggregate_detail`` URL using
        ``self.metric_slugs`` as an argument. """
        return reverse('redis_metric_aggregate_detail',
                       args=[self.metric_slugs])

    def form_valid(self, form):
        """Pull the metrics from the submitted form, and store them as a
        plus-delimited string in ``self.metric_slugs``.

        For example, if the chosen slugs were 'foo' and 'bar', this would
        essentially do: ``self.metric_slugs = "foo+bar"``.

        """
        slugs = [k.strip() for k in form.cleaned_data['metrics']]
        self.metric_slugs = '+'.join(slugs)
        return super(AggregateFormView, self).form_valid(form)


class AggregateDetailView(ProtectedTemplateView):
    template_name = "redis_metrics/aggregate_detail.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(AggregateDetailView, self).get_context_data(**kwargs)
        slug_set = set(kwargs['slugs'].split('+'))
        data['slugs'] = slug_set
        data['metrics'] = R().get_metrics(slug_set)
        return data


class AggregateHistoryView(ProtectedTemplateView):
    template_name = "redis_metrics/aggregate_history.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(AggregateHistoryView, self).get_context_data(**kwargs)
        slug_set = set(kwargs['slugs'].split('+'))
        granularity = kwargs.get('granularity', 'daily')
        try:
            # Accept GET query params for ``since``
            since = self.request.GET.get('since', None)
            if since and len(since) == 10:  # yyyy-mm-dd
                since = datetime.strptime(since, "%Y-%m-%d")

            data.update({
                'slugs': slug_set,
                'granularity': granularity,
                'metric_history': R().get_metric_history_as_columns(
                    slugs=list(slug_set),
                    since=since,
                    granularity=granularity
                )
            })
        except KeyError:
            raise Http404
        return data


class CategoryFormView(ProtectedFormView):
    """Allows the user to (re)categorize existing metrics."""
    template_name = "redis_metrics/categorize.html"
    form_class = MetricCategoryForm

    def get(self, *args, **kwargs):
        """See if this view was called with a specified category."""
        self.initial = {"category_name":  kwargs.get('category_name', None)}
        return super(CategoryFormView, self).get(*args, **kwargs)

    def get_initial(self):
        """Initialize the form with the given category."""
        return self.initial

    def get_success_url(self):
        """Show the list of metrics."""
        return reverse('redis_metrics_list')

    def form_valid(self, form):
        """Get the category name/metric slugs from the form, and update the
        category so contains the given metrics."""
        form.categorize_metrics()
        return super(CategoryFormView, self).form_valid(form)
