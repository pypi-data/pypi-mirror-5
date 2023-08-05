from zope.interface import implements, Interface

from ZODB.POSException import ConflictError
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.groupmail import groupmailMessageFactory as _


class IGroupView(Interface):
    """
    Group view interface
    """

    def sendmail():
        """Sends an email to a group"""


class GroupView(BrowserView):
    """
    Group browser view
    """
    implements(IGroupView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._group_data = None

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    @property
    def group_info(self):
        if self._group_data is None:
            groupid = self.request.form.get('groupname')
            if not groupid:
                return {'title': 'No Group', 'description': ''}

            group_tool = getToolByName(self.context, 'portal_groups')
            self._group_data = group_tool.getGroupInfo(groupid)
            
        return self._group_data
    
    def get_members(self):
        mtool = getToolByName(self.context, 'portal_membership')
        gtool = getToolByName(self.context, 'portal_groups')

        groupid = self.request.form.get('groupname')
        group = gtool.getGroupById(groupid)
        
        return [mtool.getMemberById(memberid) for memberid in group.getAllGroupMemberIds()]
        

    def sendmail(self, groupname, subject, message, referer=None):
        """Sends an email to a group"""
        plone_utils = getToolByName(self.context, 'plone_utils')
        mtool = getToolByName(self.context, 'portal_membership')
        gtool = getToolByName(self.context, 'portal_groups')
        urltool = getToolByName(self.context, 'portal_url')
        host = getToolByName(self.context, 'MailHost')
        portal = urltool.getPortalObject()
        encoding = portal.getProperty('email_charset')
        
        if referer is None:
            referer = urltool() + '/@@group_view?groupname=' + groupname

        envelope_from = portal.getProperty('email_from_address')
        sender = mtool.getAuthenticatedMember()
        send_from_address = sender.getProperty('email')
        
        if send_from_address == '':
            # happens if you don't exist as user in the portal (but at a higher level)
            # or if your memberdata is incomplete.
            # Would be nicer to check in the feedback form, but that's hard to do securely
            plone_utils.addPortalMessage(_(u'Could not find your email address'), 'error')
            self.request.response.redirect(referer)
        
        sender_id = "%s (%s), %s" % (sender.getProperty('fullname'), sender.getId(), send_from_address)
                
        variables = {'send_from_address' : send_from_address,
                     'sender_id'         : sender_id,
                     'url'               : referer,
                     'subject'           : subject,
                     'message'           : message,
                     'encoding'          : encoding,
                     }
        
        group = gtool.getGroupById(groupname)
        members = group.getAllGroupMemberIds()
        
        addresses = []
        no_email = []
        for memberid in members:
            member = mtool.getMemberById(memberid)
            email = member.getProperty('email')
            if not email:
                no_email.append('%s (%s)' % (memberid, member.getProperty('fullname')))
            else:
                addresses.append(email)
                
        successes = []
        for address in addresses:
            try:
                message = self.context.author_feedback_template(self.context, **variables)
                message = message.encode(encoding)
                result = host.send(message, mto=address, mfrom=envelope_from,
                                   subject=subject, charset=encoding)
                successes.append(address)
            except ConflictError:
                raise
            except: # TODO Too many things could possibly go wrong. So we catch all.
                exception = plone_utils.exceptionString()
                message = _(u'Unable to send mail to ${address}: ${exception}',
                            mapping={u'exception' : exception, u'address': address})
                plone_utils.addPortalMessage(message, 'error')

        if successes:
            plone_utils.addPortalMessage(_(u'Mail sent to') + ' ' + ','.join(successes), 'success')

        if no_email:
            plone_utils.addPortalMessage(_(u'No email found for users') + ' ' + ','.join(no_email), 'warning')
        
        ### clear request variables so form is cleared as well
        #self.request.set('message', None)
        #self.request.set('subject', None)
        self.request.response.redirect(referer)