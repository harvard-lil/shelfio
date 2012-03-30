from urlparse import parse_qs

# Takes POSTS with a "_method" parameter and changes the request method to match.
# Concept borrowed from the node.js Connect middleware by the same name.
class MethodOverrideMiddleware(object):
    def process_request(self, request):
        if '_method' in request.POST.keys():
            request.method = request.POST['_method'].upper()
        request.originalMethod = request.method
        return None