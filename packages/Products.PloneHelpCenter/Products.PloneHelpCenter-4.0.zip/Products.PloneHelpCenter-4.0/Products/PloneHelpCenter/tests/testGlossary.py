#
# Tests for Glossary types in the PHC
#

from Products.PloneHelpCenter.tests import PHCTestCase


class TestGlossary(PHCTestCase.PHCTestCase):
    """General tests for Glossary and Definition objects."""

    def afterSetUp(self):
        PHCTestCase.PHCTestCase.afterSetUp(self)
        self._createDefinition(self.folder.hc.glossary, 'd')
        self.definition = self.folder.hc.glossary.d

    def testInitialSections(self):
        # Test that the default section list is correct.
        self.assertEqual(self.definition.getSections(), ('General',))

    def testVersionsonGlossary(self):
        versions = ('1.0', '2.0', 'Strange version')
        self.folder.hc.setVersionsVocab(versions)
        newVersions = self.definition.getVersionsVocab()
        self.assertEqual(newVersions, versions)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestGlossary))
    return suite
