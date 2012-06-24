import csv
import json
import logging
import time
import datetime
from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import Form, CharField, FileField
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from models import App

logging.basicConfig(level=logging.INFO)

# Spreadsheet-to-DB field map generated from import and _mogrify on imported CSV
# Capture it here so we can map faster on import, validate field names,
# and export as CSV with original field names.

MOGRIFIELDS = OrderedDict(
    [#('No.', 'no'),
     ('Acronym', 'acronym'),
     ('Acronym - Previous', 'acronym_previous'),
     ('Version Number', 'version_number'),
     ('Version Number - Previous', 'version_number_previous'),
     ('Name', 'name'),
     ('Name - Previous', 'name_previous'),
     ('Description', 'description'),
     ('Description - Previous', 'description_previous'),
     ('Support Class', 'support_class'),
     ('Support Class - Previous', 'support_class_previous'),
     ('Application Type', 'application_type'),
     ('Application Type - Previous', 'application_type_previous'),
     ('Software Class', 'software_class'),
     ('Software Class - Previous', 'software_class_previous'),
     ('User Groups', 'user_groups'),
     ('User Groups - Previous', 'user_groups_previous'),
     ('Number of Users', 'number_of_users'),
     ('Number of Users - Previous', 'number_of_users_previous'),
     ('Version Status', 'version_status'),
     ('Version Status - Previous', 'version_status_previous'),
     ('Version Change Description', 'version_change_description'),
     ('Version Change Description - Previous',
      'version_change_description_previous'),
     ('Service Request Numbers', 'service_request_numbers'),
     ('Service Request Numbers - Previous', 'service_request_numbers_previous'),
     ('Service Request Class(s)', 'service_request_classs'),
     ('Service Request Class(s) - Previous', 'service_request_classs_previous'),
     ('HITSS Supported', 'hitss_supported'),
     ('HITSS Supported - Previous', 'hitss_supported_previous'),
     ('Project Manager Name', 'project_manager_name'),
     ('Project Manager Name - Previous', 'project_manager_name_previous'),
     ('Data Impact Type', 'data_impact_type'),
     ('Data Impact Type - Previous', 'data_impact_type_previous'),
     ('FIPS Information Category', 'fips_information_category'),
     ('FIPS Information Category - Previous',
      'fips_information_category_previous'),
     ('Compliance - 508', 'compliance_508'),
     ('Compliance - 508 - Previous', 'compliance_508_previous'),
     ('Internal or External System', 'internal_or_external_system'),
     ('Internal or External System - Previous',
      'internal_or_external_system_previous'),
     ('Security Plan Number', 'security_plan_number'),
     ('Security Plan Number - Previous', 'security_plan_number_previous'),
     ('URL Link', 'url_link'),
     ('URL Link - Previous', 'url_link_previous'),
     ('Architecture Type', 'architecture_type'),
     ('Architecture Type - Previous', 'architecture_type_previous'),
     ('DBMS Names and Version', 'dbms_names_and_version'),
     ('DBMS Names and Version - Previous', 'dbms_names_and_version_previous'),
     ('Software Names and Versions', 'software_names_and_versions'),
     ('Software Names and Versions - Previous',
      'software_names_and_versions_previous'),
     ('Servers - Application', 'servers_application'),
     ('Servers - Application - Previous', 'servers_application_previous'),
     ('Servers - Database', 'servers_database'),
     ('Servers - Database - Previous', 'servers_database_previous'),
     ('Servers - Report', 'servers_report'),
     ('Servers - Report - Previous', 'servers_report_previous'),
     ('Servers Location', 'servers_location'),
     ('Servers Location - Previous', 'servers_location_previous'),
     ('Network Services Used', 'network_services_used'),
     ('Network Services Used - Previous', 'network_services_used_previous'),
     ('Interface Acronym', 'interface_acronym'),
     ('Interface Acronym - Previous', 'interface_acronym_previous'),
     ('Interface Direction', 'interface_direction'),
     ('Interface Direction - Previous', 'interface_direction_previous'),
     ('Interface Method', 'interface_method'),
     ('Interface Method - Previous', 'interface_method_previous'),
     ('Comments', 'comments'),
     ])

def overview(request, acronym=None):
    """List of all apps and a few attributes, allowing drill-down.
    """
    # TODO? alphabin them
    apps = App.objects.values('id', 'acronym', 'version_number',
                              'name', 'description',
                              'architecture_type', 'number_of_users',
                              'service_request_numbers',
                              'project_manager_name').order_by('acronym').distinct()
    return render_to_response('app/overview.html',
                              {'apps': apps,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def details(request, id):
    """Return full application attrs.
    """
    app = App.objects.get(pk=id)
    return render_to_response('app/details.html',
                              {'app': app,
                               'edit_url': reverse('admin:app_app_change', args=(id,)),
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
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def compliance(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/compliance.html',
                              {'apps': apps,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def description(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/description.html',
                              {'apps': apps,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def technical(request):
    # TODO? alphabin them
    apps = App.objects.all().order_by('acronym').distinct()
    return render_to_response('app/technical.html',
                              {'apps': apps,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

# Import/Export CSV

def _mogrify(txt):
    """Transform label names to be pythonic attribute-friendly.
    """
    return txt.lower().replace(" - ", "_").replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace(".", "")


def _csv_to_db(csvfile):
    """Read a CSV file and create App models from row/fields.
    Store empty values as '' to avoid storing None which renders
    ugly in template and cannot be unicoded on export.
    We are not doing smart things like foreign keys to controlled vocabulary tables,
    nor converting string values to Integer, Boolean, Date, etc.
    """
    num_apps = 0
    warnings = []
    infos = []
    App.objects.all().delete()      # DANGER: Delete existing apps info
    reader = csv.DictReader(csvfile)
    for field in reader.fieldnames:
        if field not in MOGRIFIELDS.keys():
            msg = "Ignoring unrecognized field name '%s' for all rows in CSV" % field
            warnings.append(msg)
            logging.warning(msg)
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
        app.save()              # save for M2M
        for k, v in row.items():
            if k not in MOGRIFIELDS.keys():
                continue        # ignore unrecognized field names 
            v = v.strip()
            try:
                setattr(app, MOGRIFIELDS[k], v)
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

@login_required()
def uploadcsv(request):
    """Upload a CSV file exported from spreadsheet, parse into DB.
    """
    if request.method == 'POST':
        logging.info("UPLOAD encoding=%s" % request.encoding)
        form = UploadCsvForm(request.POST, request.FILES)
        if form.is_valid():
            res = _csv_to_db(request.FILES['file'])
            return render_to_response('app/uploadcsv.html',
                                      {'warnings': res['warnings'],
                                       'infos': res['infos'],
                                       'search_suggestions': _search_suggestions(),
                                       },
                                      context_instance=RequestContext(request));
    else:
        form = UploadCsvForm()
    return render_to_response('app/uploadcsv.html',
                              {'form': form,
                               'search_suggestions': _search_suggestions(),
                               },
                              context_instance=RequestContext(request));

def downloadcsv(request):
    """Create a CSV file and download it.
    Avoid creating a file in memory.
    """
    logging.info("dialects: %s" % csv.list_dialects())
    # TODO: what encoding? utf-8 seems likely
    fname = "rostrum-%s" % datetime.datetime.now().isoformat()[:19]
    response = HttpResponse(mimetype='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="%s"' % fname
    writer = csv.writer(response)
    writer.writerow(MOGRIFIELDS.keys()) # first row is original headers and order
    apps = App.objects.all()
    for app in apps:
        row = [getattr(app, v, u'').encode("utf-8") for v in MOGRIFIELDS.values()] # put fields in original order
        writer.writerow(row)
    return response


# Search

class SearchForm(Form):
    text = CharField(max_length=80, required=True)

def _search_suggestions():      # TODO: memoize this
    """Provide suggestions to the search box.
    Takes 0.003 seconds for this query and reduction.
    TODO: provide this on *every* view since the box is there.
    How to pull this request from Django template?
    """
    now = time.time()
    words_q = App.objects.values('acronym',
                                 'name',
                                 'project_manager_name',
                                 ).distinct()
    wordset = set()
    for worddict in words_q:
        vals = worddict.values()
        for val in vals:
            wordset.add(val)
    words = [word for word in wordset if word]
    words.sort()
    logging.info("search_suggestions len=%d time=%f" % (len(words), time.time() - now))
    return json.dumps(words)

def search(request):
    """Search common fields for substring match: acronym, name, project_manager
    We don't handle GET because our search is a mini-form on most pages.
    If we get a bad query (e.g., empty) return to where we came from.
    """
    if request.method == 'POST':
        form = SearchForm(data=request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            q = Q(acronym__icontains=text)
            q = q | Q(name__icontains=text)
            q = q | Q(project_manager_name__icontains=text)
            apps = App.objects.filter(q).order_by('acronym')
            return render_to_response('app/search_results.html',
                                      {'apps': apps,
                                       'search_suggestions': _search_suggestions(),
                                       },
                                      context_instance=RequestContext(request));
        else:
            return redirect(request.META['HTTP_REFERER'])
