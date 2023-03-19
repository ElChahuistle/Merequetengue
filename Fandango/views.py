from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, RedirectView, UpdateView
from django.views.generic.base import TemplateView

from Fandango.models import Pegoste


GLOBAL_PEGOSTES = Pegoste.objects.all()
mafufada = GLOBAL_PEGOSTES.values('author').annotate(pub_count=Count('pk')).order_by('-pub_count')[:5]
top_pegosteadores = User.objects.filter(pk__in=[author['author'] for author in mafufada]).only('username')

GLOBAL_EXTRA_CONTEXT = {
    'last_pegosteados': GLOBAL_PEGOSTES.order_by('-publish_date')[:5],
    'top_pegosteadores': top_pegosteadores
}


class HomePage(TemplateView):
    """
    Use of generic view to render homepage.
    """
    template_name = 'Fandango/home.html'
    extra_context = {**GLOBAL_EXTRA_CONTEXT, **{'author_home': False}}


class Pegosteadores(ListView):
    """
    Display existing Fandango blog sites using username.
    """

    model = User
    template_name = 'Fandango/pegosteadores.html'

    def get_queryset(self):
        return self.model.objects.filter(Q(is_active=True) and Q(groups__name='Pegosteadores'))


class Pegostes(ListView):
    """
    A list of pegostes belonging to a pegosteador indicated by <username> in '<username>/' or 'Fandango:pegostes_list'.
    This is to limit the pegostes to be listed, since it makes no sense to show ALL the existing pegostes.
    """

    model = Pegoste
    template_name = 'Fandango/pegostes.html'

    def get_queryset(self):
        """
        Override of ListView.get_queryset() to return a query set of
        pegostes authored by a pegosteador indicated by 'username'.

        :return: Queryset with pegostes related to a pegosteador ('username')
        """

        return self.model.objects.filter(author__username=self.kwargs['username'])


class PegosteView(DetailView):
    """
    This view is used when URL dispatcher receives /<username>/pegoste/<slug> or 'Fandango:pegoste'. It will get the
    pegostes authored by a pegosteador indicated by <username>, then produce the pegoste referenced by <slug>.
    """

    model = Pegoste
    template_name = 'Fandango/pegoste_view.html'
    slug_field = 'slug'
    extra_context = {**GLOBAL_EXTRA_CONTEXT, **{'author_home': False}}

    def get_queryset(self):
        """
        Overrides DetailView.get_queryset() to check if the pegosteador exists.

        :return: The query set with the pegostes belonging to a pegosteador.
        """

        pegostes_queryset = self.model.objects.filter(author__username=self.kwargs['username'])
        self.extra_context['recent_pegostes'] = pegostes_queryset.order_by('-publish_date')[:5]

        return pegostes_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']

        if self.request.user.username == self.kwargs['username'] and self.request.user.is_authenticated:
            self.extra_context['pegoste_updatable'] = True
        else:
            self.extra_context['pegoste_updatable'] = False

        return context


class PegosteadorHome(PegosteView):
    """
    Implements PegosteView to get the last pegoste published by the pegosteador as the homepage. Extending PegosteView
    gives us a query set that already checks if the pegosteador exists, but now it will get the last pegoste.
    """

    def get_object(self, **kwargs):
        """
        Overriding PegosteView.get_object() to get the last pegoste published.

        :return: The last published pegoste by a pegosteador.
        """

        query_set = self.get_queryset()

        # If the pegosteador exists, check if it has at least a pegoste. If true, then
        # return the last one, otherwise it will not return anything.
        if query_set.count() >= 1:
            last_pegoste = query_set.last()
        else:
            last_pegoste = None

        return last_pegoste

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.extra_context['author_home'] = True

        return context


class RedirectSlugPegoste(RedirectView):
    """
    This redirect prevents the use of PK in the URL to access a single pegoste, instead a slug will be use, thus
    redirecting to '<username>/pegoste/<slug>' or 'Fandango:pegoste'.
    """

    def get_redirect_url(self, *args, **kwargs):
        pegoste = get_object_or_404(Pegoste, pk=kwargs['pk'])

        return pegoste.get_absolute_url()


class RedirectAuth(RedirectView):
    """
    Simple redirect used after registration of a new pegosteador. This has the porpoise of separating URLs
    dispatching from each application.
    """

    def get_redirect_url(self, *args, **kwargs):
        if 'username' in self.kwargs:
            redirect_to = reverse('Fandango:pegosteador_home')
        else:
            redirect_to = reverse('Fandango:home')
        return redirect_to


# ToDo: Implement AccessMixin to restrict the addition and update of pegostes to the pegosteador logged in.
class AddPegoste(LoginRequiredMixin, CreateView):
    """
    The mixin view LoginRequiredMixin implements authentication mechanisms, so there is no need to write additional
    functionality or validations. For this to work, the first class in the definition of the view must be
    LoginRequiredMixin and then the generic view class.

    The default behavior of the mixin is to redirect to the login URL. The default value of "login_url" attribute
    in LoginRequiredMixin is the value in settings.LOGIN_URL, that its default value is 'accounts/login'.
    In this case, LoginRequiredMixin will use defaults.

    Reference:
        https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequiredmixin-mixin
        https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-LOGIN_URL
    """

    model = Pegoste
    fields = '__all__'
    template_name = 'Fandango/add_update_pegoste.html'
    extra_context = {**GLOBAL_EXTRA_CONTEXT, **{'add_update': True, 'add_update_view': 'Add Pegoste'}}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']

        recent_pegostes = GLOBAL_PEGOSTES.filter(author__username=self.kwargs['username']).order_by('-publish_date')[:5]
        self.extra_context['recent_pegostes'] = recent_pegostes

        return context


# ToDo: Implement AccessMixin to restrict the addition and update of pegostes to the pegosteador logged in.
class UpdatePegoste(LoginRequiredMixin, UpdateView):
    """
    The mixin view LoginRequiredMixin implements authentication mechanisms, so there is no need to write additional
    functionality or validations. For this to work, the first class in the definition of the view must be
    LoginRequiredMixin and then the generic view class.

    The default behavior of the mixin is to redirect to the login URL. The default value of "login_url" attribute
    in LoginRequiredMixin is the value in settings.LOGIN_URL, that its default value is 'accounts/login'.
    In this case, LoginRequiredMixin will use defaults.

    Reference:
        https://docs.djangoproject.com/en/4.1/topics/auth/default/#the-loginrequiredmixin-mixin
        https://docs.djangoproject.com/en/4.1/ref/settings/#std-setting-LOGIN_URL
    """

    model = Pegoste
    fields = '__all__'
    template_name = 'Fandango/add_update_pegoste.html'
    extra_context = {**GLOBAL_EXTRA_CONTEXT, **{'add_update': True, 'add_update_view': 'Update Pegoste'}}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.kwargs['username']

        recent_pegostes = GLOBAL_PEGOSTES.filter(author__username=self.kwargs['username']).order_by('-publish_date')[:5]
        self.extra_context['recent_pegostes'] = recent_pegostes

        return context
