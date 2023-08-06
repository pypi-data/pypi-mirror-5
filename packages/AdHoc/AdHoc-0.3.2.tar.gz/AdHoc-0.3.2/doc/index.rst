AdHoc Standalone Python Script Generator
########################################

The *AdHoc* compiler can be used as a program (see `Script Usage`_)
as well as a module (see :class:`adhoc.AdHoc`).

Since the *AdHoc* compiler itself is installed as a compiled *AdHoc*
script, it serves as its own usage example.

After installation of the *adhoc.py* script, the full source can be
obtained in directory ``__adhoc__``, by executing::

    adhoc.py --explode

.. @@contents@@


Purpose
=======

*AdHoc* provides python scripts with

- template facilities
- default file generation
- standalone module inclusion

See also `Use Cases`_.

*AdHoc* has been designed to provide an implode/explode cycle:

========  =======  =========  =======  =========
source_0                               xsource_0
source_1  implode             explode  xsource_1
...       ------>  script.py  ------>  ...
source_n                               xsource_n
========  =======  =========  =======  =========

where ``xsource_i === source_i``. I.e., ``diff source_i xsource_i``
does not produce any output.

Quickstart
==========

module.py:

    | # -\*- coding: utf-8 -\*-
    | mvar = 'value'

script.py:

    | # -\*- coding: utf-8 -\*-
    | # |adhoc_run_time|
    | import module # |adhoc|
    | print('mvar: ' + module.mvar)

Compilation::

    adhoc.py --compile script.py >/tmp/script-compiled.py

Execution outside source directory::

    cd /tmp && python script-compiled.py

shows::

    mvar: value

Decompilation::

    cd /tmp && \
    mkdir -p __adhoc__ && \
    adhoc.py --decompile <script-compiled.py >__adhoc__/script.py

.. |@:| replace:: ``@:``
.. |:@| replace:: ``:@``
.. |adhoc_run_time| replace:: |@:|\ ``adhoc_run_time``\ |:@|
.. |adhoc| replace:: |@:|\ ``adhoc``\ |:@|

Description
===========

The *AdHoc* compiler/decompiler parses text for tagged lines and
processes them as instructions.

The minimal parsed entity is a tagged line, which is any line
containing a recognized *AdHoc* tag.

All *AdHoc* tags are enclosed in delimiters (default: |@:| and |:@|). E.g:

  |@:|\ adhoc\ |:@|

Delimiters come in several flavors, namely line and section
delimiters and a set of macro delimiters. By default, line and
section delimiters are the same, but they can be defined separately.

`Flags`_ are tagged lines, which denote a single option or
command. E.g.:

  | import module     # |@:|\ adhoc\ |:@|
  | # |@:|\ adhoc_self\ |:@| my_module_name

`Sections`_ are tagged line pairs, which delimit a block of
text. The first tagged line opens the section, the second tagged
line closes the section. E.g.:

  | # |@:|\ adhoc_enable\ |:@|
  | # disabled_command()
  | # |@:|\ adhoc_enable\ |:@|

`Macros`_ have their own delimiters (default: |@m| and |m>|). E.g.:

  | # |@m|\ MACRO_NAME\ |m>|

The implementation is realized as class :class:`adhoc.AdHoc` which
is mainly used as a namespace. The run-time part of
:class:`adhoc.AdHoc` -- which handles module import and file export
-- is included verbatim as class :class:`RtAdHoc` in the generated
output.

Flags
-----

:|adhoc_run_time|:
    The place where the *AdHoc* run-time code is added.  This flag must
    be present in files, which use the |adhoc| import feature.  It
    is not needed for the enable/disable features.

    This flag is ignored, if double commented. E.g.:

      | # # |adhoc_run_time|

:|adhoc| [force] [flat | full]:
    Mark import line for run-time compilation.

    If ``force`` is specified, the module is imported, even if it
    was imported before.

    If ``flat`` is specified, the module is not recursively
    exported.

    If ``full`` is specified, the module is recursively
    exported. (This parameter takes priority over ``flat``).

    If neither ``flat`` nor ``full`` are specified,
    :attr:`adhoc.AdHoc.flat` determines the export scope.

    This flag is ignored, if the line is commented out. E.g.:

      | # import module  # |adhoc|

.. _adhoc_include:

:|adhoc_include| file_spec, ...:
    Include files for unpacking. ``file_spec`` is one of

    :file:
      ``file`` is used for both input and output.

    :file ``from`` default-file:
      ``file`` is used for input and output. if ``file`` does not
      exist, ``default-file`` is used for input.

    :source-file ``as`` output-file:
      ``source-file`` is used for input. ``output-file`` is used for
      output. If ``source-file`` does not exist, ``output-file`` is
      used for input also.

    This flag is ignored, if double commented. E.g.:

      | # # |adhoc_include| file

:|adhoc_verbatim| [flags] file_spec, ...:
    Include files for verbatim extraction. See adhoc_include_ for
    ``file_spec``.

    The files are included as |adhoc_template_v| sections. *file* is used
    as *export_file* mark. If *file* is ``--``, the template disposition
    becomes standard output.

    Optional flags can be any combination of ``[+|-]NUM`` for
    indentation and ``#`` for commenting. E.g.:

      | # |adhoc_verbatim| +4# my_file from /dev/null

    *my_file* (or ``/dev/null``) is read, commented and indented 4
    spaces.

    If the |adhoc_verbatim| tag is already indented, the specified
    indentation is subtracted.

    This flag is ignored, if double commented. E.g.:

      | # # |adhoc_verbatim| file

:|adhoc_self| name ...:
    Mark name(s) as currently compiling.  This is useful, if
    ``__init__.py`` imports other module parts. E.g:

      | import pyjsmo             # |@:|\ adhoc\ |:@|

    where ``pyjsmo/__init__.py`` contains:

      | # |@:|\ adhoc_self\ |:@| pyjsmo
      | from pyjsmo.base import * # |@:|\ adhoc\ |:@|

:|adhoc_compiled|:
    If present, no compilation is done on this file. This flag is
    added by the compiler to the run-time version.

Sections
--------

:|adhoc_enable|:
    Leading comment char and exactly one space are removed from lines
    in these sections.

:|adhoc_disable|:
    A comment char and exactly one space are added to non-blank
    lines in these sections.

:|adhoc_template| -mark | export_file:
    If mark starts with ``-``, the output disposition is standard output
    and the template is ignored, when exporting.

    Otherwise, the template is written to output_file during export.

    All template parts with the same mark/export_file are concatenated
    to a single string.

:|adhoc_template_v| export_file:
    Variation of |adhoc_template|. Automatically generated by |adhoc_verbatim|.

:|adhoc_uncomment|:
    Treated like |adhoc_enable| before template output.

:|adhoc_indent| [+|-]NUM:
    Add or remove indentation before template output.

:|adhoc_import|:
    Imported files are marked as such by the compiler. There is no
    effect during compilation.

:|adhoc_unpack|:
    Included files are marked as such by the compiler. There is no
    effect during compilation.

:|adhoc_remove|:
    Added sections are marked as such by the compiler. Removal is
    done when exporting.

    Before compilation, existing |adhoc_remove| tags are renamed to
    |adhoc_remove_|.

    After automatically added |adhoc_remove| sections have been
    removed during export, remaining |adhoc_remove_| tags are
    renamed to |adhoc_remove| again.

    .. note:: Think twice, before removing material from original
       sources at compile time. It will violate the condition
       ``xsource_i === source_i``.

:|adhoc_run_time_engine|:
    The run-time class :class:`RtAdHoc` is enclosed in this special
    template section.

    It is exported as ``rt_adhoc.py`` during export.

Macros
------

Macros are defined programmatically::

    AdHoc.macros[MACRO_NAME] = EXPANSION_STRING

A macro is invoked by enclosing a MACRO_NAME in
:attr:`adhoc.AdHoc.macro_call_delimiters`. (Default: |@m|, |m>|).

:|MACRO_NAME|:
    Macro call.

Internal
--------

:|adhoc_run_time_class|:
    Marks the beginning of the run-time class.  This is only
    recognized in the *AdHoc* programm/module.

:|adhoc_run_time_section|:
    All sections are concatenated and used as run-time code.  This is
    only recognized in the *AdHoc* programm/module.

In order to preserve the ``xsource_i === source_i`` bijective
condition, macros are expanded/collapsed with special macro
definition sections. (See :attr:`adhoc.AdHoc.macro_xdef_delimiters`;
Default: |<m|, |m@|).

:|adhoc_macro_call|:
    Macro call section.

:|adhoc_macro_expansion|:
    Macro expansion section.


.. include:: USE_CASES.txt

AdHoc Script
============

.. automodule:: adhoc
    :members:
    :show-inheritance:

.. _namespace_dict:

NameSpace/NameSpaceDict
=======================

.. automodule:: namespace_dict
    :members:
    :show-inheritance:


.. |adhoc_self| replace:: |@:|\ ``adhoc_self``\ |:@|
.. |adhoc_include| replace:: |@:|\ ``adhoc_include``\ |:@|
.. |adhoc_verbatim| replace:: |@:|\ ``adhoc_verbatim``\ |:@|
.. |adhoc_compiled| replace:: |@:|\ ``adhoc_compiled``\ |:@|
.. |adhoc_enable| replace:: |@:|\ ``adhoc_enable``\ |:@|
.. |adhoc_disable| replace:: |@:|\ ``adhoc_disable``\ |:@|
.. |adhoc_template| replace:: |@:|\ ``adhoc_template``\ |:@|
.. |adhoc_template_v| replace:: |@:|\ ``adhoc_template_v``\ |:@|
.. |adhoc_uncomment| replace:: |@:|\ ``adhoc_uncomment``\ |:@|
.. |adhoc_indent| replace:: |@:|\ ``adhoc_indent``\ |:@|
.. |adhoc_import| replace:: |@:|\ ``adhoc_import``\ |:@|
.. |adhoc_unpack| replace:: |@:|\ ``adhoc_unpack``\ |:@|
.. |adhoc_remove| replace:: |@:|\ ``adhoc_remove``\ |:@|
.. |adhoc_remove_| replace:: |@:|\ ``adhoc_remove_``\ |:@|
.. |adhoc_run_time_class| replace:: |@:|\ ``adhoc_run_time_class``\ |:@|
.. |adhoc_run_time_section| replace:: |@:|\ ``adhoc_run_time_section``\ |:@|
.. |adhoc_run_time_engine| replace:: |@:|\ ``adhoc_run_time_engine``\ |:@|
.. |@m| replace:: ``@|:``
.. |m>| replace:: ``:|>``
.. |<m| replace:: ``<|:``
.. |m@| replace:: ``:|@``
.. |MACRO_NAME| replace:: |@m|\ ``MACRO_NAME``\ |m>|
.. |adhoc_macro_call| replace:: |<m|\ ``adhoc_macro_call``\ |m@|
.. |adhoc_macro_expansion| replace:: |<m|\ ``adhoc_macro_expansion``\ |m@|

