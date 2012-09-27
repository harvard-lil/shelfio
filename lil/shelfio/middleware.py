# Takes POSTS with a "_method" parameter and changes the request method to match.
# Concept borrowed from the node.js Connect middleware by the same name.
class MethodOverrideMiddleware(object):
    def process_request(self, request):
        request.rfc5789_method = {}
        if '_method' in request.POST.keys():
            request.rfc5789_method = request.POST['_method'].upper()

        # Toss in support for HTTP_X_METHODOVERRIDE, see http://pdobson.com/post/18362073678/post-tunneling-http-delete-and-put-requests-with

        return None
    
class OAuthMiddleware(object):
    def process_request(self, request):
        """Look for an OAuth token in the header and then in the params. HTTP params take priority over headers.
        If we find it, attach it to the request object"""

        token = ''
               
        # Check the header
        if 'HTTP_AUTHORIZATION' in request.META:
            token_in_header = request.META['HTTP_AUTHORIZATION']
            auth_type, auth_value = token_in_header.split(' ')
            if auth_type == 'token':
                token = auth_value
        
        # Check the params  
        if 'access_token' in request.GET.keys():
            token = request.GET['access_token'].upper()
        elif 'access_token' in request.POST.keys():
            token = request.POST['access_token'].upper()
        
        
        if token:
            request.oauth_token = token
        
        return None