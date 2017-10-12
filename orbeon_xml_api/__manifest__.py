# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2017 open2bizz (open2bizz.nl).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name": "Orbeon XML API",
    'summary': 'Orbeon XML API',
    'description': """
Orbeon XML API
==============

**Use the Orbeon (Runner) Forms XML-field, like it's a simple Python object.**

This module extends the Orbeon Runner model-object, with a special
property/attribute **o_xml**.

The **o_xml** property is the "Pythonic" object API on the Runner its XML.


Syntax examples (by "Form Control Name")
----------------------------------------

**1) firstname** (text controls)

* **runner.o_xml.form.firstname.label**
    The label of (form) field *firstname*, as a Python string e.g. "First Name"

* **runner.o_xml.form.firstname.value**
    The value of (form) field *firstname*, as a Python string e.g. "John"

**2) job_title** (text controls)

*Underscorers are valid.*

* **runner.o_xml.form.job_title.label**
    The label of (form) field *job_title*, as a Python string e.g. "Job Title"

* **runner.o_xml.form.job_title.value**
    The value of (form) field *job_title*, as a Python string e.g. "Programmer"

**3) address-housenumber** (text controls)

*Hyphens should be omitted (removed) in the syntax !*

* **runner.o_xml.form.addresshousenumber.label**
    The label of (form) field *job_title*, as a Python string e.g. "Housenumber"

* **runner.o_xml.form.addresshousenumber.value**
    The value of (form) field *job_title*, as a Python string e.g. "17"

**4) birthdate** (date/time controls)

* **runner.o_xml.form.birthdate.label**
    The label of (form) field *birthdate*, as a Python string e.g. "Birthdate"

* **runner.o_xml.form.birthdate.value**
    The value of (form) field *birthdate*, as a Python *Date object*.

**5) favorite_dishes** (single and multi selection controls)

* **runner.o_xml.form.favorite_dishes.label**
    The label of (form) field *favorite_dishes*, as a Python string e.g. "Your Favorite Dishes"

* **runner.o_xml.form.favorite_dishes.choices**
    The transformed value of (form) field *favorite_dishes*, as a Python *dictionary object*.

    Whereby key is choice-label and value is choice-value.

    E.g: {'Italian Pizza': 'it-pizza', 'Calafornia Sushi': 'cal-sushi'}

* **runner.o_xml.form.favorite_dishes.choices_labels**
    The transformed value of (form) field *favorite_dishes*, as a Python *list object*, with the choice labels.
    E.g: ['Italian Pizza', 'California Sushi']

* **runner.o_xml.form.favorite_dishes.choices_values**
    The transformed value of (form) field *favorite_dishes*, as a Python *list object*, with the choice values.

    E.g: ['it-pizza', 'cal-sushi']

**5) image_primary (image controls)**

*Curently handles Orbeon Image types: "Static Image", "Image Attachment" and "Image Annotation (by Wpaint plugin)".

* **runner.o_xml.form.image_primary.label**
    The label of (form) field *primaryimage*, as a Python string e.g. "Profile Image".

* **runner.o_xml.form.image_primary.value**
    The value of (form) field *primaryimage*, as a Python *base64 string*.

""",
    "version": "0.1",
    "author": "Open2bizz",
    "website": "http://www.open2bizz.nl",
    "license": "AGPL-3",
    "category": "Extra Tools",
    "depends": [
        "orbeon",
    ],
    # 'external_dependencies': {
    #     'python': ['orbeon_xml_api'],
    # },
    'data': [
        'views/report_runner_test.xml'
    ],
    "application": False,
    "installable": True,
}
