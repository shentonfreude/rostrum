
import logging
import time
import json
from collections import OrderedDict
import csv

from django.core.context_processors import csrf
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import Form, CharField, FileField, DateField, ModelMultipleChoiceField
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


def _mogrify(txt):
    """Transform label names to be pythonic attribute-friendly.
    """
    return txt.lower().replace(" - ", "_").replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace(".", "")


def _csv_to_db(csvfile):
    App.objects.all().delete()      # DANGER: Delete existing apps info
    reader = csv.DictReader(csvfile)
    num_apps = 0
    warnings = []
    infos = []
    for rid, row in enumerate(reader):
        acronym = row['Acronym'].strip()
        version = row['Version Number'].strip()
        if acronym == '':
            msg = "Ignoring row=%d without Acronym" % rid
            warnings.append(msg)
            logging.warning(msg)
            continue
        if len(acronym) < 2:
            msg = "Ignoring row=%d with too-short Acronym=%s" % (rid, acronym)
            warnings.append(msg)
            logging.warning(msg)
            continue
        existing = App.objects.filter(acronym__iexact=acronym, version_number=version)
        if existing:
            msg = "Ignoring extant acronym=%s version=%s" % (acronym, version)
            warnigns.append(msg)
            logging.warning(msg)
            continue
        app = App()
        app.save()                  # save for M2M
        for k, v in row.items():
            v = v.strip()
            if not v:           # don't store empty values
                continue
            # MAYBE TODO: filter nulls from M2M, check nullish
            # MAYBE TODO: transform Date, Time, Boolean, Integer
            try:
                setattr(app, _mogrify(k), v)
            except (TypeError, ValidationError), e:
                logging.error("SETATTR: %s", e)
                import pdb; pdb.set_trace()
        try:
            app.save()
        except (TypeError, ValidationError), e:
                logging.error("SAVE: %s", e)
                import pdb; pdb.set_trace()
        msg = "Row=%d App=%d: %s %s" % (rid, num_apps, acronym, version)
        infos.append(msg)
        logging.info(msg)
        num_apps += 1
    return {'warnings': warnings, 'infos': infos}

class UploadCsvForm(Form):
    file = FileField()

def uploadcsv(request):
    """Upload a CSV file exported from spreadsheet, parse into DB.
    """
    if request.method == 'POST':
        form = UploadCsvForm(request.POST, request.FILES)
        if form.is_valid():
            res = _csv_to_db(request.FILES['file'])
            return render_to_response('app/uploadcsv.html',
                                      {'warnings': res['warnings'],
                                       'infos': res['infos'],
                                       },
                                      context_instance=RequestContext(request));
    else:
        form = UploadCsvForm()
    return render_to_response('app/uploadcsv.html',
                              {'form': form},
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


