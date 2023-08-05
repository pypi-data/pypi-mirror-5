============
herokufu
============

by John Mark Schofield (jms@schof.org)

Provides common utility functions for Django projects on Heroku.

(It's heroku-fu as in Kung Fu, not as in F-U.)



IMPORTANT NOTE:
Please check the version number. This is pre-1.0 software. It's useful as examples of what I'm doing, but not yet ready for general-purpose production. (We're using it in production, but slight differences from our setup may break it.)


Requirements:
You must have vagrant and virtualbox and virtualenvwrapper installed.


Suggested installation workflow:

* Make project directory:
mkdir ~/versoncontrol/PROJECT
cd ~/versioncontrol/PROJECT
git init
django-admin.py createproject or mezzanine createproject
hfu init
edit files in settings directory




Offers the command hfu.

Examples:

hfu manage -- sends command-line arguments to manage.py on runlocal

hfu runlocal -- runs django project in a vagrant/virtualbox VM, accessible via 127.0.0.1:8000

hfu staging_push -- push all assets to staging, creating staging environment if necessary.

hfu staging_manage -- send command-line arguments to manage.py on staging

hfu staging_destroy -- remove staging server, stopping yourself from being charged for it.

hfu test -- Does "hfu staging push," runs tests, and reports on them, then runs "hfu staging destroy"

hfu prod_push -- Does hfu test, and if tests pass, pushes all assets to production

hfu prod_manage -- send command-line arguments to manage.py on prod

hfu prod_reset -- Destroys prod, and then runs "hfu prod push"

hfu prod_revert -- Revert to previous build if most recent prod push has issues. THIS IS A TEMPORARY FIX WHILE YOU FIX THE ISSUE. Do not leave a an app in a reverted state! (This is because dyno changes may create new dynos with the current HEAD, not the reverted state.)