# -*- coding: UTF-8 -*-
"""

:copyright: Copyright 2009-2013 by Luc Saffre.
:license: BSD, see LICENSE for more details.
"""

from __future__ import unicode_literals

import sys
import types
import datetime
from dateutil import parser as dateparser



class AttrDict(dict):
    """
    Dictionary-like helper object.
    
    Usage example:
    
    >>> from atelier.utils import AttrDict
    >>> a = AttrDict()
    >>> a.define('foo',1)
    >>> a.define('bar','baz',2)
    >>> print a
    {u'foo': 1, u'bar': {u'baz': 2}}
    >>> print a.foo
    1
    >>> print a.bar.baz
    2
    >>> print a.resolve('bar.baz')
    2
    >>> print a.bar
    {u'baz': 2}
    
    """
  
    #~ def __getattr__(self, name):
        #~ return self[name]
        
    def __getattr__(self, name,*args):
        return self.get(name,*args)
        #~ raise AttributeError("%r has no attribute '%s'" % (self,name))
        
    def define2(self,name,value):
        return self.define(*name.split('.')+[value])
        
    def define(self,*args):
        "args must be a series of names followed by the value"
        assert len(args) >= 2
        d = s = self
        for n in args[:-2]:
            d = s.get(n,None)
            if d is None:
                d = AttrDict()
                s[n] = d
            s = d
        oldvalue = d.get(args[-2],None)
        #~ if oldvalue is not None:
            #~ print 20120217, "Overriding %s from %r to %r" % (
              #~ '.'.join(args[:-1]),
              #~ oldvalue,
              #~ args[-1]
              #~ )
        d[args[-2]] = args[-1]
        return oldvalue
    
    def resolve(self,name,default=None):
        """
        return an attribute with dotted name
        """
        o = self
        for part in name.split('.'):
            o = getattr(o,part,default)
            # o = o.__getattr__(part)
        return o


def iif(condition,true_value,false_value): 
    """
    "Inline If" : an ``if`` statement as a function.
    
    Examples:
    
    >>> import six
    >>> from atelier.utils import iif
    >>> six.print_("Hello, %s world!" % iif(1+1==2,"real","imaginary"))
    Hello, real world!
    
    """
    if condition: return true_value
    return false_value
    
def i2d(i):
    """
    Convert `int` to `date`. Examples:
    
    >>> i2d(20121224)
    datetime.date(2012, 12, 24)
    
    """
    d = dateparser.parse(str(i))
    d = datetime.date(d.year,d.month,d.day)
    #print i, "->", v
    return d
    
def i2t(s):
    """
    Convert `int` to `time`. Examples:
    
    >>> i2t(815)
    datetime.time(8, 15)
    
    >>> i2t(1230)
    datetime.time(12, 30)
    
    >>> i2t(12)
    datetime.time(12, 0)
    
    >>> i2t(1)
    datetime.time(1, 0)
    
    """
    s = str(s)
    if len(s) == 4:
        return datetime.time(int(s[:2]),int(s[2:]))
    if len(s) == 3:
        return datetime.time(int(s[:1]),int(s[1:]))
    if len(s) <= 2:
        return datetime.time(int(s),0)
    raise ValueError(s)

    
    
    

def ispure(s):
    """
    Returns `True` if the specified string `s` is either a unicode 
    string or contains only ASCII characters.
    """
    if s is None: return True 
    if type(s) == types.UnicodeType:
        return True
    if type(s) == types.StringType:
        try:
            s.decode('ascii')
        except UnicodeDecodeError as e:
            return False
        return True
    return False

def assert_pure(s):
    #~ assert ispure(s), "%r: not pure" % s
    if s is None: return 
    if isinstance(s,unicode):
        return True
    try:
        s.decode('ascii')
    except UnicodeDecodeError as e:
        raise Exception("%r is not pure : %s" % (s,e))
     



def confirm(prompt=None):
    """
    Ask for user confirmation from the console.
    """
    while True:
        ln = raw_input(prompt)
        if ln.lower() in ('y','j','o'):
            return True
        if ln.lower() == 'n':
            return False
        print "Please anwer Y or N"



def indentation(s):
    r"""
    Examples:
    
    >>> from atelier.utils import indentation
    >>> indentation("")
    0
    >>> indentation("foo")
    0
    >>> indentation(" foo")
    1
    
    """
    return len(s)-len(s.lstrip())


def unindent(s):
    r"""
    Reduces indentation of a docstring to the minimum.
    Empty lines don't count.
    
    Examples:
    
    >>> from atelier.utils import unindent
    >>> unindent('')
    u''
    >>> print unindent('''
    ...   foo
    ...     foo
    ... ''')
    <BLANKLINE>
    foo
      foo
    >>> print unindent('''
    ... foo
    ...     foo
    ... ''')
    <BLANKLINE>
    foo
        foo
    """
    lines = s.splitlines()
    if len(lines) == 0: 
        return s.lstrip()
    mini = sys.maxint
    for ln in lines:
        ln = ln.rstrip()
        if len(ln) > 0: 
            mini = min(mini,indentation(ln))
            if mini == 0:
                break
    if mini == sys.maxint: 
        return s
    return '\n'.join([ln[mini:] for ln in lines])
    
