from django.shortcuts import render_to_response


"""
If it's a simple view, let's put it here
"""

def not_found(request):
    """The application-wide 404 page."""
    return render_to_response('404.html', {'user': request.user})

def about(request):
    """The application-wide about page."""
    return render_to_response('about.html', {'user': request.user})

def privacy(request):
    """The application-wide privacy policy page."""
    return render_to_response('privacy.html', {'user': request.user})

def bookmark(request):
    """The application-wide bookmark page."""
    return render_to_response('bookmark.html', {'user': request.user})

def faq(request):
    """The application-wide FAQ page."""
    return render_to_response('faq.html', {'user': request.user})

def search(request):
    """The application-wide search page."""
    return render_to_response('search.html', {'user': request.user})