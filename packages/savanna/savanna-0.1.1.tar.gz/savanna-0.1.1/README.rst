Savanna project
===============

Savanna at wiki.openstack.org: https://wiki.openstack.org/wiki/Savanna

Launchpad project: https://launchpad.net/savanna

Project blueprint: https://savanna.readthedocs.org/en/latest/index.html

Architecture draft: https://savanna.readthedocs.org/en/latest/architecture.html

Roadmap: https://savanna.readthedocs.org/en/latest/roadmap.html

API draft: https://savanna.readthedocs.org/en/latest/restapi/v02.html

QuickStart (Ubuntu)
----------

Please, take a look at https://savanna.readthedocs.org/en/latest/quickstart.html


Pip speedup
-----------

Add the following lines to ~/.pip/pip.conf
::
    [global]
    download-cache = /home/<username>/.pip/cache
    index-url = <mirror url>

Note! The ~/.pip/cache folder should be created.

Git hook for fast checks
------------------------
Just add the following lines to .git/hooks/pre-commit and do chmod +x for it.
::
    #!/bin/sh
    # Run fast checks (PEP8 style check and PyFlakes fast static analysis)
    tools/run_fast_checks

You can added the same check for pre-push, for example, run_tests and run_pylint.

Running static analysis (PyLint)
--------------------------------
Just run the following command
::
    tools/run_pylint

License
-------
Copyright (c) 2013 Mirantis Inc.

Apache License Version 2.0 http://www.apache.org/licenses/LICENSE-2.0
