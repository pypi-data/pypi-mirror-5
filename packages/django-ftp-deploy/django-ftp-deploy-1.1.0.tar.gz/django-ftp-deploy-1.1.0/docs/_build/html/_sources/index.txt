.. Django FTP Deploy documentation master file, created by
   sphinx-quickstart on Mon Oct  7 18:49:46 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Django FTP Deploy Documentation
============================================

django-ftp-deploy allows you to automatically deploy GIT repositories to FTP servers. You don't need to install git on the server!

.. warning:: Version 1.1 is completely rewritten and not back compatible with version 1.0


**Features:**

* Services Dashboard (a service is one repository-to-ftp configuration)
* Manage Multiple Services
* Verification Services Configurations
* Repository Hook Management
* Dynamic Loading of Repository list
* Restore Failed Deploys
* Configurable Email Notifications
* Statistics of Deployments
* Deployment Logs


Supported GIT repositories:

* Bitbucket
* Github (planned)


User Guide
----------


.. toctree::
   :maxdepth: 2

   installation
   usage
   other

Developer Guide
---------------

.. toctree::
   :maxdepth: 4

   api/ftp_deploy
   api/ftp_deploy.server


TO-DO
-----  
*v1.3*

* Github support

*v1.2*

* login screen
* cron services validation
* email notification configuration per service




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

