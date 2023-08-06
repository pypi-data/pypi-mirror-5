#
# Tests for PHC and the Comment (discussion or talkback) system
#

try:
    from email.parser import Parser
    Parser  # pyflakes
except ImportError:  # Plone 3, Python 2.4.
    from email.Parser import Parser

from Products.CMFCore.utils import getToolByName
from Products.PloneHelpCenter.tests import PHCTestCase

try:
    from Products.CMFPlone.tests.utils import MockMailHost
    MockMailHost  # pyflakes
except ImportError:
    MockMailHost = None
from Products.PloneHelpCenter.utils import discussion_notify
from Products.PloneHelpCenter.utils import PLONE4


class TestTutorialPageComments(PHCTestCase.PHCTestCase):
    """Tests related to a bug where comments on objects in a PHC Tutorial's
    items were shoting up on the tutorial itself."""

    def afterSetUp(self):
        PHCTestCase.PHCTestCase.afterSetUp(self)
        self.tf = self.folder.hc.tutorial  # tutorial folder
        self.tf.invokeFactory('HelpCenterTutorial', id='t')
        self.tutorial = self.tf.t
        self.tutorial.invokeFactory('HelpCenterLeafPage', 'page1')
        self.tutorial.invokeFactory('HelpCenterLeafPage', 'page2')
        self.tutorial.invokeFactory('HelpCenterLeafPage', 'page3')
        # turn on discussion
        self.tutorial.allowDiscussion(allowDiscussion=True)
        self.tutorial.page1.allowDiscussion(allowDiscussion=True)
        self.tutorial.page2.allowDiscussion(allowDiscussion=True)
        self.tutorial.page3.allowDiscussion(allowDiscussion=True)

    def testCommentOnTutorialPage(self):
        title = 'Test comment'
        body = 'head\nbody\nlegs\n'
        discussionTool = getToolByName(self.portal, 'portal_discussion')
        # turn on discussion
        self.tutorial.page2.allowDiscussion(allowDiscussion=True)
        # set up the talkback subobject
        discussionTool.getDiscussionFor(self.tutorial.page2)
        # create a comment on the tutorial page
        self.tutorial.page2.discussion_reply(subject=title, body_text=body,)
        # verify that we can get it back on the page
        talkback = discussionTool.getDiscussionFor(self.tutorial.page2)
        comment = talkback.objectValues()[0]
        self.assertEqual(comment.Title(), title)
        self.assertEqual(comment.EditableBody(), body)
        # verify that the comment doesn't show up on the parent tutorial object
        talkback = discussionTool.getDiscussionFor(self.tutorial)
        self.assertEqual(talkback.objectValues(), [])
        # verify that the comment doesn't show up on the other tutorial pages
        talkback = discussionTool.getDiscussionFor(self.tutorial.page1)
        self.assertEqual(talkback.objectValues(), [])
        talkback = discussionTool.getDiscussionFor(self.tutorial.page3)
        self.assertEqual(talkback.objectValues(), [])

    def testCommentOnTutorialFolder(self):
        title = 'Test folder comment'
        body = 'head\nbody\nlegs\n'
        discussionTool = getToolByName(self.portal, 'portal_discussion')
        # set up the talkback subobject
        discussionTool.getDiscussionFor(self.tutorial)
        # create a comment on the tutorial
        self.tutorial.discussion_reply(subject=title, body_text=body,)
        # verify that we can get it back on the tutorial
        talkback = discussionTool.getDiscussionFor(self.tutorial)
        comment = talkback.objectValues()[0]
        self.assertEqual(comment.Title(), title)
        self.assertEqual(comment.EditableBody(), body)
        # verify that the comment doesn't show up on any of the tutorial pages
        talkback = discussionTool.getDiscussionFor(self.tutorial.page1)
        self.assertEqual(talkback.objectValues(), [])
        talkback = discussionTool.getDiscussionFor(self.tutorial.page2)
        self.assertEqual(talkback.objectValues(), [])
        talkback = discussionTool.getDiscussionFor(self.tutorial.page3)
        self.assertEqual(talkback.objectValues(), [])


class MockMailHostTests(PHCTestCase.PHCTestCase):

    def afterSetUp(self):
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost('MailHost')
        PHCTestCase.PHCTestCase.afterSetUp(self)
        self.tf = self.folder.hc.tutorial  # tutorial folder
        self.tf.invokeFactory('HelpCenterTutorial', id='t')
        self.tutorial = self.tf.t
        self.tutorial.invokeFactory('HelpCenterLeafPage', 'page1')

    def beforeTearDown(self):
        self.portal.MailHost = self.portal._original_MailHost

    def testCommentMailing(self):
        """ Make sure we're mailing comments """

        mailhost = self.portal.MailHost
        self.assertEqual(len(mailhost.messages), 0)

        # try to notify
        discussion_notify(self.tutorial.page1)
        # there is no sendto address, so we expect no outgoing mail
        self.assertEqual(len(mailhost.messages), 0)

        # set an owner email address and try again
        owner = self.tutorial.page1.Creator()
        member = self.portal.portal_membership.getMemberById(owner)
        member.setMemberProperties({'fullname': 'fullname', 'email': 'testuser@testme.com', })
        discussion_notify(self.tutorial.page1)
        self.assertEqual(len(mailhost.messages), 1)

        if PLONE4:
            msg_text = mailhost.messages[0]
            parser = Parser()
            msg = parser.parsestr(msg_text)
            msgTo = msg['To']
            msgSubject = msg['subject']
            payload = msg.get_payload()
        else:
            msg = mailhost.messages[0]
            msgTo = msg.mto[0]
            msgSubject = msg.message['subject']
            payload = msg.message.get_payload().decode('base64')

        self.failUnlessEqual(msgTo, 'testuser@testme.com')
        self.failUnlessEqual(msgSubject, '=?utf-8?q?New_comment_on_page1?=')
        self.failUnless(payload.find('Someone added a comment on your HelpCenterLeafPage:\npage1.') > 0)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTutorialPageComments))
    if MockMailHost:
        suite.addTest(makeSuite(MockMailHostTests))
    return suite
