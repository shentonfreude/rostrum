import csv
import json
import logging
import time

from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.forms import Form, CharField, FileField
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

from models import App

logging.basicConfig(level=logging.INFO)


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
    We are not doing smart things like foreign keys to controlled vocabulary tables,
    nor converting string values to Integer, Boolean, Date, etc.
    """
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
        app.save()              # save for M2M
        for k, v in row.items():
            v = v.strip()
            if not v:           # don't store empty values
                continue
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
