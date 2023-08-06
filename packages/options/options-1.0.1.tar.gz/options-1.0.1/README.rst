A module that helps encapsulate option and configuration data using a
multi-layer stacking (a.k.a. nested context) model.

Classes are expected to define default option values. When instances are
created, they can be instantiated with "override" values. For any option that
the instances doesn't override, the class default "shines through" and remains
in effect. Similarly, individual method calls can set transient values that
apply just for the duration of that call. If the call doesn't set a value, the
instance value applies. If the instance didn't set a
value, the class default applies. Python's ``with`` statement can be used to
tweak options for essentially arbitrary duration.

This layered or stacked approach is particularly helpful for highly
functional classes that aim for "reasonable" or "intelligent" defaults and
behaviors, that allow users to override those defaults at any time, and that
aim for a simple, unobtrusive API. It can also be used to provide flexible
option handling for functions.

This option-handling pattern is based on delegation rather than inheritance.
It's described in `this StackOverflow.com discussion of "configuration sprawl" 
<http://stackoverflow.com/questions/11702437/where-to-keep-options-values-paths-to-important-files-etc/11703813#11703813>`_.

Unfortunately, it's a bit hard to demonstrate the virtues of this approach with
simple code. Python already supports flexible function arguments, including
variable number of arguments (``*args``) and optional keyword arguments
(``**kwargs``). Combined with object inheritance, base Python features already
cover a large number of use cases and requirements. But when you have a large
number of configuration and instance variables, and when you might want to
temporarily override either class or instance settings, things get dicey. This
messy, complicated space is where ``options`` truly begins to shine.

.. image:: https://pypip.in/d/options/badge.png
    :target: https://crate.io/packages/options/


Usage
=====

::

    from options import Options, attrs
    
    class Shape(object):
    
        options = Options(
            name   = None,
            color  = 'white',
            height = 10,
            width  = 10,
        )
        
        def __init__(self, **kwargs):
            self.options = Shape.options.push(kwargs)
        
        def draw(self, **kwargs):
            opts = self.options.push(kwargs)
            print attrs(opts)

    one = Shape(name='one')
    one.draw()
    one.draw(color='red')
    one.draw(color='green', width=22)
    
yielding::

    color='white', width=10, name='one', height=10
    color='red', width=10, name='one', height=10
    color='green', width=22, name='one', height=10

So far we could do this with instance variables and standard arguments. It
might look a bit like this::

    class ClassicShape(object):

        def __init__(self, name=None, color='white', height=10, width=10):
            self.name   = name
            self.color  = color
            self.height = height
            self.width  = width

but when we got to the ``draw`` method, things would be quite a bit messier.::

        def draw(self, **kwargs):
            name   = kwargs.get('name',   self.name)
            color  = kwargs.get('color',  self.color)
            height = kwargs.get('height', self.height)
            width  = kwargs.get('width',  self.width)
            print "color='{}', width={}, name='{}', height={}".format(color, width, name, height)
        
One problem here is that we broke apart the values provided to
``__init__()`` into separate instance variables, now we need to
re-assemble them into something unified.  And we need to explicitly
choose between the ``**kwargs`` and the instance variables.  It
gets repetitive, and is not pretty. Another classic alternative,
using native keyword arguments, is no better::

        def draw2(self, name=None, color=None, height=None, width=None):
            name   = name   or self.name
            color  = color  or self.color
            height = height or self.height
            width  = width  or self.width
            print "color='{}', width={}, name='{}', height={}".format(color, width, name, height)

If we add just a few more instance variables, we have the `Mr. Creosote
<http://en.wikipedia.org/wiki/Mr_Creosote>`_ of class design on our hands. Not
good. Things get worse if we want to set default values for all shapes in the
class. We have to rework every method that uses values, the ``__init__`` method,
*et cetera*. We've entered "just one more wafer-thin mint..." territory.

But with ``options``, it's easy::

    Shape.options.set(color='blue')
    one.draw()
    one.draw(height=100)
    one.draw(height=44, color='yellow')
    
yields::

    color='blue', width=10, name='one', height=10
    color='blue', width=10, name='one', height=100
    color='yellow', width=10, name='one', height=44

In one line, we reset the default for all ``Shape`` objects.

The more options and settings a class has, the more unwieldy the class and
instance variable approach becomes, and the more desirable the delegation
alternative. Inheritance is a great software pattern for many kinds of data and
program structures, but it's a bad pattern for complex option and configuration
handling. For richly featured classes, the delegation pattern ``options`` proves
simpler. Supporting even a large number of options requires almost no additional
code and imposes no additional complexity or failure modes. By consolidating
options into one place, and by allowing neat, attribute-style access, everything
is kept tidy. We can add new options or methods with confidence::

    def is_tall(self, **kwargs):
        opts = self.options.push(kwargs)
        return opts.height > 100

Under the covers, ``options`` uses a variation on the ``ChainMap`` data
structure (a multi-layer dictionary) to provide its option stacking. Every
option set is stacked on top of previously set option sets, with lower-level
values shining through if they're not set at higher levels. This stacking or
overlay model resembles how local and global variables are managed in many
programming languages.

For more, please see the full installation and usage documentation 
on `Read the Docs <http://options.readthedocs.org/en/latest/>`_.

