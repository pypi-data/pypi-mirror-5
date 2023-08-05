Widgets
==========

**Changing the widget used to render a field**

Like most form libraries, *z3c.form* separates a field – a
representation of the value being provided by the form – from its widget
– a UI component that renders the field in the form. In most cases, the
widget is rendered as a simple HTML *<input />* element, although more
complex widgets may use more complex markup.

The simplest widgets in *z3c.form* are field-agnostic. However, we
nearly always work with *field widgets*, which make use of field
attributes (e.g. constraints or default values) and optionally the
current value of the field (in edit forms) during form rendering.

Most of the time, we don’t worry too much about widgets: each of the
standard fields has a default field widget, which is normally
sufficient. If we need to, however, we can override the widget for a
given field with a new one.

Selecting a custom widget using form directives
-----------------------------------------------

*plone.directives.form* provides a convenient way to specify a custom
widget for a field, using the *form.widget()* directive:

::

    from five import grok
    from plone.directives import form

    from zope import schema

    from plone.app.z3cform.wysiwyg import WysiwygFieldWidget

    ...

    class IPizzaOrder(form.Schema):
        
        ...
        
        form.widget(notes=WysiwygFieldWidget)
        notes = schema.Text(
                title=_(u"Notes"),
                description=_(u"Please include any additional notes for delivery"),
                required=False
        )

The argument can be either a field widget factory, as shown here, or the
full dotted name to one (*plone.app.z3cform.wysiwyg.WysiwygFieldWidget*
in this case).

Supplying a widget factory
~~~~~~~~~~~~~~~~~~~~~~~~~~

Later in this manual, we will learn how to set up the *fields* attribute
of a form manually, as is done in “plain” *z3c.form*, instead of using
the *schema* shortcut that is provided by *plone.autoform*. If you are
using this style of configuration (or simply looking at the basic
*z3c.form* documentation), the syntax for setting a widget factory is:

::

    class OrderForm(Form):
        
        fields = field.Fields(IPizzaOrder)
        fields['notes'].widgetFactory = WysiwygFieldWidget
        
        ...

Updating widget settings
------------------------

All widgets expose properties, which control how they are rendered. You
can set these properties by overriding the *updateWidget()* method,
calling the base class version, and then changing properties. For
example, we could set the size of the postcode widget to be more
suitable for its contents:

::

    class OrderForm(form.SchemaForm):
        grok.name('order-pizza')
        grok.require('zope2.View')
        grok.context(ISiteRoot)
        
        schema = IPizzaOrder
        ignoreContext = True
        
        label = _(u"Order your pizza")
        description = _(u"We will contact you to confirm your order and delivery.")
        
        def update(self):
            # disable Plone's editable border
            self.request.set('disable_border', True)
            
            # call the base class version - this is very important!
            super(OrderForm, self).update()
        
        def updateWidgets(self):
            super(OrderForm, self).updateWidgets()
            self.widgets['postcode'].size = 4

        ...

Some of the more useful properties are shown below. These generally
apply to the widget’s *<input />* element.

-  *klass*, a string, can be set to a CSS class. There’s also the
   *addClass()* helper method, which can be used to add a new CSS class.
-  *style*, a string, can be set to a CSS style string
-  *title*, a string, can be used to set the HTML attribute with the
   same name
-  *onclick*, *ondblclick*, etc can be used to associate JavaScript code
   with the corresponding events
-  *disabled* can be set to True to disable input into the field

Other widgets also have attributes that correspond to the HTML elements
they render. For example, the default widget for a *Text* field renders
a *<textarea />* , and has attributes like *rows* and *cols*. For a
*TextLine*, the widget renders an *<input type=“text” />*, which
supports a *size* attribute, among others.

Take a look at *z3c.form*’s *browser/interfaces.py* for a full list of
attributes that are used.

Widget reference
----------------

You can find the default widgets in the *browser* package in *z3c.form*.
The *z3c.form* `documentation`_ contains a `listing`_ of all the default
widgets that shows the HTML output of each.

In addition, the Dexterity manual contains `an overview`_ of widgets
which are frequently used as custom widgets.

.. _documentation: http://docs.zope.org/z3c.form
.. _listing: http://docs.zope.org/z3c.form/browser/README.html
.. _an overview: http://readthedocs.org/docs/dexterity-developer-manual/en/latest/reference/widgets.html
