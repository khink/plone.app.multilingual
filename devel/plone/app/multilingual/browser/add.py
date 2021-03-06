from plone.dexterity.browser.add import DefaultAddForm, DefaultAddView
from plone.app.multilingual.dx.interfaces import ILanguageIndependentField

from plone.z3cform import layout
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.multilingual.browser.selector import LanguageSelectorViewlet
from plone.app.i18n.locales.browser.selector import LanguageSelector


from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from plone.app.multilingual.interfaces import IMultiLanguageExtraOptionsSchema


from zope.component import adapts
from zope.component import queryMultiAdapter
from zope.interface import implements
from zope.interface import Interface
from zope.traversing.interfaces import ITraversable
from zope.traversing.interfaces import TraversalError
from plone.dexterity.interfaces import IDexterityFTI

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView


class AddViewTraverser(object):

    """Add view traverser.
    """

    adapts(IFolderish, Interface)
    implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignored):
        ttool = getToolByName(self.context, 'portal_types')
        ti = ttool.getTypeInfo(name)
        if not IDexterityFTI.providedBy(ti):
            # we are not on DX content
            baseUrl = self.context.absolute_url()
            url = '%s/@@add_at_translation?type=%s' % (baseUrl, name)
            return self.request.response.redirect(url)
        # set the self.context to the place where it should be stored
        if not IFolderish.providedBy(self.context):
            self.context = self.context.__parent__
        if ti is not None:
            add_view = queryMultiAdapter((self.context, self.request, ti),
                                         name='babel_view')
            if add_view is None:
                add_view = queryMultiAdapter((self.context, self.request, ti))
            if add_view is not None:
                add_view.__name__ = ti.factory
                return add_view.__of__(self.context)

        raise TraversalError(self.context, name)



# Dexteity form

class MultilingualAddForm(DefaultAddForm):

    babel = ViewPageTemplateFile("templates/dexterity_edit.pt")

    def gtenabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.google_translation_key != ''

    def portal_url(self):
        portal_tool = getToolByName(self.context, 'portal_url', None)
        if portal_tool is not None:
            return portal_tool.getPortalObject().absolute_url()
        return None

    def render(self):
        self.request['disable_border'] = True

        for field in self.fields.keys():
            if field in self.schema:
                if ILanguageIndependentField.providedBy(self.schema[field]):
                    self.widgets[field].addClass('languageindependent')
            # With plone.autoform, fieldnames from additional schematas
            # reference their schema by prefixing their fieldname
            # with schema.__identifier__ and then a dot as a separator
            # See autoform.txt in the autoform package
            if '.' in field:
                schemaname, fieldname = field.split('.')
                for schema in self.additionalSchemata:
                    if schemaname == schema.__identifier__ and fieldname in schema:
                        if ILanguageIndependentField.providedBy(\
                            schema[fieldname]):
                            self.widgets[field].addClass('languageindependent')
        self.babel_content = super(MultilingualAddForm, self).render()
        return self.babel()

    @property
    def max_nr_of_buttons(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMultiLanguageExtraOptionsSchema)
        return settings.buttons_babel_view_up_to_nr_translations


class DefaultMultilingualAddView(DefaultAddView):
    """This is the default add view as looked up by the ++add++ traversal
    namespace adapter in CMF. It is an unnamed adapter on 
    (context, request, fti).
    
    Note that this is registered in ZCML as a simple <adapter />, but we
    also use the <class /> directive to set up security.
    """
    
    form = MultilingualAddForm
    
    def __init__(self, context, request, ti):
        super(DefaultAddView, self).__init__(context, request)
        self.ti = ti

        # Set portal_type name on newly created form instance
        if self.form_instance is not None and not getattr(self.form_instance, 'portal_type', None): 
            self.form_instance.portal_type = ti.getId()

