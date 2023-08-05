Overview    
=================================================

"Suds" is a lightweight SOAP-based web service client for Python licensed 
under LGPL (see the LICENSE.txt file included in the distribution).

This fork incorporates changes from several SUDS forks found on Bitbucket and
Github. Eventually the issues from the SUDS issue tracker will be analysed
and, where appropriate, merged into this fork.

  * Forked project information:
   
    * Project site: https://bitbucket.org/philpem/suds
    * Epydocs documentation: needs to be built from sources
    * Official releases can be downloaded from:
   
        * BitBucket - https://bitbucket.org/philpem/suds/downloads
        * PyPI - ``pip install suds-philpem``. Unfortunately because the PyPI
          project name ``suds`` is already taken, packages which require SUDS
          via ``install_requires=['suds']`` in ``setup.py`` will not detect
          ``suds-philpem``. Do not install ``suds`` and ``suds-philpem`` on the
          same system!
          If you can suggest a way to resolve this issue (other than make
          everyone update their ``setup.py`` scripts), please let me know at
          <philpem@gmail.com> and I will post the resolution in the README.
        
    * Forked from `jurko <https://bitbucket.org/jurko/suds>`_, who forked it 
      from the original suds library.

    * Changes merged from the following forks:
        * https://bitbucket.org/palday/suds/
        * https://bitbucket.org/blarghmatey/suds-blarghmatey/
        * https://bitbucket.org/timsavage/suds/
        * https://bitbucket.org/apkawa/suds/
        * https://bitbucket.org/danifus/suds/
        * https://github.com/hheimbuerger/suds-gzip/
  
  * Original suds Python library development project information:
   
    * Project site: https://fedorahosted.org/suds
    * Documentation: https://fedorahosted.org/suds/wiki/Documentation
    * Epydocs: http://jortel.fedorapeople.org/suds/doc

For development notes see the HACKING.txt document included in the
distribution.


Installation
=================================================

Standard Python installation.

Here are the basic instructions for 3 different installation methods:

  #. Using pip:
  
     * Currently not supported: see above notes on PyPI.
     * Theoretically: ``pip install suds-philpem``.
 
  #. Using easy-install: 

     * Currently not supported: see above notes on PyPI.

  #. From sources:

     * Unpack the source package somewhere.
     * Run ``python setup.py install`` from the source distribution's top level folder.


Release Notes
=================================================

version 0.4.3 philpem 1 (2013-01-30)

    * Philip Pemberton
        * Update setup.py to reflect status as a fork-and-merge

    * Henrik Heimbuerger
        * Implemented decompression of error responses (e.g. SOAP faults).
        * Applied patches from suds ticket #318 (with some from #320 mixed in) by Daniel Rodriguez.

    * Daniel Hillier
        * Change exec(...) to execfile.
        * Modify pretty print to differentiate between attributes and params.
        * Add pretty printing for service methods.
        * hack: add option so that output will never be considered wrapped
        * Filter empty parameters in method calls.  [set-attrs]
        * Add patch from ticket #21 from the original suds site.  [set-attrs]
        * Add method to Client to add service not defined in wsdl.  [add-extern-service]

    * apkawa
        * Fixed show Document instance in log as xml (regression)
        * Fixed WebFault with unicode string

    * Tim Savage
        * Fix of local timezone detection code.

    * Phillip Alday
        * Fixed a typo in README.rst
        * More work on README (especially formatting); updated some information in setup.py
        * Changed header case
        * Updated formatting for README.rst. Left original release notes largely alone (no literals); there seems to be some remnants of another ReStructuredText/Markdown/etc type markup language.
        * Converted README to rst format.
        * Added tag release-0.4.2 palday 1 for changeset 6f1d03a18d0f

    * George Sakkis
        * Don't break if error.fp is None
        * Applied fix from https://fedorahosted.org/suds/ticket/292
        * Auto service generation for Exchange ill-formed WSDL.

    * PiWhy
        * Fixed bug when object has no type information in literal.py

    * Guy Rozendorn
        * Fix of log formatting error, originated in the original suds

    * Tobias Macey
        * Updated get_fault in bindings.binding and send in client so it doesnt die if there is no "Fault" tag in the returned XML

    * Baldur Thor Emilsson
        * Stopped using .format as it is not supported for all Python versions that suds supports. 
        * Removed carriage return characters from files (r). They break the install script in Python 2.6 (and probably earlier). 


version 0.4.2 palday 1 (2012-04-16)

    * Fixed an issue with http authentication related to the difference between bytes and str in Python 3.
    * Changed some version information so that the suds dependency is reliably recognized by other installers.
    * Replaced ``jurko`` build tags by ``palday`` and moved it from the ``__version__`` field to the ``__build__`` field.  

version 0.4.1 jurko 4 (2012-04-17)

    * Based on revision 712 from the original suds Python library development
      project's Subversion repository. Last officially packaged & released suds
      Python library version - 0.4.1.
    * Supported Python versions.

        * Basic sources prepared for Python 2.x.
        * For using Python 3 the sources first processed by the Python 2to3 tool
          during the setup procedure.
        * Tested with:

            * Python 2.7.1 on Windows XP, x64.
            * Python 3.2.2 on Windows XP, x64.

        * Intended to work with Python 2.4+.

    * Cleaned up how the distribution package maintainer name string is
      specified so it does not contain characters causing the setup procedure to
      fail when run using Python 3+ on systems using CP1250 or UTF-8 as their
      default code-page.
    * Internal cleanup - renamed bounded to single_occurrence and unbounded to multi_occurrence.
        
        * Original term unbounded meant that its object has more than one
          occurrence while its name inferred that 'it has no upper limit on its
          number of occurrences'.

Prior CHANGELOG entries can by found in the file "CHANGELOG.old".
