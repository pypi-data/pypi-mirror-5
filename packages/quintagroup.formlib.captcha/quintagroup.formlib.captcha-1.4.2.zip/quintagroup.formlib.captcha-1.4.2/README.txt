Introduction
============

quintagroup.formlib.captcha is a package that allows to add captcha to zope.formlib.
As a result such forms are prevented from automatic submit.

Captchas in a formlib form
--------------------------

Using quintagroup.formlib.captcha in a formlib form is simple. Just add a
Captcha field to your schema, and away you go:

  >>> from zope.interface import Interface
  >>> from quintagroup.formlib.captcha import Captcha
  >>> class CaptchaSchema(Interface):
  ...     captcha = Captcha(
  ...         title=_(u'Type the code'),
  ...         description=_(u'Type the code from the picture shown below.'))

and formlib will take care of the rest. The widget associated with this field 
will render the captcha and verify the use input automatically.

Supported Plone versions
------------------------

quintagroup.formlib.captcha was tested with Plone 3.x and Plone 4.0.

Authors
-------

* Vitaliy Podoba
* Andriy Mylenkyi
* Vitaliy Stepanov

Copyright (c) "Quintagroup": http://quintagroup.com, 2004-2010
