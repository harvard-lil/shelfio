from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse

def faq(request):
    """The application-wide FAQ page."""
    return render_to_response('faq.html', {'user': request.user})
