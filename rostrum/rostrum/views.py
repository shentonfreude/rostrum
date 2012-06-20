import logging

from collections import OrderedDict

from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import Form, CharField, DateField, ModelMultipleChoiceField
from django.forms import SelectMultiple
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

#from application.models import Application
#from application.views import _search_suggestions

logging.basicConfig(level=logging.INFO)

def home(request):
    """Show Hero logo and provide a search box for convenience.
    """
    return render_to_response('home.html',
                              # {'search_suggestions': _search_suggestions(),
                              #  },
                              context_instance=RequestContext(request));

def about(request):
    """Show About info and What's New.
    """
    return render_to_response('about.html',
                              # {'search_suggestions': _search_suggestions(),
                              #  },
                              context_instance=RequestContext(request));

