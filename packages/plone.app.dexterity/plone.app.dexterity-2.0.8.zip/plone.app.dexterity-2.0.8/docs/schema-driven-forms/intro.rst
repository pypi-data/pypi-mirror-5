Introduction 
=============

**What is z3c.form all about?**

HTML forms are the cornerstone of modern web applications. When you
interact with Plone, you use forms all the time - to search the content
store, to edit content items, to fill in your personal details. You will
notice that most of these forms use the same layout and conventions, and
that they all rely on common patterns such as server-side validation and
different buttons resulting in different actions.

Over the years, several approaches have evolved to deal with forms. A
few of the most important ones are:

-  Creating a simple view with an HTML form that submits to itself (or
   another view), where the request is validated and processed in custom
   Python code. This is very flexible and requires little learning, but
   can also be fairly cumbersome, and it is harder to maintain a common
   look and feel and behaviour across all forms. See the `five.grok
   tutorial`_ for some hints on one way to build such views.
-  Using the *CMFFormController* library. This relies on special page
   objects known as “controller page templates” that submit to
   “controller python scripts”. The form controller takes care of the
   flow between forms and actions, and can invoke validator scripts.
   This only superficially addresses the creation of standard form
   layouts and widgets, however. It is largely deprecated, although
   Plone still uses it internally in places.
-  Using *zope.formlib*. This is a library which ships with Zope. It is
   based on the principle that a *schema interface* defines a number of
   form fields, constraints and so on. Special views are then used to
   render these using a standard set of widgets. Formlib takes care of
   page flow, validation and the invocation of *actions* - methods that
   correspond to buttons on the form. Formlib is used for Plone’s
   control panels and portlets. However, it can be cumbersome to use,
   especially when it comes to creating custom widgets or more dynamic
   forms.
-  Using *`z3c.form`_*. This is a newer library, inspired by formlib,
   but more flexible and modern.

This manual will show you how to use *z3c.form* in a Plone context. It
will use tools and patterns that are consistent with those used for
Dexterity development, as shown in the `Dexterity manual`_, but the
information contained herein is not Dexterity specific. Note that
Dexterity’s standard add and edit forms are all based on *z3c.form*.

Tools
-----

As a library, *z3c.form* has spawned a number of add-on modules, ranging
from new field types and widgets, to extensions that add functionality
to the forms built using the framework. We will refer to a number of
packages in this tutorial. The most important packages are:

-  `z3c.form`_ itself, the basic form library. This defines the standard
   form view base classes, as well the default widgets. The *z3c.form*
   `documentation`_ applies to the forms created here, but some of the
   packages below simplify or enhance the integration experience.
-  `plone.z3cform`_ makes *z3c.form* usable in Zope 2. It also adds a
   number of features useful in Zope 2 applications, notably a mechanism
   to extend or modify the fields in forms on the fly.
-  `plone.app.z3cform`_ configures *z3c.form* to use Plone-looking
   templates by default, and adds few services, such as a widget to use
   Plone’s visual editor and “inline” on-the-fly validation of forms.
   This package must be installed for *z3c.form*-based forms to work in
   Plone.
-  `plone.autoform`_ improves *z3c.form*’s ability to create a form from
   a schema interface. By using the base classes in this package,
   schemata can be more self-describing, for example specifying a custom
   widget, or specifying relative field ordering. We will use
   *plone.autoform* in this tutorial to simplify form setup.
-  `plone.directives.form`_ provides tools for registering forms using
   convention-over-configuration instead of ZCML. It depends on
   `five.grok`_ and adds support for the patterns that apply to the
   *grok.View* base class, including automatic template association. We
   will use *plone.directives.form* to configure our forms in this
   manual. You can read more about this in the `five.grok manual`_. We
   will register all our forms using *plone.directives.form* in this
   tutorial.

A note about versions
---------------------

The tools described in this manual work with both Plone 3.x (Zope 2.10)
and Plone 4 (Zope 2.12). However, the sample code is only tested in
Plone 4. Where there are differences between the two version, they will
be highlighted, but you should note that Zope 2.12 provides a better
environment out of the box. In Zope 2.10, a number of core packages must
be upgraded to work with *z3c.form*.

This manual has been tested with *z3c.form* 2.3.

.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _documentation: http://docs.zope.org/z3c.form
.. _plone.z3cform: http://pypi.python.org/pypi/plone.z3cform
.. _plone.app.z3cform: http://pypi.python.org/pypi/plone.app.z3cform
.. _plone.autoform: http://pypi.python.org/pypi/plone.autoform
.. _plone.directives.form: http://pypi.python.org/pypi/plone.directives.form
.. _five.grok: http://pypi.python.org/pypi/five.grok
.. _five.grok manual: ../developer-manual/custom-views/simple-views
.. _five.grok tutorial: /products/dexterity/documentation/manual/five.grok/browser-components/views
.. _z3c.form: http://pypi.python.org/pypi/z3c.form
.. _Dexterity manual: /products/dexterity/documentation/manual/developer-manual
