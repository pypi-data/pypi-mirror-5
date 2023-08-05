# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# lib:  templatealchemy.test
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2013/07/03
# copy: (C) Copyright 2013 Cadit Health Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import unittest, os.path
import templatealchemy
from templatealchemy.util import adict

#------------------------------------------------------------------------------
class TestTemplateAlchemy(unittest.TestCase):

  maxDiff = None

  #----------------------------------------------------------------------------
  def test_mustache(self):
    root = templatealchemy.Template(
      source='pkg:templatealchemy:test_data/mustache',
      renderer='mustache')
    tpl = root.getTemplate('document')
    out = tpl.render('html', adict(
        title='TemplateAlchemy',
        doc=adict(title='Mustache'),
        sections=[
          adict(title='Overview', text='Good'),
          adict(title='Details', text='Poor'),
          adict(title='Utility', text='Excellent'),
          ]))
    chk = '''\
<html>
 <head>
  <title>TemplateAlchemy</title>
 </head>
 <body>
  <h1>TemplateAlchemy</h1>
  <h2>Mustache</h2>
   <h3>Overview</h3>
   <p>Good</p>
   <h3>Details</h3>
   <p>Poor</p>
   <h3>Utility</h3>
   <p>Excellent</p>
 </body>
</html>
'''
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_mako(self):
    root = templatealchemy.Template(
      source='pkg:templatealchemy:test_data/mako',
      renderer='mako')
    tpl = root.getTemplate('document')
    out = tpl.render('html', adict(
        title='TemplateAlchemy',
        doc=adict(title='Mako'),
        sections=[
          adict(title='Overview', text='Good'),
          adict(title='Details', text='Poor'),
          adict(title='Utility', text='Excellent'),
          ]))
    chk = '''\
<html>
 <head>
  <title>TemplateAlchemy</title>
 </head>
 <body>
  <h1>TemplateAlchemy</h1>
  <h2>Mako</h2>
   <h3>Overview</h3>
   <p>Good</p>
   <h3>Details</h3>
   <p>Poor</p>
   <h3>Utility</h3>
   <p>Excellent</p>
 </body>
</html>
'''
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_sqlalchemy(self):
    # todo: what if templatealchemy is a zipped archive?...
    path = os.path.join(os.path.dirname(__file__), 'test_data/sa/source.db')
    root = templatealchemy.Template(
      source='sqlalchemy:sqlite:///' + path,
      renderer='mustache')
    tpl = root.getTemplate('document')
    out = tpl.render('html', adict(title='TemplateAlchemy'))
    chk = '<html><body><h1>TemplateAlchemy</h1></body></html>'
    self.assertMultiLineEqual(out, chk)

  #----------------------------------------------------------------------------
  def test_string(self):
    root = templatealchemy.Template(source='string:ALL YOUR ${plan["from"]} ARE BELONG TO ${plan["to"]}')
    params = dict(plan=adict((('from', 'BASE'), ('to', 'US'))))
    outt = root.render('text', params)
    outh = root.render('html', params)
    self.assertEqual(outt, 'ALL YOUR BASE ARE BELONG TO US')
    self.assertEqual(outh, 'ALL YOUR BASE ARE BELONG TO US')

  #----------------------------------------------------------------------------
  def test_commandLine(self):
    from . import cli
    from StringIO import StringIO
    out = StringIO()
    tpl = '''\
<html>
 <head>
  <title>{{title}}</title>
 </head>
 <body>
  <h1>{{title}}</h1>
  <h2>{{doc.title}}</h2>
  {{#sections}}
   <h3>{{title}}</h3>
   <p>{{text}}</p>
  {{/sections}}
 </body>
</html>
'''
    cli.main([
        '--params',
        '{title: "TemplateAlchemy", doc: {title: "Command Line"}, sections: ['
        + '{title: Overview, text: Good},'
        + '{title: Details, text: Poor},'
        + '{title: Utility, text: Excellent},'
        + ']}',
        '--renderer', 'mustache',
        'string:' + tpl], output=out)
    chk = '''\
<html>
 <head>
  <title>TemplateAlchemy</title>
 </head>
 <body>
  <h1>TemplateAlchemy</h1>
  <h2>Command Line</h2>
   <h3>Overview</h3>
   <p>Good</p>
   <h3>Details</h3>
   <p>Poor</p>
   <h3>Utility</h3>
   <p>Excellent</p>
 </body>
</html>
'''
    self.assertMultiLineEqual(out.getvalue(), chk)

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
