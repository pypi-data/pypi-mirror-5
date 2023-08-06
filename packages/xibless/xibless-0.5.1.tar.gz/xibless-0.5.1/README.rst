===================================
xibless - Get rid of XIBs and XCode
===================================

``xibless`` is a library that generates Objective-C code that builds Cocoa UIs. The goal of this library
is to replace XIBs in XCode and, if you want, get rid of XCode altogether.

With ``xibless``, instead of designing UIs with a WYSIWYG editor, you build them in a Python script,
similarly to what you do when you build Qt UIs without the Designer. For example, a script like this::

    result = Window(330, 110, "Tell me your name!")
    nameLabel = Label(result, text="Name:")
    nameField = TextField(result, text="")
    helloLabel = Label(result, text="")
    button = Button(result, title="Say Hello")

    nameLabel.width = 45
    nameLabel.moveTo(Pack.UpperLeft)
    nameField.moveNextTo(nameLabel, Pack.Right, align=Pack.Middle)
    nameField.fill(Pack.Right)
    helloLabel.moveNextTo(nameLabel, Pack.Below, align=Pack.Left)
    helloLabel.fill(Pack.Right)
    button.moveNextTo(helloLabel, Pack.Below, align=Pack.Right)
    nameField.setAnchor(Pack.UpperLeft, growX=True)
    helloLabel.setAnchor(Pack.UpperLeft, growX=True)
    button.setAnchor(Pack.UpperRight)

would generate Objective-C code that build a form with a name field, a text label and a button. The
second part of the script places the widgets on the form appropriately.

**Although xibless is written in Python, the Objective-C code it generates has no Python dependency,
so this tool is suitable for any Cocoa developer.**

``xibless`` runs on Python 2.7 and up. This means that if you're on OS X 10.7 or newer, you can use
the built-in Python. Otherwise, you'll have to install a more recent version of Python.

**Installation and usage:** Please refer to the `Documentation <http://packages.python.org/xibless/>`_
for installation and usage instructions.

Early Development
-----------------

``xibless`` is in very early development and the number of rough edges at the moment are
incalculable. There are no error message for invalid UI scripts, so it might be very hard, for now,
to figure out why your scripts don't work.
