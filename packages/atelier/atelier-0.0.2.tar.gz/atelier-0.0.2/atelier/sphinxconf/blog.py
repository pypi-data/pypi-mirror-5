# -*- coding: utf-8 -*-
"""

This Sphinx extension defines the 
``blogger_year`` and 
``blogger_index``
directives and the ``blogref`` text role.


:copyright: Copyright 2011-2013 by Luc Saffre.
:license: BSD, see LICENSE for more details.

Thanks to 

- `Creating reStructuredText Directives 
  <http://docutils.sourceforge.net/docs/howto/rst-directives.html>`_


"""
  
import os
import sys
import calendar
import datetime
from StringIO import StringIO

from unipath import Path
#~ import lino

#~ from django.conf import settings

#~ from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from docutils import nodes, utils
from docutils import statemachine
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles
from sphinx.util.compat import Directive

from atelier import rstgen

from atelier.sphinxconf import InsertInputDirective

import jinja2

templates = dict()
templates['calendar.rst'] = """
====
{{year}}
====

{{intro}}

.. |br| raw:: html

   <br />   

.. |sp| raw:: html

   <span style="color:white;">00</span>

{{calendar}}


"""

JINJA_ENV = jinja2.Environment(
    #~ extensions=['jinja2.ext.i18n'],
    loader=jinja2.DictLoader(templates))
    
    



class Year(object):
    """
    A :class:`Year` instance is created for each 
    `blogger_year` directive.
    """
    #~ _instances = dict()
    #~ def __init__(self,env,blogname,starting_year):
    #~ def __init__(self,env,blogname,year):
    def __init__(self,env):
        """
        :docname: the name of the document containing the `main_blogindex` directive
        :starting_year: all years before this year will be pruned
        """
        
        blogname, year, index = env.docname.rsplit('/',3)
        if index != 'index':
            raise Exception("Allowed only in /<blogname>/<year>/index.rst files")
        self.year = int(year)
        
        #~ print "20130113 Year.__init__", blogname, self.year
        #~ self.blogname = blogname
        self.days = set()
        #~ self.years = set()
        #~ self.starting_year = int(starting_year)
        top = os.path.dirname(env.doc2path(env.docname))
        #~ print top
        for (dirpath, dirnames, filenames) in os.walk(top):
            del dirnames[:] # don't descend another level
            #~ unused, year = dirpath.rsplit(os.path.sep,2)
            #~ year = int(year)
            #~ assert year in self.years
            for fn in filenames:
                if len(fn) == 8 and fn.endswith('.rst'):
                    d = docname_to_day(self.year,fn[:-4])
                    self.days.add(d)
                    #~ self.years.add(s)
                        
        #~ self.years = sorted(self.years)
        if not hasattr(env,'blog_instances'):
            env.blog_instances = dict()
        years = env.blog_instances.setdefault(blogname,dict())
        years[self.year] = self
                        
        
        
"""
docs/conf.py
docs/blog/index.rst --> contains a main_blogindex directive (hidden toctree)
docs/blog/2013/index.rst --> contains a blogger_year directive (calendar)
docs/blog/2013/0107.rst --> a blog entry
docs/blog/2010/0107.rst

"""
        
   
    
class MainBlogIndexDirective(InsertInputDirective):
    """
    Directive to insert a blog master archive page toctree
    """
    #~ required_arguments = 1
    #~ allow_titles = True
    raw_insert = True
  
    def get_rst(self):
        #~ print 'MainBlogIndexDirective.get_rst()'
        env = self.state.document.settings.env
        intro = '\n'.join(self.content)
        #~ dn  = os.path.dirname(env.doc2path(env.docname))
        #~ year = os.path.split(dn)[-1]
        blogname, index = env.docname.rsplit('/',2)
        if index != 'index':
            raise Exception("Allowed only inside index.rst file")
        #~ blog = Blog.get_or_create(env,blogname,self.arguments[0])
        text = intro
        text += """

.. toctree::
    :maxdepth: 2

"""
        years = list(env.blog_instances.get(blogname).values())
        def f(a,b): 
            return cmp(a.year,b.year)
        years.sort(f)
        for blogger_year in years:
        #~ for year in blog.years:
            text += """
    %d/index""" % blogger_year.year
  
        text += "\n"
        #~ print text
        return text
   
   
   

class YearBlogIndexDirective(InsertInputDirective):
    """
    Directive to insert a year's calendar
    """
    #~ required_arguments = 1
    #~ allow_titles = True
    raw_insert = True
    
      
    def get_rst(self):
        from djangosite.dbutils import monthname
  
        #~ year = self.arguments[0]
        env = self.state.document.settings.env
        today = datetime.date.today()
        
        #~ dn  = os.path.dirname(env.doc2path(env.docname))
        #~ year = os.path.split(dn)[-1]
        blogger_year = Year(env)
        #~ blog = Blog.get_or_create(env,blogname)
        
        tpl = JINJA_ENV.get_template('calendar.rst')
        
        intro = '\n'.join(self.content)
        cal = calendar.Calendar()
        text = ''
        
        for month in range(1,13):
            
            text += """        
            
.. |M%02d| replace::  **%s**""" % (month,monthname(month))
            
            weeknum = None
            #~ text += "\n  |br| Mo Tu We Th Fr Sa Su "
            for day in cal.itermonthdates(blogger_year.year,month):
                iso_year,iso_week,iso_day = day.isocalendar()
                if iso_week != weeknum:
                    text += "\n  |br|"
                    weeknum = iso_week
                if day.month == month:
                    label = "%02d" % day.day
                    docname = "%02d%02d" % (day.month,day.day)
                    if blogger_year.year == iso_year and day in blogger_year.days:
                        text += " :doc:`%s <%s>` " % (label,docname)
                    elif day > today:
                        text += ' |sp| '
                    else:
                        text += ' ' + label + ' '
                else:
                    text += ' |sp| '
                
            
            
        text += """
        
===== ===== =====
|M01| |M02| |M03|
|M04| |M05| |M06|
|M07| |M08| |M09|
|M10| |M11| |M12|
===== ===== =====
        
        """
        
        text += """

.. toctree::
    :hidden:
    :maxdepth: 2
    
"""
        
        days = sorted(blogger_year.days)
        for day in days:
            text += """
    %02d%02d""" % (day.month,day.day)
        
        return tpl.render(
            calendar=text,
            intro=intro,
            year=blogger_year.year,
            days=blogger_year.days)
        

def docname_to_day(year,s):
    #~ print fn
    month = int(s[:2])
    day = int(s[2:])
    return datetime.date(year,month,day)
  
  
#~ class ChangedDirective(InsertInputDirective):
  
    #~ def get_rst(self):
        #~ env = self.state.document.settings.env
        #~ blogname, year, monthday = env.docname.rsplit('/',3)
        #~ # raise Exception("Allowed only in blog entries")
        
        #~ year = int(year)
        #~ day = docname_to_day(year,monthname)
        
        #~ if not hasattr(env,'changed_items'):
            #~ env.changed_items = dict()
        #~ env.changed_items
        #~ for item in self.content:
            #~ entries = env.changed_items.setdefault(item,dict())
            #~ entries.setdefault(env.docname)
            
            

def setup(app):
    #~ app.add_node(blogindex)
    #~ app.add_node(blogindex,html=(visit_blogindex,depart_blogindex))
    #~ app.add_directive('changed', ChangedDirective)
    app.add_directive('blogger_year', YearBlogIndexDirective)
    app.add_directive('blogger_index', MainBlogIndexDirective)
    


