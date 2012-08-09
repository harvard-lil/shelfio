from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

def about(request):
    """The application-wide about page."""
    return render_to_response('about.html', {'user': request.user})
