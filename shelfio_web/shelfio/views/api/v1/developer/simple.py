from django.shortcuts import render_to_response


"""
If it's a simple developer view, let's put it here
"""

def intro_and_common(request):
    """The introductiona to the api and its common pieces"""
    return render_to_response('developer/intro.html', {'user': request.user})

def item(request):
    """Details on the item api."""
    return render_to_response('about.html', {'user': request.user})

def shelf(request):
    """Details on the shelf api."""
    return render_to_response('privacy.html', {'user': request.user})

def user(request):
    """Details on the user api."""
    return render_to_response('bookmark.html', {'user': request.user})

def favorites(request):
    """Details on the favorites api."""
    return render_to_response('faq.html', {'user': request.user})

def authorizations(request):
    """Details on the authorizations api."""
    return render_to_response('search.html', {'user': request.user})