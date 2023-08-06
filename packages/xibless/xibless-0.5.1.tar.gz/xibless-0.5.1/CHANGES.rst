Changes
=======

Version 0.5.1 -- 2013/11/10
---------------------------

Version 0.5.0 -- 2012/10/08
---------------------------

* Added VHLayout.
* Added Box.
* In View, added delegate, fixedHeight, fixedWidth and accessibilityDescription attributes as well
  as moveTo() (a more powerful version of packToCorner()) and fillAll() methods.
* In Segment, added image and accessibilityDescription attributes.
* Added SplitView.dividerStyle and added documentation for a direct split view hierarchy.
* Added TableView.borderType and View.focusRingType.
* Added Button.bordered
* Added MenuItem.state
* Added TabView.tabViewType.
* Added TextField.usesSingleLineMode.
* Added margin and align arguments to layouts.
* Deprecated View.packToCorner().
* Layouts can now contain sublayouts.
* Allow Color() to receive values in the range of 0-255 in addition to 0.0-1.0.
* Don't localize strings containing only "-" (they're used to indicate a separator menu item).
* RadioButtons' height now depends on the number of rows it has.
* Fixed filler resizing in layouts in cases where there are other views next to the filler.
* Allow UI scripts to import units that are from the same folder.
* Replaced Button.keyEquivalent with Button.shortcut.
* Fixed runtemplate so that the XiblessSupport unit is compiled in the RunUI executable.
* Fixed a bug where we would sometimes end up with two generated item with the same varname.
* Always set growX/growY to False in setAnchor() for views that have a fixed width/height.
* The "text" argument of TextField's constructor is now optional.
* Support sides and middle in View.setAnchor().
* Generated units now have a comment indicating generation time and xibless version.
* Moved TextField.alignment down to Control
* Only copy XiblessSupport unit when it changed, thus avoiding needless recompilation.
* Fixed TabView's layout deltas for cases where there's no tabs.
* Support shortcuts involving the '+' character.
* Improved default margins in layouts, control heights and all other little tweaks of this sort.

Version 0.4.1 -- 2012/08/08
---------------------------

* Added NLSTR to UI scripts namespace.
* Don't wrap Window.autosaveName in localization calls.
* Fixed a bug causing some strings not to be wrapped in localization calls.
* Set RadioButton's "autosizesCells" to True upon creation.

Version 0.4.0 -- 2012/07/30
---------------------------

* Added Panel, SplitView, OutlineView, ListView, Toolbar, SegmentedControl, SearchField, Slider
  and NumberFormatter.
* Added Layouts.
* Added support for many, many, many new attributes, constants and types.
* Now generates a ".h" to go alongside the generated unit.
* Added Property and its subclasses, an easier way to add support for new attributes, even the
  complex ones.
* It's now possible to override margins in layout method calls.
* Added support for bindings with the new ``View.bind()`` method.
* Added the new ``defaults`` global variable, which can be used to bind to user defaults.
* Constants accessed with ``const`` can now be bitwise OR-ed.
* Generated code is now formatted to look a bit better and be easier to debug.
* Added new constants for menu shortcuts for special keys (arrows, enter etc.).
* Added support for UI script arguments.


Version 0.3.1 -- 2012/07/20
---------------------------

* Pushed down the `action` attribute from `Button` to `Control`.
* `RadioButtons` is now a `Control` subclass.
* Made window recalculate its view loop after having generated its children.

Version 0.3.0 -- 2012/07/09
---------------------------

* Added RadioButtons, TableView, TabView, TextView, ImageView and ProgressIndicator.
* Added support for string localization.
* Added TextField.alignment and TextField.textColor.
* Added Button.keyEquivalent.
* Added canClose, canResize and canMinimize to Window.
* Added a Control subclass.
* View can now be directly instantiated in UI scripts (They're like "Custom Views" in IB).
* `xibless run` can now be run on script for which the result is a View.
* Improved layout system.
* Window origin is now supplied in terms of screen proportions rather than absolute positions.
* Fixed 'id' ownerclass in main function prototype generation and added the "ownerimport" global
  variable in the UI script.
* Escape newlines in string code generation.
* Added documentation for Button.buttonType and Button.bezelStyle and added a demo for a button
  with a different bezel style.
* Fixed the most glaring memory leaks.
* Fixed a bug where attributes like class-level default fonts wouldn't be generated when generating
  more than one UI script in the same python session.
* Windows are not released when closed by default.
* Added support for circular references (a window setting one of its properties to an item that
  required that window before being created, for example, initialFirstResponder). We previously
  couldn't generate code for such bindings.
* Made the `align` argument in `View.packRelativeTo()` optional.

Version 0.2.0 -- 2012/06/28
---------------------------

* Added Sphinx documentation
* Added the ``xibless run`` command for quick UI previews.
* Added Combobox and Popup.

Version 0.1.0 -- 2012/06/25
---------------------------

* Initial pre-alpha release