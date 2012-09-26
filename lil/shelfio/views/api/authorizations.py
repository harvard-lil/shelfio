import json
import logging
import base64

from lil.shelfio.models import AuthTokens

from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

try:
    from lil.shelfio.local_settings import *
except ImportError, e:
    logger.error('Unable to load local_settings.py:', e)

@csrf_exempt
def api_tokens(request):
    """create and get a user's authorizations here 
    """

    if not request.user.is_authenticated():
        # Is the user logged in, if not, let's try HTTP BASIC AUTH
        if _auth_using_basic_auth(request) == False:
            return HttpResponse('You need to authenticate to connect to this resource', status=401)

    
    if request.method == 'GET':
        # Get all tokens owned by the authenticated user
        serialized = get_and_serialize_tokens(request.user)
        
        return HttpResponse(json.dumps(serialized, cls=DjangoJSONEncoder), mimetype='application/json', )

    elif request.method == 'POST':
        # Create a new token and return it
        auth_token = AuthTokens(user=request.user)
        if request.POST.get('notes'):
            auth_token.notes = request.POST.get('notes')
        auth_token.save()
        
        serialized = serialize_token(auth_token)

        return HttpResponse(json.dumps(serialized, cls=DjangoJSONEncoder), mimetype='application/json', )

    return HttpResponseNotAllowed(['POST', 'GET'])

@csrf_exempt
def api_one_token(request, token): 
    """A single resource is supplied. Return it or delete depending on the request type"""

    if not request.user.is_authenticated():
        # Is the user logged in, if not, let's try HTTP BASIC AUTH
        if _auth_using_basic_auth(request) == False:
            return HttpResponse('You need to authenticate to connect to this resource', status=401)

    if request.method == 'GET':
        auth_token = get_object_or_404(AuthTokens, user=request.user, token=token)
        serialized = serialize_token(auth_token)
        
        return HttpResponse(json.dumps(serialized, cls=DjangoJSONEncoder), mimetype='application/json', )
    
    elif request.rfc5789_method == 'DELETE':
        auth_token = get_object_or_404(AuthTokens, user=request.user, token=token)
        auth_token.delete()
        
        return HttpResponse(status=204)

    return HttpResponseNotAllowed(['DELETE', 'GET'])

def _auth_using_basic_auth(request):
    """If we have basic authentication in the request"""
    if 'HTTP_AUTHORIZATION' in request.META:
        auth_header = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth_header) == 2:
            if auth_header[0].lower() == "basic":
                uname, passwd = base64.b64decode(auth_header[1]).split(':')
                user = auth.authenticate(username=uname, password=passwd)
                
                if user is not None and user.is_active:
                        auth.login(request, user)
                        request.user = user
                        return True
    return False
                    

def serialize_token(token):
    """Take a single token and serialize it"""
    serialized_token = {}
    serialized_token['token'] = str(token.token)
    if token.notes:
        serialized_token['notes'] = token.notes
    
    return {
        'docs': serialized_token,
        'num_found': 1
    }    
                
def get_and_serialize_tokens(user):
    """Take a user, get that user's auth tokens, and serialize"""
    auth_tokens = AuthTokens.objects.filter(user=user).filter(is_active=True)
    
    token_list = []
    for token in auth_tokens:
        serialized_token = {}
        serialized_token['token'] = str(token.token)
        if token.notes:
            serialized_token['notes'] = token.notes
        token_list.append(serialized_token)
    
    return {
        'docs': token_list,
        'num_found': len(token_list)
    }    