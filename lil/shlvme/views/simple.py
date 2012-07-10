from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

"""
If it's a simple view, let's put it here
"""

def privacy(request):
    """The application-wide privacy policy page."""
    return render_to_response('privacy.html', {'user': request.user})
