""" support for HelpCenter container templates """

import Acquisition

from plone.memoize.view import memoize
from zope.component import getAdapter

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

from Products.PloneHelpCenter.utils import PLONE4


# Compare section brains by title
def _sectionCmp(a, b):
    # XXX: convert into an ordering adapter for Plone 4
    # depends on cmp(True, False) == 1
    ash = getattr(a, 'getStartHere', False)
    bsh = getattr(b, 'getStartHere', False)
    if ash == bsh:
        if PLONE4:
            from plone.folder.interfaces import IOrdering
            ordering = getAdapter(Acquisition.aq_parent(a.getObject()), IOrdering)
            try:
                return cmp(ordering.getObjectPosition(a.id), ordering.getObjectPosition(b.id))
            except ValueError:
                # not comparable; these items are probably not in the same folder
                return 0
        else: # Plone 3
            return cmp(a.getObjPositionInParent(), b.getObjPositionInParent())
    elif ash:
        return -1
    else:
        return 1


class HelpCenterFolderView(BrowserView):
    """ support for HelpCenter container templates """

    def __init__(self, context, request):
        """ set up a few convenience object attributes """
        BrowserView.__init__(self, context, request)


    def Versions(self):
        """Method to display the versions in a nicer way."""
        context = Acquisition.aq_inner(self.context)
        return ", ".join(getattr(context, 'versions', []))


    def getItemsBySection(self, section, **kwargs):
        """Get items in this section"""

        context = Acquisition.aq_inner(self.context)

        criteria = {}
        if section == 'No section':
            items = []
            for item in context.getFolderContents(contentFilter = kwargs):
                sections = item.getSections
                if sections and len(sections) < 2:
                    items.append(item)
            return items
        else:
            if isinstance(section, basestring):
                # Wrap in list to avoid solr interpreting sections with spaces
                # as multiple keywords
                criteria['getSections'] = [section]
            else:
                criteria['getSections'] = section
            res = []
            #we have to filter the brains to avoid getting one concerning a minor section when the section is a major section
            # -> we don't want 'major:minor' if only 'major' is searched
            for brain in context.getFolderContents(contentFilter = criteria):
                #the searched section is a major one, we have to check if there's a minor one too"
                if section.find(':') == -1 and len([s for s in brain.getSections if s.startswith('%s:'%section)]):
                    continue
                res.append(brain)
            return res

    def getItemsBySections(self, **kwargs):
        """Get all items to list, by section only. Returns a list of dicts:

        'id'      : A normalised string representing the section
        'section' : The name of the section
        'items'   : A list of catalog brains for items in this section

        The first item will have an section title of 'No section' and contain
        all items with no section selected.
        """

        context = Acquisition.aq_inner(self.context)

        plone_utils = getToolByName(context, 'plone_utils')

        charset = context.getCharset()

        # Set up the dicts listing all sections
        # This is needed because we want it to list the audiences and sections
        # in the order the vocab specifies them.

        sections = []
        for s in ['No section'] + list(context.getSectionsVocab()):
            t = s.encode(charset)
            sections.append({'id'      : plone_utils.normalizeString(t),
                             'section' : t,
                             'items'   : self.getItemsBySection(t, kwargs=kwargs)})

        # Finally clean out empty audiences or sections
        delSections = []
        for j in range(len(sections)):
            if len(sections[j]['items']) == 0:
                delSections.append(j)
        delSections.reverse()
        for j in delSections:
            del sections[j]

        # sort inside sections
        for j in sections:
            j['items'].sort(_sectionCmp)

        return sections


    def getItemsByAudiencesAndSections(self, **kwargs):
        """Get all items to list, by audience and section. Returns a list of
        dicts:

            'audience'  : The name of the audience category
            'sections'  : A list of dicts:

                'id'      : A normalised string representing the section
                'section' : The name of the section
                'items'   : A list of catalog brains for items in this section

        The first item will have an 'audience' title of 'Any audience' and
        contain all items with no audience selected.
        """

        context = Acquisition.aq_inner(self.context)

        plone_utils = getToolByName(context, 'plone_utils')

        contentFilter = {'object_provides':'Products.PloneHelpCenter.interfaces.IHelpCenterContent'}
        brains = context.getFolderContents(contentFilter=contentFilter)

        charset = context.getCharset()

        # Set up the dicts listing all audiences + sections
        # This is needed because we want it to list the audiences and sections
        # in the order the vocab specifies them.
        audiences = []
        for a in ['Any audience'] + list(context.getAudiencesVocab()):
            sections = []
            for s in ['No section'] + list(context.getSectionsVocab()):
                t = s.encode(charset)
                sections.append({'id'      : plone_utils.normalizeString(t),
                                 'section' : t,
                                 'items'   : []})
            audiences.append({'id'       : plone_utils.normalizeString(a),
                              'audience' : a,
                              'sections' : sections})

        # Then insert each how-to in the appropriate audience/section
        for b in brains:
            secs = b.getSections or []
            itemSections = [s for s in secs if s]
            if not itemSections:
                itemSections = ['No section']
            else:
                # we don't want to display an item under both a major and minor
                # section. Presence of a colon indicates a subsection.
                for section in itemSections[:]:
                    cpos = section.find(':')
                    if cpos > 0:
                        try:
                            itemSections.remove(section[:cpos])
                        except ValueError:
                            pass

            itemAudiences = b.getAudiences or ['Any audience']
            matchedAudiences = [a for a in audiences if a['audience'] in itemAudiences]
            if not matchedAudiences:
                # put it in 'Any audience'
                matchedAudiences = [audiences[0]]
            for a in matchedAudiences:
                matchedSections = [s for s in a['sections'] if s['section'] in itemSections]
                if not matchedSections:
                    # put it in 'No section'
                    matchedSections = [a['sections'][0]]
                for s in matchedSections:
                    s['items'].append(b)

        # Finally clean out empty audiences or sections
        delAudiences = []
        for i in range(len(audiences)):
            a = audiences[i]
            delSections = []
            for j in range(len(a['sections'])):
                if len(a['sections'][j]['items']) == 0:
                    delSections.append(j)
            delSections.reverse()
            for j in delSections:
                del a['sections'][j]
            if len(a['sections']) == 0:
                delAudiences.append(i)
        delAudiences.reverse()
        for i in delAudiences:
            del audiences[i]

        # sort inside sections
        for a in audiences:
            for s in a['sections']:
                s['items'].sort(_sectionCmp)

        return audiences


    @memoize
    def getSectionsToList(self, **kwargs):
        """Sections that have at least one listable item. Note that this does
        not take account of audiences.

        May return [] if there are no sections in the vocabulary
        """
        context = Acquisition.aq_inner(self.context)

        sections = {}
        allSections = context.getSectionsVocab()

        if len(allSections) == 0:
            return []

        max_sections = len(allSections)

        for o in context.getFolderContents(contentFilter = kwargs):
            for s in o.getSections:
                if not s: continue #we pass the empty string !
                sections[s]=1
            if len(sections) == max_sections:
                break
        return [s for s in allSections if sections.has_key(s)]
