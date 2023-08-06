Introduction
============

This module patches PloneLanguageTool's getContentLanguage method
to work in a virtual hosting environment such as Plone served by Zope.
The original code uses the variable PATH_TRANSLATED from the request
but that variable has all the VirtualHostBase and domain keywords
used when virtualhosting your Plone site, so this small patch looks
at the request and if the application is run in a virtual hosted
environment, looks at VIRTUAL_URL_PARTS variable and if not at
PATH_TRANSLATED as usual.

This error has been reported to plone-users but has no fix yet.

You'll need PloneLanguageTool 2.1 to have this patch working
Introduction
============


