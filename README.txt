=========
 ROSTRAW
=========

Visualize data extracted from ROSA and updated.

Only current version information is included.

About 66 attributes.
Some attributes record previous values, and will be labeled with "*-previous" column name.

Categories
==========

Administrative
Compliance
Descriptive
Technical

See the Crosswalk spread for which attrs fall into which categories. 

Proposed Application
====================

Import
------

Since the spread is the canonical data source, export data as CSV.

Upload into new app, parse into DB based on field names.

App View
--------

1. List of apps: click gives Detail view
2. Detail: app attributes like my ROSA but with the 4 categories and their attributes
3. Per Category: table view, one for each Category, showing its details as column heads

When we have a "*-preview" data associated, show the new and prev with some highlighting to call attention.

Edit/Export
-----------

None. It's not possible to maintain canonical data in both a CSV and application.

If the app's visualization shows data should be changed, fix the
canonical spreadsheet, then re-export and import into the app.

If we have time, perhaps we can make an editing interface, but then
we're creating ROSA again, which we're told is something that now
should be done in Rational.

