from django.shortcuts import render_to_response
from django.template import RequestContext

from app.views import _search_suggestions

def home(request):
    """Show Hero logo and provide a search box for convenience.
    """
    return render_to_response('home.html',
                              {'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def about(request):
    """Show About info and What's New.
    """
    return render_to_response('about.html',
                              {'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

