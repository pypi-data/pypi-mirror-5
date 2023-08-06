============================
 quintagroup.formlib.captcha
============================

This package allows to add captcha to zope.formlib form.
As a result such forms are prevented from automatic submit.

 *example.py* module provides example of usage the *Captcha*
 field with formlib form.

What you have to do
-------------------

1. You should add a *Captcha* field to your schema:

  >>> from zope.interface import Interface
  >>> from quintagroup.formlib.captcha import Captcha
  >>> class ICaptchaFormlibFormSchema(Interface):
  ...     # ... your schema definition
  ...     captcha = Captcha(title=u'Type the code')

2. If your form define Schema adapter (ICaptchaFormlibFormSchema
adapter in our case), just add *captcha* property.

  >>> from zope.component import adapts
  >>> from zope.interface import implements
  >>> class CaptchaFormlibFormAdapter(object):
  ...     adapts(Interface)
  ...     implements(ICaptchaFormlibFormSchema)
  ...     # ... your adapter code
  ...     captcha = None
 
And away we go.

In tests/tests.zcml we have registered a adapter and page view for test form,
named @@formlib-captcha-form.

Get browser object .
    
    >>> from Products.Five.testbrowser import Browser
    >>> from Products.PloneTestCase import PloneTestCase as ptc
    >>> user, pwd = ptc.default_user, ptc.default_password
    >>> browser = Browser()

Now check if captcha presented on the mentioned form.

    >>> browser.open(self.portal.absolute_url() + '/@@formlib-captcha-form')
    >>> open("/tmp/test.html", 'w').write(browser.contents)
    >>> "Type the code" in browser.contents
    True


Now try to submit form with wrong captcha key. Error status message will
be shown.

    >>> browser.open(self.portal.absolute_url() + '/@@formlib-captcha-form')
    >>> browser.getControl(name='form.captcha').value = "wrong captcha"
    >>> browser.getControl(name='form..hashkey').value = self.hashkey
    >>> browser.getControl(name="form.actions.save").click()
    >>> "Type the code" in browser.contents
    True
    >>> "Please re-enter validation code." in browser.contents
    True

And now submit form with correct captcha key.

    >>> browser.open(self.portal.absolute_url() + '/@@formlib-captcha-form')
    >>> browser.getControl(name='form.captcha').value = self.captcha_word
    >>> browser.getControl(name='form..hashkey').value = self.hashkey
    >>> browser.getControl(name="form.actions.save").click()
    >>> "Please re-enter validation code." in browser.contents
    False

No error shown.
