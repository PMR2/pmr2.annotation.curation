import zope.interface
import zope.schema

from zope.schema.interfaces import ConstraintNotSatisfied
from zope.schema.vocabulary import getVocabularyRegistry

from pmr2.annotation.curation.schema.interfaces import IBasicCurationDict
from pmr2.annotation.curation.schema.interfaces import ICurationDict
from pmr2.annotation.curation.schema.interfaces import ICurationFlagDict
from pmr2.annotation.curation.schema.interfaces import ISequenceChoice


class BasicCurationDict(zope.schema.Dict):
    """
    The basic curation dictionary
    """

    zope.interface.implements(IBasicCurationDict)

    def __init__(self, *a, **kw):
        key_type = zope.schema.DottedName(title=u'Key')
        value_type = zope.schema.List(
            title=u'Values',
            value_type=zope.schema.DottedName(title=u'Value'),
            required=False,
        )

        super(BasicCurationDict, self).__init__(key_type, value_type, *a, **kw)

    # XXX don't do this, don't dynamic schema here (yet).
    # @property
    # def schema(self):
    #     return zope.interface.Interface


class CurationDict(zope.schema.Dict):
    """\
    Curation dictionary.
    """

    zope.interface.implements(
        ICurationDict, 
        zope.schema.interfaces.IFromUnicode,
    )

    def __init__(self, **kw):
        key_type = zope.schema.TextLine(
            title=u'Key',
        )
        value_type = zope.schema.List(
            title=u'Values',
            value_type=zope.schema.TextLine(title=u'Values',),
        )
        super(CurationDict, self).__init__(key_type, value_type, **kw)


    def fromUnicode(self, u):
        """\
        >>> d = CurationDict()
        >>> d.fromUnicode(u'key:value')
        {u'key': [u'value']}

        >>> result = d.fromUnicode(u'key:value\\nkey2:type2\\nkey:value2')
        >>> result[u'key']
        [u'value', u'value2']
        >>> result[u'key2']
        [u'type2']

        >>> d.fromUnicode(u'key:value\\nkey2\\nkey3:value3')
        Traceback (most recent call last):
        ...
        InvalidValue: Invalid curation string
        """

        result = {}
        for i in u.splitlines():
            lines = i.split(u':', 1)
            if len(lines) != 2:
                raise zope.schema.interfaces.InvalidValue(
                    'Invalid curation string')
            k, v = lines
            if k not in result:
                result[k] = []
            result[k].append(v)
        return result


class CurationFlagDict(zope.schema.Dict):
    """\
    Curation flag dictionary.

    The values for this are represented in unicode in two lines for each
    entry, first line being the key, second being the value.
    """

    zope.interface.implements(
        ICurationFlagDict, 
        zope.schema.interfaces.IFromUnicode,
    )

    def __init__(self, **kw):
        key_type = zope.schema.TextLine(
            title=u'Key',
            description=u'A valid value for this curation flag',
        )
        value_type = zope.schema.TextLine(
            title=u'Value',
            description=u'Definition of this value.',
        )
        super(CurationFlagDict, self).__init__(key_type, value_type, **kw)

    def fromUnicode(self, u):
        """\
        >>> d = CurationFlagDict()
        >>> d.fromUnicode(u'key\\nvalue')
        {u'key': u'value'}

        >>> r = d.fromUnicode(u'key\\nvalue\\nkey2\\ntype2\\nkey\\nvalue2')
        >>> a = {u'key': u'value2', u'key2': u'type2'}
        >>> r == a
        True

        >>> r = d.fromUnicode(u'key\\nvalue\\nkey2\\ntype2\\nkey\\n')
        >>> a = {u'key': u'', u'key2': u'type2'}
        >>> r == a
        True

        >>> r = d.fromUnicode(u'key\\nvalue\\nkey2\\ntype2\\nkey')
        >>> a = {u'key': u'', u'key2': u'type2'}
        >>> r == a
        True

        >>> r = d.fromUnicode(u'key\\n\\nkey2\\ntype2\\nkey3\\nvalue3')
        >>> a = {u'key': u'', u'key2': u'type2', u'key3': 'value3'}
        >>> r == a
        True

        >>> r = d.fromUnicode(u'key\\n\\nkey2\\ntype2\\n\\nvalue3')
        >>> a = {u'key': u'', u'key2': u'type2'}
        >>> r == a
        True

        >>> r = d.fromUnicode(u'key\\n\\n\\n\\nkey2\\ntype2')
        >>> a = {u'key': u'', u'key2': u'type2'}
        >>> r == a
        True

        """

        result = {}
        lines = u.splitlines()
        lines.reverse()
        while lines:
            key = lines.pop()
            value = lines and lines.pop() or u''
            if key:
                result[key] = value
        return result


class SequenceChoice(zope.schema.Choice):
    """\
    A marked Choice field for discriminating the right adapters.
    """

    zope.interface.implements(ISequenceChoice)
    _type = list

    def _validate(self, value):
        # Pass all validations during initialization
        if self._init_field:
            return
        try:
            super(SequenceChoice, self)._validate(value)
        except ConstraintNotSatisfied:
            # retry
            vocabulary = self.vocabulary
            vr = getVocabularyRegistry()
            vocabulary = vr.get(None, self.vocabularyName)
            for v in value:
                if v not in vocabulary:
                    raise ConstraintNotSatisfied(v)
