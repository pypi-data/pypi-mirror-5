PyGreen
=======

A micro web framework/static web site generator.

PyGreen is a simple tool to generate small web sites. The concept is to put all
files to serve in a folder and invoke the Mako template engine on all .html files.
The result is quite similar to a classic PHP application, but with the
good features of the Mako templates (like inheritance) and the cool syntax of Python.

PyGreen uses the MIT license.

Quick Start
-----------

To install:

    sudo easy_install pygreen

To launch and serve files:

    pygreen serve

The above command will serve the files located in the current folder.
All files with the .html extension will also be processed by Mako. So if the current
folder contains a file index.html with the following code:

    <p>Hello, my age is ${30 - 2}.</p>

When going to http://localhost:8080, you will see:

    <p>Hello, my age is 28.</p>

PyGreen can also export all the files of you current folder after having the .html files processed by Mako. To do so, type this command:

    pygreen gen <output_folder>

This can be useful to post your files on Github Pages or any other free static files hosting services.

Features
--------

PyGreen was designed to not have a lot of features. Mako templates can contain Python code, so you can always
code anything you need. The following features are still useful in most projects and are directly integrated in PyGreen.

Non-generated files
-------------------

All files with the .mako or .py extension will not be outputed by pygreen gen.
This is useful to avoid generating macros files or templates to inherit.
Hidden files (files beginning with '.') will not be generated either.

Markdown
--------

While it is easy to define your own macro for markdown, it's still a recurrent need for most sites.
So there is a default Mako filter for that:

    <%block filter="markdown">
    Look at my title
    ================
    </%block>


FAQ
===

I miss feature XYZ, can you add it?
-----------------------------------

No. But you can. Easily. PyGreen can be a command line application or it can be a small framework to ease creation of complete Python web applications. PyGreen is just Mako templates served using the Bottle web framework. You can easily modify any of these using some python code. Example:

    from pygreen import pygreen

    pygreen.app # the Bottle wsgi application, use the @route() decorator to add new routes
    pygreen.templates # the Mako TemplateLookup object, do what you want with it

    pygreen.cli() # call the command line interface of PyGreen, you can use it or

    # just launch a web server using the Bottle application object

It's important to understand that PyGreen is just a helper that allows to make simple things simple (like defining 3 html files that inherit from a common template without the need to type code) but doesn't restrict you. You need anything complex? Mako templates can contain Python code so import whatever you need and use the features it provides. If you need anything more complex hack through PyGreen and do it. Read the PyGreen code, it's 100 lines with some documentation, anyone can understand it. If you read this you should be a Python programmer, so just type the code and get the job done.

Why is it so cool?
------------------

PyGreen was primarily created to be a static web site generator more effective than existing ones. The problem of existing site generators like Jekyll or Hyde is that they have a fixed number of features. Even if their creators try to add advanced features those will not be correctly documented, so the users do not know how to use them.

The fact that PyGreen has a small set of features is a feature. You don't need to spend hours to read crappy documentation before discovering it's impossible to do what you want. If you need to do anything which is not trivial you know you will have to code it, so just do it. That's what I call being pragmatic.

Does PyGreen need contributions?
--------------------------------

Yes! Report issues, write examples in the wiki, propose improvements, everything is on Github. Just keep in mind that PyGreen is designed to be minimalist, so big features will probably not be accepted.

You can also write articles or blog posts about PyGreen.

[See the web site for any information.](http://pygreen.neoname.eu)

Version 1.0.3

Changelog:

* 1.0.3:

    * Added *.py to excluded files
    * Some minor API changes
    * Bug fixes
