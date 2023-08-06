from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

import Products.CMFCore.permissions as CMFCorePermissions

from Products import ATContentTypes
from Products.ATContentTypes.interface import IATDocument

from Products.PloneHelpCenter.config import *
from Products.PloneHelpCenter.content.PHCContent import HideOwnershipFields


HelpCenterReferenceManualPageSchema = ATContentTypes.content.document.ATDocumentSchema.copy()
HideOwnershipFields(HelpCenterReferenceManualPageSchema)


class HelpCenterReferenceManualPage(ATContentTypes.content.document.ATDocumentBase):
    """Part of a reference manual."""

    implements(IATDocument)

    schema = HelpCenterReferenceManualPageSchema

    portal_type = meta_type = 'HelpCenterReferenceManualPage'
    archetype_name = 'Manual Page'

    security = ClassSecurityInfo()

    # Satisfy metadata requirements for items with deleted ownership.
    # It would be great to do this in a mixin or adapter,
    # but the structure of Archetypes prevents that.

    security.declareProtected(CMFCorePermissions.View, 'Rights')
    def Rights(self):
        """ get from parent """
        return aq_inner(self).aq_parent.Rights()

    security.declareProtected(CMFCorePermissions.View, 'Creators')
    def Creators(self):
        """ get from parent """
        try:
            return aq_inner(self).aq_parent.Creators()
        except AttributeError:  # parent in not a ReferenceManual
            return ()

    security.declareProtected(CMFCorePermissions.View, 'Contributors')
    def Contributors(self):
        """ get from parent """
        return aq_inner(self).aq_parent.Contributors()

    security.declareProtected(CMFCorePermissions.View, 'listCreators')
    def listCreators(self):
        """ List Dublin Core Creator elements - resource authors.
        """
        return self.Creators()


registerType(HelpCenterReferenceManualPage, PROJECTNAME)
