from urlparse import parse_qs

# Takes POSTS with a "_method" parameter and changes the request method to match.
# Concept borrowed from the node.js Connect middleware by the same name.
class MethodOverrideMiddleware(object):
    def process_request(self, request):
        request.rfc5789_method = {}
        if '_method' in request.POST.keys():
            request.rfc5789_method = request.POST['_method'].upper()

        return None