from zope.interface import implements
from AccessControl import ClassSecurityInfo

try:
    from Products.LinguaPlone.public import *
except ImportError:
    # No multilingual support
    from Products.Archetypes.public import *

from Products.PloneHelpCenter.config import *
from Products.PloneHelpCenter.interfaces import IHelpCenterHowTo
from schemata import HelpCenterItemSchemaNarrow
from PHCContent import PHCContentMixin, HideOwnershipFields, IHelpCenterContent

from Products.ATContentTypes.interface import IATFolder, IATDocument
from Products.ATContentTypes.content.document import \
    ATDocumentSchema, ATDocumentBase
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema
from Products.ATContentTypes.content.base import ATCTOrderedFolder


# Create a Frankenstein's monster: a hybrid of ATCT
# folder and document types.
# Since the document type is more complex, we'll use it for the base.

HowToSchema = ATDocumentSchema.copy() + ConstrainTypesMixinSchema + HelpCenterItemSchemaNarrow
HideOwnershipFields(HowToSchema)
finalizeATCTSchema(HowToSchema, folderish=True, moveDiscussion=False)


class HelpCenterHowTo(ATDocumentBase, PHCContentMixin, ATCTOrderedFolder):

    """A How-to is a document describing how to address a single, common
    use-case or issue. You may add images and files as attachments.
    """

    implements(IATFolder, IATDocument, IHelpCenterHowTo, IHelpCenterContent)

    isPrincipiaFolderish = True

    content_icon = 'howto_icon.gif'

    typeDescription= 'A How-to is a document describing how to address a single, common use-case or issue. You may add images and files as attachments.'
    typeDescMsgId = 'description_edit_howto'

    schema = HowToSchema
    archetype_name = 'How-to'
    meta_type = 'HelpCenterHowTo'

    security = ClassSecurityInfo()

    security.declarePublic('canSetDefaultPage')
    def canSetDefaultPage(self):
        """Check if the user has permission to select a default page on this
        (folderish) item, and the item is folderish.
        """
        return False

registerType(HelpCenterHowTo, PROJECTNAME)
