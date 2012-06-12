from django.contrib.auth.forms import UserCreationForm
from django.http import  HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import auth

# TODO: replace this registration method with the django auth one (but make sure we're not doing the email activation bullshit) 

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