# -*- coding: utf-8 -*-
from OFS.SimpleItem import SimpleItem
from Products.PlonePAS.Extensions.Install import activatePluginInterfaces
from Products.PluggableAuthService.plugins import DomainAuthHelper


class RemoteKeywordsLibrary(SimpleItem):
    """Robot Framework Remote Library Tool for Plone

    See also: http://robotframework.googlecode.com/hg/doc/userguide/RobotFrameworkUserGuide.html?r=2.7.65#remote-library-interface

    """
    def get_keyword_names(self):
        """Return names of the implemented keywords
        """
        blacklist = dir(SimpleItem)
        blacklist.extend(['get_keyword_names', 'run_keyword'])
        names = filter(lambda x: x[0] != '_' and x not in blacklist, dir(self))
        return names

    def run_keyword(self, name, args):
        """Execute the specified keyword with given arguments.
        """
        func = getattr(self, name, None)
        result = {'error': '', 'return': ''}
        try:
            retval = func(*args)
        except Exception, e:
            result['status'] = 'FAIL'
            result['error'] = str(e)
        else:
            result['status'] = 'PASS'
            result['return'] = retval
            result['output'] = retval
        return result

    def product_is_activated(self, product_name):
        """Assert that given product_name is activated in
        portal_quickinstaller.

        """
        from Products.CMFCore.utils import getToolByName
        quickinstaller = getToolByName(self, "portal_quickinstaller")
        assert quickinstaller.isProductInstalled(product_name),\
            "Product '%s' was not installed." % product_name

    def enable_autologin_as(self, *args):
        """Add and configure DomainAuthHelper PAS-plugin to login
        all anonymous users from localhost as a special *Remote User* with
        one or more given roles. Examples of use::

            Enable autologin as  Manager
            Enable autologin as  Site Administrator
            Enable autologin as  Member  Contributor

        """
        if "robot_login" in self.acl_users.objectIds():
            self.acl_users.robot_login._domain_map.clear()
        else:
            DomainAuthHelper.manage_addDomainAuthHelper(
                self.acl_users, "robot_login")
            activatePluginInterfaces(self, "robot_login")
        user = ", ".join(sorted(args))
        self.acl_users.robot_login.manage_addMapping(
            match_type="regex", match_string=".*", roles=args, username=user)

    def set_autologin_username(self, login):
        """Update autologin mapping with the given username
        """
        if "robot_login" not in self.acl_users.objectIds():
            raise Exception(u"Autologin is not enabled")
        if len(self.acl_users.robot_login._domain_map) == 0:
            raise Exception(u"Autologin is not enabled")
        domain_map_key = self.acl_users.robot_login._domain_map.keys()[0]
        domain_map = self.acl_users.robot_login._domain_map[domain_map_key]
        domain_map[0]["user_id"] = domain_map[0]["username"] = login
        self.acl_users.robot_login._domain_map[domain_map_key] = domain_map

    def disable_autologin(self):
        """Clear DomainAuthHelper's map to effectively 'logout' user
        after 'autologin_as'. Example of use::

            Disable autologin

        """
        if "robot_login" in self.acl_users.objectIds():
            self.acl_users.robot_login._domain_map.clear()

    def portal_type_is_installed(self, portal_type):
        ids = self.portal_types.objectIds()
        titles = map(lambda x: x.title, self.portal_types.objectValues())
        assert portal_type in ids + titles,\
            u"'%s' was not found in portal types." % portal_type

    def change_ownership(self, path, user_id):
        from AccessControl.interfaces import IOwned
        obj = self.restrictedTraverse(path)

        acl_users = self.get('acl_users')
        if acl_users:
            user = acl_users.getUser(user_id)
        if not user:
            root = self.getPhysicalRoot()
            acl_users = root.get('acl_users')
            if acl_users:
                user = acl_users.getUser(user_id)

        IOwned(obj).changeOwnership(user, recursive=1)

    def create_type_with_date_field(self, name):
        from plone.dexterity.fti import DexterityFTI
        fti = DexterityFTI(str(name), title=name)
        fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IBasic",)
        fti.model_source = u"""\
<model xmlns="http://namespaces.plone.org/supermodel/schema">
<schema>
<field name="duedate" type="zope.schema.Date">
  <description />
  <required>False</required>
  <title>Due Date</title>
</field>
</schema>
</model>"""
        self.portal_types._setObject(str(name), fti)

    def report_sauce_status(self, job_id, test_status, test_tags=[]):
        import os
        import httplib
        import base64
        try:
            import json
            json  # pyflakes
        except ImportError:
            import simplejson as json

        username = os.environ.get('SAUCE_USERNAME')
        access_key = os.environ.get('SAUCE_ACCESS_KEY')

        if not job_id:
            return u"No Sauce job id found. Skipping..."
        elif not username or not access_key:
            return u"No Sauce environment variables found. Skipping..."

        token = base64.encodestring('%s:%s' % (username, access_key))[:-1]
        body = json.dumps({'passed': test_status == 'PASS',
                           'tags': test_tags})

        connection = httplib.HTTPConnection('saucelabs.com')
        connection.request('PUT', '/rest/v1/%s/jobs/%s' % (
            username, job_id), body,
            headers={'Authorization': 'Basic %s' % token}
        )
        return connection.getresponse().status
