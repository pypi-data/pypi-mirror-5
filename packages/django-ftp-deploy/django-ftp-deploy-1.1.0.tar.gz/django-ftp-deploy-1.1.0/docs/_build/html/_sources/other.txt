.. _other:

Other
======

Other information for django-ftp-deploy module

Email Notifications
-------------------

The email notification system provides html and text templates that can be overriden if you wish. In order to do that you need to create your own templates for success and fail notification separately::


  /ftp_deploy/email/email_success.html
  /ftp_deploy/email/email_success.txt

  /ftp_deploy/email/email_fail.html
  /ftp_deploy/email/email_fail.txt


All templates are rendered with the following context information:

``Success Template``
  | - *{{service}}* object
  | - *{{host}}* of the current website (where the email came from)
  | - *{{commits_info}}* in format [['commit message','commit user','raw node'],[...]]
  | - *{{files_added}}* , *{{files_modified}}*, *{{files_removed}}* in format ['file_name_1', 'file_name_2', ...]


``Fail Template``
  | - *{{service}}* object
  | - *{{host}}* of the current website (where the email came from)
  | - *{{error}}* message of the exception


Screens
-------

All screens are only for preview purposes, and may be different then original application.

1. Dashboard
************

.. image:: images/dashboard.png

2. Manage
*********
  
.. image:: images/manage.png

3. Restore
**********
  
.. image:: images/restore.png

4. Log
******
  
.. image:: images/log.png

   
  

