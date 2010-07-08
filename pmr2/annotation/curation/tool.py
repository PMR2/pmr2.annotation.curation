from persistent import Persistent
from zope.annotation import factory, IAttributeAnnotatable
from zope.app.container.contained import Contained
from zope.app.component.hooks import getSite, getSiteManager
import zope.schema
import zope.interface
import zope.component

from pmr2.app.content.interfaces import IWorkspaceContainer
from pmr2.app.interfaces import IPMR2GlobalSettings, IPMR2PluggableSettings
from pmr2.app.factory import NamedUtilBase

from pmr2.annotation.curation.interfaces import ICurationFlag
from pmr2.annotation.curation.interfaces import ICurationTool

__all__ = [
    'CurationTool',
]


class CurationToolAnnotation(Persistent, Contained):
    """\
    Please refer to ICurationTool
    """

    zope.interface.implements(ICurationTool)
    zope.component.adapts(IAttributeAnnotatable)

    custom_flags = zope.schema.fieldproperty.FieldProperty(
        ICurationTool['custom_flags'])
    inactive_flags = zope.schema.fieldproperty.FieldProperty(
        ICurationTool['inactive_flags'])

    def getFlag(self, name):
        if name in self.custom_flags:
            return self.custom_flags[name]
        flag = zope.component.queryUtility(ICurationFlag, name=name)
        return flag

    def setFlag(self, name, flag):
        # query flag first to not overwrite product-defined flags?
        if flag is None and name in self.custom_flags:
            del self.custom_flags[name]
            return
        self.custom_flags[name] = flag

CurationTool = factory(CurationToolAnnotation)