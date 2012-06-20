
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
    # Query Application.objects.prefetch_related('app_status').\
    #    values_list('acronym', flat=True).distinct().order_by('acronym') 
    # took 5.2 seconds.
    # Query attrs we want and reducing with dicts takes 0.03 seconds, 173x speedup. :-)
    logging.warning("overview acronym=%s" % acronym)
    if not acronym:
        apps = App.objects.values('acronym', 'version_number', 'name', 'description', 'id').order_by('acronym').distinct()
        return render_to_response('app/overview.html',
                                  {'apps': apps,
                                   'bootstrap_label': BOOTSTRAP_LABEL,
                                   'search_suggestions': _search_suggestions(),
                                   },
                                  context_instance=RequestContext(request));
    apps = App.objects.filter(acronym__iexact=acronym).order_by('acronym', 'version_number')
    return render_to_response('application/search_results.html',
                              {'object_list': apps,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def details(request, id):
    """Return full application.
    Also show all other release versions for context.
    """
    app = App.objects.get(pk=id)
    # app_class = BOOTSTRAP_LABEL.get(app.app_status.all()[0].name, '') # all()[0] for bogus M2M
    # rels = Application.objects.filter(acronym=app.acronym).values('id', 'release', 'app_status__name').order_by('release').distinct() # worthless 'distinct'
    # releases = []
    # Is there a away to do this to 'rels' in place, or with a comprehension?
    # for rel in rels:
    #     rel.update({'app_class': BOOTSTRAP_LABEL.get(rel.pop('app_status__name'))})
    #     releases.append(rel)
    return render_to_response('app/details.html',
                              {'app': app,
                               # 'app_class': app_class,
                               # 'releases': releases,
                               'bootstrap_label': BOOTSTRAP_LABEL,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));



# def list_apps(request):
#     return render_to_response('list_apps.html',
#                               {'apps': Application.objects.all().order_by('acronym', 'release'),
#                                },
#                               context_instance=RequestContext(request));

# def application_versions(request):
#     """Return sorted list of Arco and Versions
#     ['Acro': [<appv1>, <appv2>, ...], 'Zeta':[<apps>...]]
#     Render like:
#     BESS  1.1, 1.2, 2.1
#     CATS  2.0, 2.3, 2.4
#     alphabin={'A' : [{'AIIS': {'id': 1, 'release': '3.14', app_status__name='Prior'},
#                               {'id': 2, 'release': '3.15', app_status__name='Current'},
#                       'ARDVARK' : ...,
#                      }],
#               'B' : ...}
#     Doing query for acros, then queries for release status,
#     without prefetch: 2.7 seconds, with: 1.8
#     Doing a single limited query of just the attrs we need: 0.05 seconds.
#     """
#     # Why is this getting a single app_status since it's M2M currently?
#     apps = Application.objects.values('id', 'acronym', 'release', 'app_status__name').order_by('acronym', 'release')
#     acro_vers = OrderedDict()
#     for app in apps:
#         acro = app.pop('acronym')
#         if not acro in acro_vers:
#             acro_vers[acro] = []
#         app['app_class'] = BOOTSTRAP_LABEL.get(app.pop('app_status__name'), '')
#         acro_vers[acro].append(app)
#     alphabin = OrderedDict()
#     for acro, releases in acro_vers.items():
#         c = acro[0].upper()
#         if c not in alphabin:
#             alphabin[c] = []
#         alphabin[c].append((acro, releases))
#     return render_to_response('application/application_versions.html',
#                               {'bootstrap_label': BOOTSTRAP_LABEL,
#                                'alphabin': alphabin,
#                                'search_suggestions': _search_suggestions(),
#                                },
#                               context_instance=RequestContext(request));


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


# def report(request):
#     """Show page offering different reports. Boring.
#     """
#     return render_to_response('application/report.html',
#                               {'search_suggestions': _search_suggestions(),
#                                },
#                               context_instance=RequestContext(request));

# def report_current(request):
#     """Show page offering different reports. Boring.
#     """
#     apps = Application.objects.filter(app_status__name__icontains='Current').order_by('acronym', 'release')
#     return render_to_response('application/search_results.html',
#                               {'object_list': apps,
#                                'search_suggestions': _search_suggestions(),
#                                },
#                               context_instance=RequestContext(request));

# def report_development(request):
#     """Show page offering different reports. Boring.
#     """
#     apps = Application.objects.filter(app_status__name__icontains='Development').order_by('acronym', 'release')
#     return render_to_response('application/search_results.html',
#                               {'object_list': apps,
#                                'search_suggestions': _search_suggestions(),
#                                },
#                               context_instance=RequestContext(request));

# def report_development(request):
#     """Actual, Projected, In-Suspense and TBD [wtf?]"
#     rel date, release, acro, sr#, org acro, nasa requester, change description
#     TODO: don't understand the status selection meanings above. Our choices:
#     Cancelled, Archived, Prior Version, Current Version, Moved, Inactive,
#     Roll Back, In Suspense, Unassigned, In Development.
#     """
#     q =     Q(app_status__name__iequals='Current Version') # actual?
#     q = q | Q(app_status__name__iequals='In Development')  # projected?
#     q = q | Q(app_status__name__iequals='In Suspense')     # supense
#     q = q | Q(app_status__name__iequals='Unassigned')      # TBD?
#     apps = Application.objects.filter(q).values('release_date', 'release', 'acronym', 'sr_number', 'owner_org', 'nasa_requester', 'release_change_description', 'app_status__name').order_by('release_date', 'acronym', 'release')
#     return render_to_response('report/app_pipeline_abbrev.html',
#                               {'object_list': apps,
#                                'search_suggestions': _search_suggestions(),
#                                },
#                               context_instance=RequestContext(request));

