
import logging
import time
import json
from collections import OrderedDict

from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import Form, CharField, DateField, ModelMultipleChoiceField
from django.forms import SelectMultiple
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from models import App

logging.basicConfig(level=logging.INFO)


class SearchForm(Form):
    text   = CharField(max_length=80, required=True)

BOOTSTRAP_LABEL = {                                # underscore names for template access
    "Archived"          : "label",                 # gray
    "Cancelled"         : "label label-inverse",   # black
    "Current Version"   : "label label-success",   # green
    "Current_Version"   : "label label-success",   # green
    "In Development"    : "label label-info",      # blue
    "In_Development"    : "label label-info",      # blue
    "In Suspense"       : "label label-important", # red
    "In_Suspense"       : "label label-important", # red
    "Inactive"          : "",
    "Moved"             : "",
    "Prior Version"     : "",
    "Prior_Version"     : "",
    "Roll Back"         : "",
    "Roll_Back"         : "",
    "Unassigned"        : "label label-warning",   # yellow
}

###############################################################################
# Attributes

# acronym
# acronym_previous
# application_type
# application_type_previous
# architecture_type
# architecture_type_previous
# comments
# compliance_508
# compliance_508_previous
# data_impact_type
# data_impact_type_previous
# dbms_names_and_version
# dbms_names_and_version_previous
# description
# description_previous
# fips_information_category
# fips_information_category_previous
# hitss_supported
# hitss_supported_previous
# id
# interface_acronym
# interface_acronym_previous
# interface_direction
# interface_direction_previous
# interface_method
# interface_method_previous
# internal_or_external_system
# internal_or_external_system_previous
# name
# name_previous
# network_services_used
# network_services_used_previous
# number_of_users
# number_of_users_previous
# project_manager_name
# project_manager_name_previous
# security_plan_number
# security_plan_number_previous
# servers_application
# servers_application_previous
# servers_database
# servers_database_previous
# servers_location
# servers_location_previous
# servers_report
# servers_report_previous
# service_request_classs
# service_request_classs_previous
# service_request_numbers
# service_request_numbers_previous
# software_class
# software_class_previous
# software_names_and_versions
# software_names_and_versions_previous
# support_class
# support_class_previous
# url_link
# url_link_previous
# user_groups
# user_groups_previous
# version_change_description
# version_change_description_previous
# version_number
# version_number_previous
# version_status
# version_status_previous

# BUG? Now 'owner' info in DB? 

# TODO: memoize this
def _search_suggestions():
    """Provide suggestions to the search box.
    Takes 0.06 seconds for this query and reduction.
    TODO: provide this on *every* view since the box is there.
    How to pull this request from Django template?
    """
    now = time.time()
    words_q = App.objects.values('acronym',
                                 'name', 'project_manager_name',
                                 ).distinct()
                                         # 'owner', 'owner_org',
                                         # 'nasa_off_name', 'nasa_requester',
                                         # 'manager_app_development', 'manager_project',
                                         # 'dev_name_primary', 'dev_name_alternate').distinct()
    wordset = set()
    for worddict in words_q:
        vals = worddict.values()
        for val in vals:
            wordset.add(val)
    words = [word for word in wordset if word]
    words.sort()
    logging.info("search_suggestions len=%d time=%f" % (len(words), time.time() - now))
    return json.dumps(words)


def overview(request, acronym=None):
    # TODO? alphabin them
    apps = App.objects.values('id', 'acronym', 'version_number',
                              'name', 'description',
                              'architecture_type', 'number_of_users',
                              'service_request_numbers',
                              'project_manager_name').order_by('acronym').distinct()
    return render_to_response('app/overview.html',
                              {'apps': apps,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def details(request, id):
    """Return full application attrs.
    """
    app = App.objects.get(pk=id)
    return render_to_response('app/details.html',
                              {'app': app,
                               # 'app_class': app_class,
                               # 'releases': releases,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

# For category views, get all attrs for all apps, render to specific templates.
# Less effiencient perhaps but easier coding, especially with _previous vals

def administrative(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/administrative.html',
                              {'apps': apps,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def compliance(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/compliance.html',
                              {'apps': apps,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def description(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/description.html',
                              {'apps': apps,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def technical(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/technical.html',
                              {'apps': apps,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));



# def search(request):
#     """Search common fields for substring match:
#     acronym, name, description, ...
#     TODO: We should match what ROSA does, even if it's dumb.
#     """
#     if request.method == 'POST':
#         form = SearchForm(data=request.POST)
#         if form.is_valid():
#             text = form.cleaned_data['text']
#             q = Q(acronym__icontains=text)
#             q = q | Q(app_name__icontains=text)
#             q = q | Q(description__icontains=text)
#             q = q | Q(owner__icontains=text)
#             q = q | Q(owner_org__icontains=text)
#             q = q | Q(nasa_off_name__icontains=text)
#             q = q | Q(nasa_requester__icontains=text)
#             q = q | Q(manager_app_development__icontains=text)
#             q = q | Q(manager_project__icontains=text)
#             q = q | Q(dev_name_primary__icontains=text)
#             q = q | Q(dev_name_alternate__icontains=text)
#             apps = Application.objects.filter(q).order_by('acronym', 'release')
#             return render_to_response('application/search_results.html',
#                                       {'object_list': apps,
#                                        'bootstrap_label': BOOTSTRAP_LABEL,
#                                        'search_suggestions': _search_suggestions(),
#                                        },
#                                       context_instance=RequestContext(request));
#     else:
#         form = SearchForm()
#     return render_to_response('application/search.html',
#                               {'form': form,
#                                'search_suggestions': _search_suggestions(),
#                                },
#                               context_instance=RequestContext(request));


