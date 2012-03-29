from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render_to_response, get_object_or_404
from django.core.urlresolvers import reverse
from lil.shlvme.models import LoginForm
from django.core.context_processors import csrf
from django.contrib import auth, messages

# TODO: a lot of the auth/auth functionality is crude. cleanup.

def process_register(request):
    """Register a new user"""
    c = {}
    c.update(csrf(request))

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
            c.update({'form': form})
            return render_to_response('register.html', c)
    else:
        form = UserCreationForm()
        c.update({'form': form})
        return render_to_response("register.html", c)


def process_login(request):
    """The login handler"""
    
    # If we get a GET, send the login form
    if request.method == 'GET':
        if not request.user.is_authenticated():
            formset = LoginForm()
            
            c = {
                'formset': formset,
                'messages': messages.get_messages(request)
            }
            c.update(csrf(request))
            return render_to_response('login.html', c)
        else:
            return redirect(reverse('welcome'))

    # If we get a POST, someone has filled out the login form
    if request.method == 'POST':
        formset= LoginForm(request.POST)
        c = {}
        c.update(csrf(request))

        if formset.is_valid():
            supplied_username = formset.cleaned_data['username']
            supplied_password = formset.cleaned_data['password']    
            user = auth.authenticate(username=supplied_username, password=supplied_password)
            c.update({'formset': formset})
            
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return redirect(reverse('user_home', args=[user.username]))
                else:
                    messages.error(request, 'This account is inactive.')
            else:
                messages.error(request, 'Login failed. Please check your username and password.')
            c.update({'messages': messages.get_messages(request)})
        
        c.update({'formset': formset})
        return render_to_response('login.html', c)

def process_logout(request):
    """The logout handler"""
    
    if request.user.is_authenticated():
        auth.logout(request)
    
    return redirect(reverse('welcome'))