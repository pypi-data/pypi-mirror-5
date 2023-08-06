dj-timelinejs
=============

Support for [TimelineJS](http://timeline.verite.co/) served through Django.

##Features

* Support for TimelineJS title, era and normal slides
* Support for markdown in slide content
* Media upload and storage on Django site
* Import existing TimelineJS Google Spreadsheets
* Private/Public and Published/Unpublished timeline states

##Basic Usage

This package supplies Django models and Class-Based-Views which make it easy to
save and serve up TimelineJS content from a Django site

###Brief Installation Instructions

1. pip install dj-timelinejs
2. add `timelinejs` to your list of `INSTALLED_APPS` in `settings.py`
3. `manage.py syncdb`
4. Override urls and templates as noted below.

###Adding Timelines

This package supports two storage methods for Timelines.

The preferred method is to store the timeline data directly in your Django
site. You may do this through the admin interface by creating a Timeline object
in the Timelinejs admin panel. Timeline items are added through this same
interface. Item content can use markdown syntax for formatting. Media can added
and it will be uploaded and serverd through your site, meaning users do not
need to find a way to host and link their media.

The second method is to use the Google Spreadsheet template as documented at
[http://timeline.verite.co/#make](http://timeline.verite.co/#make) and simply
set the `data_source` attribute on your Timeline instance to the url for the
spreadsheet as indicated in the TimelineJS documentation. This is not preferred
as markdown syntax is not implemented and loading a timeline will require an
additional request to fetch data from the Google Spreadsheet.


If you have existing timelines in Google Spreadsheets you may import them using
the `ImportTimelineFromSpreadsheet` view. Input the url of the Google
Spreadsheet and valid items will be imported into the database and a new
timeline created.

###Overriding URLS and Templates

You probably want to do your own url and template configuration. Class-Based-Views makes this easy.

```python
# your urls.py
from timelinejs.views import TimelineListView, \
    TimelineDeTailView, ImportTimelineFromSpreadsheetView

urls = patterns(''
    (
        r'^/$',
        TimelineListView.as_view(template_name='list_template_name.html'),
        name='timelines',
    ),
    (
        r'^import/$',
        ImportTimelineFromSpreadsheetView.as_view(template_name='import_template_name.html'),
        name='import_timeline',
    ),
    (
        r'^(?P<slug>[a-zA-Z0-9-_]+)/$',
        TimelineView.as_view(template_name='detail_template_name.html'),
        name='timeline',
    ),
)
```

Use the included templates as a sample and adjust based on your template setup.
There is no templatetag support since the configuration of TimelineJS is
complicated and you may want to use tools such as django_compressor for static
assets. A `Timeline` instance does have a `source` property which prints the
Google Spreadsheet URL if your timeline is linked to a Google Spreadsheet, or
outputs the appropriate JSON generated from the corresponding Django models.
Use `timeline.html` as a reference, but many more config options are available,
see the TimelineJS documentation.


###Permissions

On top of the default permissions (add, change, remove which apply through the
Django admin) dj-timelinejs includes a `view_private_timelines` permission that
toggles whether or not a user sees private timelines.

Users with the `add_timeline` permission will also be allowed to use the import
function, and a `user_can_add_timelines` context variable is passed to the
`TimlineListView` if you wish to include a link to the admin page for adding
timelines. See the timelines.html template as an example.


