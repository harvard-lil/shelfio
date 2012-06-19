from django.http import  HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib import auth
from lil.shlvme.models import Shelf, UserCreationFormWithEmail

# TODO: replace this registration method with the django auth one (but make sure we're not doing the email activation bullshit) 

def process_register(request):
    """Register a new user"""
    c = {}
    c.update(csrf(request))

    if request.method == 'POST':
        form = UserCreationFormWithEmail(request.POST)
        if form.is_valid():
            new_user = form.save()
            # Create a default shelf for the user
            shelf = Shelf(
                    user= new_user,
                    name='Misc',
                    description= "%s's miscellaneous shelf" % new_user.username,
                    is_private=False,
                )
            shelf.save()
            
            # Log the user in
            supplied_username = request.POST.get('username', '')
            supplied_password = request.POST.get('password1', '')
            user = auth.authenticate(username=supplied_username, password=supplied_password)
            auth.login(request, user)
            
            return HttpResponseRedirect(reverse('user_home', args=[user.username]))
        else:
            c.update({'form': form})
            return render_to_response('register.html', c)
    else:
        form = UserCreationFormWithEmail()
        c.update({'form': form})
        return render_to_response("register.html", c)