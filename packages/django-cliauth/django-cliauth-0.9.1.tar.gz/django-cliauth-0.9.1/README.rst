Authenticating Apache2 using your Django DB
============================================

* Make sure you have apache2 mod-auth-external installed and configured (See: http://code.google.com/p/mod-auth-external/wiki/Configuration)

* Define django-cliauth as your external authenticator by adding the following line in your virtualhost:

  * DefineExternalAuth django_cliauth pipe "/path/to/your/django-admin.py cliauth --settings="YOUR_PROJECT.settings""
  
* Set your authentication using a .htaccess file (or <Location> inside the virtualhost):

  * AuthType Basic
  * AuthName <authname>
  * AuthBasicProvider external
  * AuthExternal django_cliauth
  * Require valid-user
  
* Reload your apache2 configuration


Checking is the user belongs to a group
========================================

* Define django-cliauth as your external group checker by adding the following to your apache virtualhost:

  * DefineExternalGroup django_cliauth_grpck pipe "/path/to/your/django-admin.py cliauth  --groupcheck --settings='YOUR_PROJECT.settings'"

* Set your authentication using a .htaccess file (or <Location> inside the virtualhost):

  * AuthType Basic
  * AuthName <authname>
  * AuthBasicProvider external
  * AuthExternal django_cliauth
  * GroupExternal django_cliauth_grpck
  * Require group <groupname1> <groupname2> ...

