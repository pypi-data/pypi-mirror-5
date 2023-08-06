Tests for pas.plugins.osiris

test setup
----------

    >>> from Testing.ZopeTestCase import user_password
    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()

Plugin setup
------------

    >>> acl_users_url = "%s/acl_users" % self.portal.absolute_url()
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % ('portal_owner', user_password))
    >>> browser.open("%s/manage_main" % acl_users_url)
    >>> browser.url
    'http://nohost/plone/acl_users/manage_main'
    >>> form = browser.getForm(index=0)
    >>> select = form.getControl(name=':action')

pas.plugins.osiris should be in the list of installable plugins:

    >>> 'Osiris Helper' in select.displayOptions
    True

and we can select it:

    >>> select.getControl('Osiris Helper').click()
    >>> select.displayValue
    ['Osiris Helper']
    >>> select.value
    ['manage_addProduct/pas.plugins.osiris/manage_add_osiris_helper_form']

we add 'Osiris Helper' to acl_users:

    >>> from pas.plugins.osiris.plugin import OsirisHelper
    >>> myhelper = OsirisHelper('myplugin', 'Osiris Helper')
    >>> self.portal.acl_users['myplugin'] = myhelper

and so on. Continue your tests here

    >>> 'ALL OK'
    'ALL OK'

