#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2017
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
""" Flask application routes for Wikidata portal. """
import re

from flask import flash, render_template, request
import wtforms
from wikidp.wikidata import print_page
from wikidp import APP

class ReusableForm(wtforms.Form):
    """Valdiators for application forms."""
    name = wtforms.TextField('Name:', validators=[wtforms.validators.required()])


@APP.route("/", methods=['GET', 'POST'])
def home():
    """Default landing page."""
    form = ReusableForm(request.form)

    print(form.errors)
    if request.method == 'POST':
        name = request.form['name']
        print(name)
        item_list = [x.upper() for x in re.findall("Q\d+|q\d+", name)]
        if form.validate():
            # Save the comment here.
            for q_id in item_list:
                flash(q_id + ':  \n' + print_page(q_id))
        else:
            flash('All the form fields are required. ')
    return render_template('home.html', form=form)

@APP.route("/search/<string:name>/")
def search(name):
    """ search route. """
    # text = wikidata_test()
    return render_template('temp.html', name=name, output=print_page(name))

if __name__ == "__main__":
    APP.run()
