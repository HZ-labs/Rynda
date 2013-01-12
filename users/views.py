# -*- coding: utf-8 -*-

from django.shortcuts import redirect, render_to_response
from django.contrib.auth.models import User
from django.views.generic.detail import DetailView

from core.views import RyndaFormView, RyndaListView
from core.backends import IonAuth
from users.forms import SimpleRegistrationForm
from users.models import Users
from templated_emails.utils import send_templated_email

class UserDetail(DetailView):
    model = User
    template_name = 'user_profile.html'
    context_object_name = 'u'

class UserList(RyndaListView):
    template_name = 'userlist.html'
    context_object_name = 'users'
    queryset = User.objects.select_related().filter(is_active=True).order_by('date_joined')
    paginator_url = '/user/page/'
    paginate_by = 10


class CreateUser(RyndaFormView):
    template_name = 'registerform_simple.html'
    form_class = SimpleRegistrationForm
    success_url = '/'

    def form_valid(self, form):
        user = User()
        auth = IonAuth()
        ce = form.cleaned_data
        user.first_name = ce['first_name']
        user.last_name = ce['last_name']
        user.email = ce['email']
        user.username = ce['email']
        user.password = auth.password_hash(ce['password1'])
        user.save()
        pr = user.get_profile()
        pr.activCode = auth.generate_code()
        pr.save()
        send_templated_email([user], 'emails/registration_confirm',
            {'user': user, 'site_url': self.request.META['SERVER_NAME'],
             'activation_code': pr.activCode,
            }
        )
        return redirect(self.success_url)


def activate_profile(request, pk, key):
    user = User.objects.get(id=pk)
    p = user.get_profile()
    if p.activCode == key:
        user.is_active = True
        user.save()
        p.activCode = ''
        p.save()
        redirect('/login')
    redirect('/')
