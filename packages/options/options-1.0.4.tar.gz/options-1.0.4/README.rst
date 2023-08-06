options
=======

``options`` helps encapsulate options and configuration data using a
layered stacking model (a.k.a. nested contexts).

For most functions and many classes, ``options``
is overkill and not recommended.
Python's already-flexible function arguments, ``*args``,
``**kwargs``, and inheritance patterns are elegant and sufficient
for 99.9% of all development situations.

``options``
is intended for the 0.1%: highly
functional classes that have many different options, that
aim for "reasonable" or "intelligent" defaults and
behaviors, that allow users to override those defaults at any time, and yet that
aim for a simple, unobtrusive API.

In those cases, Python's simpler built-in, inheritance-based
model leads to fairly complex code as non-trivial options and argument-management
code spreads through many individual methods. This is where
``options``'s delegation-based approach begins to shine.


.. image:: https://pypip.in/d/options/badge.png
    :target: https://crate.io/packages/options/


Usage
=====

In a typical use, your class defines default option values. Subclasses
can add, remove, or override options. Instances
use class defaults, but they can be overridden when each instance
is created. For any option an instance doesn't override, the class
default "shines through."

So far, this isn't very different from a typical use of Python's
standard instance and
class variables.  The next step is where ``options`` gets interesting.

Individual method calls can similarly override instance and class defaults.
The options stated in each method call obtain
only for the duration of the method's execution.
If the call doesn't set a value, the
instance value applies. If the instance didn't set a
value, its class default applies (and so on, to its superclasses, if any).

One step further, Python's ``with`` statement can be used to
set option values for essentially arbitrary duration. As soon as the
``with`` block exists, the option values automagically fall back to
what they were before the with block. (In general, if any option is unset,
its value falls back to what it was in the next higher layer.)

To recap: Python easily layers class, subclass, and instance settings.
``options`` layers class, subclass, and instance settings as well, but also
adds method and transient settings. When Python mechanisms override a setting,
they do so destructively; they cannot be "unset" without additional code.
When a program using ``options`` overrides a setting, it does so non-destructively,
layering the new settings atop the previous ones. When attributes are unset,
they immediately fall back to their prior value (at whatever higher level it
was last set).

Unfortunately, because this is a capability designed for high-end, edge-case
situations, it's hard to demonstrate its virtues with
simple code. But we'll give it a shot.

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
            print "color='{0}', width={1}, name='{2}', height={3}".format(color, width, name, height)

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
            print "color='{0}', width={1}, name='{2}', height={3}".format(color, width, name, height)

If we add just a few more instance variables, we have the `Mr. Creosote
<http://en.wikipedia.org/wiki/Mr_Creosote>`_ of class design on our hands. Every
possible setting has to be managed in every method. It's neither elegant nor
scalable. Things get even worse if we want to set default values for all shapes in the
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

In one line, we reset the default for all ``Shape`` objects. (In typical usage
we'd also define ``Shape.set()`` to transparently forward
to ``Shape.options.set()`` for an even simpler resulting API.)

The more options and settings a class has, the more unwieldy the class and
instance variable approach becomes, and the more desirable the delegation
alternative. Inheritance is a great software pattern for many kinds of data and
program structures--but it's a bad, or at least incomplete,
pattern for complex option and configuration
handling.

For richly-featured classes, ``options``'s delegation pattern is
simpler. As the number of options grows, almost no additional
code is required. More options
impose no additional complexity and introduce no additional failure modes.
Consolidating
options into one place, and providing
neat attribute-style access, keeps everything
tidy. We can add new options or methods with confidence::

    def is_tall(self, **kwargs):
        opts = self.options.push(kwargs)
        return opts.height > 100

Under the covers, ``options`` uses a variation on the ``ChainMap`` data
structure (a multi-layer dictionary) to provide option stacking. Every
option set is stacked on top of previously set option sets, with lower-level
values shining through if they're not set at higher levels. This stacking or
overlay model resembles how local and global variables are managed in many
programming languages.

This makes advanced use cases, such as temporary value changes, easy::

    with one.settings(height=200, color='purple'):
        one.draw()
        if is_tall(one):
            ...         # it is, but only within the ``with`` context

    if is_tall(one):    # nope, not here!
        ...

Full disclosure: Doing temporary settings took more class setup code
than is shown above. Four lines of code, to be precise.

As one final feature, consider "magical" parameters. Add the following
code::

    options.magic(
        height = lambda v, cur: cur.height + int(v) if isinstance(v, str) else v,
        width  = lambda v, cur: cur.width  + int(v) if isinstance(v, str) else v
    )

Now, in addition to absolute ``height`` and ``width`` parameters specified with
``int`` (integer/numeric) values, your module
auto-magically supports relative parameters for ``height`` and ``width``.::

    one.draw(width='+200')

yields::

    color='blue', width=210, name='one', height=10

Neat, huh?

For more, see `this StackOverflow.com discussion of how to combat "configuration sprawl"
<http://stackoverflow.com/questions/11702437/where-to-keep-options-values-paths-to-important-files-etc/11703813#11703813>`_
and ``options`` full documentation
on `Read the Docs <http://options.readthedocs.org/en/latest/>`_. For examples of ``options``
in use, see `say <https://pypi.python.org/pypi/say>`_ and `show <https://pypi.python.org/pypi/show>`_.
