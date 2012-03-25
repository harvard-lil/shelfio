from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from lil.shlvme.models import LoginForm
from django.core.context_processors import csrf
from django.contrib import auth

# TODO: a lot of the auth/auth functionality is crude. cleanup.

def process_register(request):
    """Register a new user"""
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            supplied_username = request.POST.get('username', '')
            supplied_password = request.POST.get('password1', '')
            user = auth.authenticate(username=supplied_username, password=supplied_password)
            
            auth.login(request, user)
            return HttpResponseRedirect(reverse('user_home', args=[user.username]))
    else:
        form = UserCreationForm()
        c = {}
        c.update(csrf(request))
        c.update({'form': form})
        return render_to_response("register.html", c)


def process_login(request):
    """The login handler"""
    
    # If we get a GET, send the login form
    if request.method == 'GET':
        if not request.user.is_authenticated():
            formset = LoginForm()
            
            c = {}
            c.update(csrf(request))
            c.update({'formset': formset})
            return render_to_response('login.html', c)
        else:
            return redirect(reverse('welcome'))

    # If we get a POST, someone has filled out the login form
    if request.method == 'POST':
        supplied_username = request.POST['username']
        supplied_password = request.POST['password']
        user = auth.authenticate(username=supplied_username, password=supplied_password)
        
        formset = LoginForm(initial={'username': supplied_username})
        c = {}
        c.update(csrf(request))
        c.update({'formset': formset})
        
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return redirect(reverse('user_home', args=[user.username]))
            else:
                return render_to_response('login.html', c)
        else:
            return render_to_response('login.html', c)

def process_logout(request):
    """The logout handler"""
    
    if request.user.is_authenticated():
        auth.logout(request)
    
    return redirect(reverse('welcome'))