#!/usr/bin/env python

# Import ROSA/STRAW data from CSV export with column labels.
# Get filename from command line's first (only) argument

# Dir: /Users/cshenton/Projects/core/rostrum/rostrum
# export DJANGO_SETTINGS_MODULE=settings
# ./importcsv.py

import sys
import csv
import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import FieldDoesNotExist

from app.models import App

# UNUSED_FIELDS = (
#     'no',
#     )

# NULLISH_VALUES = (
#     None,
#     [],
#     '',
#     'Unassigned',
#     'Unk',
#     'Unknown',
#     'Not Applicable',
# )

# DATE_FIELDS = ('release_date', 'cm_resubmit_date') # have to transform on load

# TIME_FIELDS = ('cm_entered_time', 're_entered_time') # have to transform on load

# INTEGER_FIELDS = ('app_users_num',)

# BOOLEAN_FIELDS = (
#     'awrs_checklist',
#     )

# def _booleanize(val):
#     """Return True/False based on text.
#     """
#     return val.lower() in ('yes', 'true', 'y')

# def get_fk(model, name):
#     """Find name in model, if not there, create it. Return key.
#     use: get_fk(OrganizationalAcronym, row['nasa_owner_office_id'])
#     CAVEAT: this will pollute our DB with useless "Unspecified" and "UNSPECIFIED"
#     types of entries. Maybe we can defend against these specific words?
#     """
#     try:
#         item = model.objects.get(name=name)
#     except model.DoesNotExist:
#         item = model(name=name)
#         item.save()
#         logging.info("CREATE model=%s name=%s" % (model, name))
#     return item

def mogrify(txt):
    """Transform label names to be pythonic attribute-friendly.
    """
    return txt.lower().replace(" - ", "_").replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "").replace(".", "")


#model = models.get_model('app', 'App') # UNUSED??

def csv_to_db(csvfile):
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
                setattr(app, mogrify(k), v)
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

with open(sys.argv[1], 'rb') as csvfile:
    csv_to_db(csvfile)


