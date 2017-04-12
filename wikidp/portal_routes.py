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
from wikidata import printPage
from flask import Flask, request
import wtforms
import flask
import re
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'
class ReusableForm(wtforms.Form):
    name = wtforms.TextField('Name:', validators=[wtforms.validators.required()])
 
 
@app.route("/", methods=['GET', 'POST'])
def home():
    form = ReusableForm(request.form)
 
    print (form.errors)
    if request.method == 'POST':
        name=request.form['name']
        print (name)
        itemList = [x.upper() for x in re.findall("Q\d+|q\d+", name)]
        if form.validate():
            # Save the comment here.
            for qID in itemList:
            	flask.flash(qID + ':  \n' + printPage(qID))
        else:
            flash('All the form fields are required. ')
        "Hello"
    return flask.render_template('home.html', form=form)
 
# @app.route("/", methods=['GET', 'POST'])
# def home():
#     """ Home route. """
#     name = wtforms.TextField('Name:')
#     # text = wikidata_test()
#     text = printPage()
#     return flask.render_template('home.html') + text
     
#     return text 
@app.route("/search/<string:name>/")
def search(name):
    """ search route. """
    # text = wikidata_test()
    return flask.render_template('temp.html', name=name, output=printPage(name))
    text = "searched\n" +  printPage() 
    return text
if __name__ == "__main__":
    app.run()
