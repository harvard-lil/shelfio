from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

def not_found(request):
    """The application-wide 404 page."""
    return render_to_response('404.html', {'user': request.user})