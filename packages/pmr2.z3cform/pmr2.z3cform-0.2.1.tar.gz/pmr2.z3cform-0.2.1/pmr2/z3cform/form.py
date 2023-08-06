import os.path

import zope.component
import zope.event
from zope.schema.fieldproperty import FieldProperty
import zope.lifecycleevent
from zope.browser.interfaces import IAdding

from AccessControl import Unauthorized
from Acquisition import aq_parent, aq_inner

import z3c.form.form
import z3c.form.interfaces
from z3c.form.interfaces import IWidgets
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.z3cform.fieldsets import group
from plone.z3cform.interfaces import IForm, IWrappedForm
from plone.z3cform.templates import ZopeTwoFormTemplateFactory

from pmr2.z3cform.i18n import MessageFactory as _
from pmr2.z3cform.interfaces import IFormLayer, IAuthenticatedForm
from pmr2.z3cform.templates import path

wrapped_form_factory = ZopeTwoFormTemplateFactory(
    path('wrapped_form.pt'), form=IWrappedForm,
    request=IFormLayer)

form_factory = ZopeTwoFormTemplateFactory(path('form.pt'), 
    form=z3c.form.interfaces.IForm,
    request=IFormLayer)


class Form(z3c.form.form.Form):

    def updateActions(self):
        super(Form, self).updateActions()
        for k in self.actions.keys():
            self.actions[k].addClass("btn")


class DisplayForm(z3c.form.form.DisplayForm):
    """\
    A very generic display form.
    """

    id = ''  # plone.app.z3cform template macros expect this.
    enctype = FieldProperty(z3c.form.interfaces.IInputForm['enctype'])

    def __call__(self):
        self.update()
        return self.render()


class AuthenticatedForm(Form):
    """\
    Form with authentication protection.
    """

    zope.interface.implements(IAuthenticatedForm)

    disableAuthenticator = False

    def authenticate(self):
        if self.disableAuthenticator:
            return True

        authenticator = zope.component.getMultiAdapter(
            (self.context, self.request),
            name=u'authenticator',
        )

        if not authenticator.verify():
            raise Unauthorized

    def extractData(self, *a, **kw):
        self.authenticate()
        return super(AuthenticatedForm, self).extractData(*a, **kw)


class PostForm(AuthenticatedForm):
    """\
    Post form mixin class.
    """

    def authenticate(self):
        if not self.request.method == 'POST':
            raise Unauthorized

        return super(PostForm, self).authenticate()


class AddForm(z3c.form.form.AddForm, PostForm):
    """\
    Generic AddForm for the creation of classes.  Since most objects 
    share a similar interface, the process for creating them generally 
    follows/fits into this pattern as defined by the methods below.

    For data assignment of fields and other custom work, redefine the
    method 'add_data'
    """

    extractData = PostForm.extractData

    # set clsobj to the object to be created.
    clsobj = None

    def update(self):
        """\
        Since this could be instantiated as a subform of sort in the
        adding view, we are going to rebase the context up one level if
        that's the case.
        """

        context = self.context
        while context and IAdding.providedBy(context):
            context = aq_parent(context)
        self.context = context
        return super(AddForm, self).update()

    def create(self, data):
        """\
        The generic create method.
        """

        if self.clsobj is None:
            raise TypeError('`clsobj` need to be defined')

        if 'id' in data:
            id_ = data['id']
        else:
            id_ = data['title']
            id_ = zope.component.queryUtility(IIDNormalizer).normalize(id_)

        self._name = id_
        self._data = data
        return self.clsobj(self._name, **data)

    def add(self, obj):
        """\
        The generic add method.
        """

        # add the object to context and retrieve it
        self.context[self._name] = obj
        ctxobj = self.context[self._name]

        # assign data
        self.add_data(ctxobj)

        # do what CMFCore does while finishing construction. 
        # insert it into the workflows and reindex
        ctxobj.notifyWorkflowCreated()
        ctxobj.reindexObject()

        self.post_add(ctxobj)

        self.ctxobj = ctxobj
        
    def add_data(self, obj):
        """\
        Generally this format should work:
        obj.title = self._data['title']
        """

        # it would be nice if the data assignment can happen without
        # explicit declaration.
        raise NotImplementedError

    def post_add(self, obj):
        """\
        If needed, extra actions taken can be defined here.
        """
        pass

    def nextURL(self):
        """\
        Default nextURL method.
        """

        ctxobj = self.ctxobj
        # XXX test whether getTypeInfo is provided?
        fti = ctxobj.getTypeInfo()
        if fti and not fti.immediate_view == fti.default_view:
            # since we do the redirects (rather, provide the URI), we
            # need to support this immediate view value.
            view = fti.immediate_view
        else:
            # XXX propertiestools, typesUseViewActionInListings is
            # ignored!  for now this product doesn't have anything that
            # doesn't do the above statement yet require a /view, so
            # we leave this unimplemented for now.
            # To implement this, get the portal_properties tools.
            # refer to plone.app.content, folder_contents.py
            view = None

        if view:
            return "%s/%s" % (self.ctxobj.absolute_url(), view)
        else:
            return self.ctxobj.absolute_url()


class EditForm(z3c.form.form.EditForm, PostForm):
    """\
    Include POST method checking.
    """

    extractData = PostForm.extractData


class Group(group.Group):
    def updateWidgets(self):
        self.widgets = zope.component.getMultiAdapter(
            (self, self.request, self.getContent()), IWidgets)
        # difference with parent is we use this group's ignoreContext
        # attribute rather than the parent form's setting
        self.widgets.ignoreContext = self.ignoreContext
        for attrName in ('mode', 'ignoreRequest', 'ignoreReadonly'):
            value = getattr(self.parentForm.widgets, attrName)
            setattr(self.widgets, attrName, value)
        self.widgets.update()

    def getContent(self):
        # since context is manually set...
        return self.context

