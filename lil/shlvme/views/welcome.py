from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

def welcome(request):
    """The application-wide welcome page."""
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('user_home', args=[request.user.username]))
    else:
        return render_to_response('index.html', {'user': request.user})