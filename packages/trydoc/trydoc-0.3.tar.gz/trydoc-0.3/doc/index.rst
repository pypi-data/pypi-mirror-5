.. TryDoc Test documentation master file, created by
   sphinx-quickstart on Sun Nov 13 11:04:16 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

TryDoc documentation
====================

Installation
------------

This extension requires the following packages:

- Sphinx 1.0
- proteus
- tryton

Use ``pip`` to install this extension straight from the Python Package Index::

   pip install trydoc


Configuration
-------------

In order to use trydoc you should add it to the list of extensions in conf.py::

   extensions = ['sphinxcontrib.trydoc']

You should also configure proteus in conf.py with the required parameters. The 
following example will create a new sqlite database automatically::

   import proteus
   proteus.config.set_trytond(database_type='sqlite')

If you use 'sqlite' memory database (like the example) you must define the
list of modules to install to be able to reference their elements (models,
fields, views, menus...).::

   trydoc_modules = ['party', 'sale']

You can use a persistent PostgreSQL database (the customer's database
tipically). The configuration will be something like this:::

    proteus_config = proteus.config.set_trytond(database_name='trydoc',
            database_type='postgresql', language='es_ES', password='admin',
            config_file='~/trytond/etc/trytond.conf')

Usage
-----

TryDoc adds the following set of directives to be used in the docs:

Fields
~~~~~~

You can refer to any field with the following directive:

::

   .. fields:: model/field

which will print the given field name inside an _span_ with the class
*trydocfield*. You can change this default class with the configuration option
*trydoc_fieldclass*.

Optionally the ``:help:`` flag can be added. See the following example:

::

   .. fields:: ir.cron/user
      :help:

It will print the help text of field despite of the field name (if the field
doesn't have help text it will print a message advertising it.

It also have another optional option ``:class: CLASSLIST``. It adds the
specified classes to the _span_ (not replace the default class). An example:::

   .. fields:: ir.cron/user
      :class: admin

It will generate the following code:::

    <span class="trydocfield admin">Usuario</span>

Views
~~~~~

You can add a screenshot of any model view with the following directive:

::

   .. view:: reference_to_view_xml_id
      :field: fieldname

where ``:field:`` is optional and will ensure the given field name is shown in 
the generated screenshot.

::

   .. view:: party.party_party_form
      :field: name

.. Note:: This directive is not fully working yet. It will add a screenshot of
   tryton's client but not of the appropriate view.

It also has the optional option ``:class: CLASSLIST`` which adds the specified
class to the default class *trydocview* (which can be changed with the
configuration option *trydoc_viewclass*).

Menus and other data
~~~~~~~~~~~~~~~~~~~~

You can refer to any menu entry with the following directive:

::

   .. tryref:: reference_to_menu_xml_id/fieldname

The following code shows the full menu entry:

::

   .. tryref:: ir.menu_cron_form/complete_name

which will output *Administration / Scheduler / Scheduled Actions*.
You can also access any field of the record, for example:

::

   .. tryref:: ir.menu_cron_form/name

will output *Scheduled Actions*. **tryref** can be used to access any field of 
any record with an *ir.model.data* if you know its XML id.

Like field directive, it will output the text inside an _span_ tag with the
class *trydocref*. This default class could be changed with the configuration
option *trydoc_refclass*. And if you want to add another classes to an specific
entry you could use the ``:class: CLASSLIST`` option.

Inline usage
~~~~~~~~~~~~

Inline usage is also available either using Sphinx's replace mechanism. As it
uses the directive it has all options and the same behaviour than directives:

::

   This is a reference to field |cron_user|.

   .. |cron_user| field:: ir.cron/user

or one provided by trydoc, which is shorter (but it doesn't put the text inside
and _span_ tag and it doesn't support any option):

::

   This is a reference to a field @field:ir.cron/user@.

