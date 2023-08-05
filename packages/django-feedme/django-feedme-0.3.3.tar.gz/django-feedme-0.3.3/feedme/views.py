from django.views.generic import ListView, FormView, CreateView
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from infuse.auth.permissions import LoginRequiredMixin

from .models import Feed, FeedItem, Category
from .forms import AddFeedForm, ImportFeedForm
from .google_takeout import GoogleReaderTakeout
from .mixins import AjaxableResponseMixin


class FeedList(LoginRequiredMixin, ListView):
    """
    Show the feed list for the logged in user.
    @todo - need to protect ti with logged in user
    """
    template_name = 'feedme/feed_list.html'
    context_object_name = 'feed_items'

    def update_feeds(self, user):
        for feed in Feed.objects.filter(user=user):
            feed.update()
        return True

    def get_queryset(self):
        # Update the feed on page load..
        self.update_feeds(self.request.user)
        items = FeedItem.objects.my_feed_items(self.request.user).un_read()

        if self.kwargs.get('category', None):
            return items.category(self.kwargs.get('category'))

        if self.kwargs.get('feed_id', None):
            return items.filter(feed__id=self.kwargs.get('feed_id'))

        return items

    def get_context_data(self, **kwargs):
        context = super(FeedList, self).get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['add_form'] = AddFeedForm()

        return context


class ImportView(LoginRequiredMixin, FormView):
    template_name = 'feedme/takeout_form.html'
    form_class = ImportFeedForm
    success_url = 'feedme-feed-list'

    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)
        context['add_form'] = AddFeedForm()
        return context

    def form_valid(self, form):
        takeout = GoogleReaderTakeout(self.request.FILES['archive'])
        for data in takeout.subscriptions():
            Feed.objects.get_or_create(
                url=data['xmlUrl'], title=data['title'],
                user=self.request.user, last_update=None,
                category=form.cleaned_data['category']
            )
        return HttpResponseRedirect(reverse(self.get_success_url()))


class AddView(LoginRequiredMixin, AjaxableResponseMixin, CreateView):
    form_class = AddFeedForm
    model = Feed
