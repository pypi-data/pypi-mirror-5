""" Visualization Data Provenance

    >>> portal = layer['portal']
    >>> from eea.app.visualization.interfaces import IDataProvenance

"""
from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from eea.app.visualization.config import ANNO_DATA
from eea.app.visualization.interfaces import IDataProvenance

class DataProvenance(object):
    """ Abstract visualization data provenance metadata accessor/mutator

    >>> document = portal.invokeFactory('Document', 'document')
    >>> document = portal._getOb(document)
    >>> source = IDataProvenance(document)
    >>> source
    <eea.app.visualization.data.source.DataProvenance object...>

    """
    implements(IDataProvenance)

    def __init__(self, context):
        self.context = context
    #
    # Internal methods
    #
    @property
    def _config(self):
        """ Config
        """
        anno = IAnnotations(self.context)
        config = anno.get(ANNO_DATA, None)
        if config is None:
            config = anno[ANNO_DATA] = PersistentDict()
        return config
    #
    # Title
    #
    @property
    def title(self):
        """Data source title

            >>> source.title
            u''

        """
        return self._config.get('title', u'')

    @title.setter
    def title(self, value):
        """
        Data source title setter

            >>> source.title = 'GDP vs. GHG'
            >>> source.title
            u'GDP vs. GHG'

        """
        if isinstance(value, str):
            value = value.decode('utf-8')
        self._config['title'] = value
    #
    # Link
    #
    @property
    def link(self):
        """
        Data source link

            >>> source.link
            u''

        """
        return self._config.get('link', u'')

    @link.setter
    def link(self, value):
        """
        Data source link setter

            >>> source.link = 'http://daviz.eionet.europa.eu'
            >>> source.link
            u'http://daviz.eionet.europa.eu'

        """
        if isinstance(value, str):
            value = value.decode('utf-8')
        self._config['link'] = value
    #
    # Owner
    #
    @property
    def owner(self):
        """
        Data source owner

            >>> source.owner
            u''

        """
        return self._config.get('owner', u'')

    @owner.setter
    def owner(self, value):
        """
        Data source owner setter

            >>> source.owner = 'EEA'
            >>> source.owner
            u'EEA'

        """
        if isinstance(value, str):
            value = value.decode('utf-8')
        self._config['owner'] = value

class BlobDataProvenance(object):
    """
    Visualization data provenance metadata accessor/mutator for Blob Files

        >>> blob = portal.invokeFactory('File', 'blob')
        >>> blob = portal._getOb(blob)
        >>> blob.setTitle(u'Blob data')
        >>> source = IDataProvenance(blob)
        >>> source
        <eea.app.visualization.data.source.BlobDataProvenance object...>

    """
    implements(IDataProvenance)

    def __init__(self, context):
        self.context = context
    #
    # Internal methods
    #
    @property
    def copyrights(self):
        """ Parse owner and link from object rights field
        """
        field = self.context.getField('rights')
        rights = field.getAccessor(self.context)()
        index = rights.find('<')
        if index == -1:
            return rights.strip(), ''
        owner = rights[:index].strip()
        link = rights[index:].replace('<', '').replace('>', '').strip()
        return owner, link

    @copyrights.setter
    def copyrights(self, value):
        """ Set owner and link within object rights field.

        value -- tuple like (owner, link)

        """
        if isinstance(value, (str, unicode)):
            value = (value, "")
        rights = u"%s <%s>" % value
        self.context.getField('rights').getMutator(self.context)(rights.strip())
        self.context.reindexObject()
    #
    # Title
    #
    @property
    def title(self):
        """
        Blob data source title

        Source title shares the same field as obj.title

            >>> source.title
            'Blob data'

        """
        return self.context.getField('title').getAccessor(self.context)()

    @title.setter
    def title(self, value):
        """
        Blob data source title setter

            >>> source.title = u'GDP vs. GHG'
            >>> source.title
            'GDP vs. GHG'

            >>> blob.title_or_id()
            'GDP vs. GHG'

        """
        self.context.getField('title').getMutator(self.context)(value)
        self.context.reindexObject()
    #
    # Link
    #
    @property
    def link(self):
        """
        Blob data source link

            >>> source.link
            ''

        """
        return self.copyrights[1]

    @link.setter
    def link(self, value):
        """
        Blob data source link setter

        Source link and owner share the object.rights field

            >>> blob.getField('rights').getAccessor(blob)()
            ''

            >>> source.link = u'http://daviz.eionet.europa.eu'
            >>> source.link
            'http://daviz.eionet.europa.eu'

            >>> blob.getField('rights').getAccessor(blob)()
            '<http://daviz.eionet.europa.eu>'

        """
        owner, link = self.copyrights
        link = value
        self.copyrights = (owner, link)
    #
    # Owner
    #
    @property
    def owner(self):
        """
        Blob data source owner

            >>> source.owner
            ''

        """
        return self.copyrights[0]

    @owner.setter
    def owner(self, value):
        """
        Blob data source owner setter

            >>> source.owner = u'EEA'
            >>> source.owner
            'EEA'

            >>> blob.getField('rights').getAccessor(blob)()
            'EEA <http://daviz.eionet.europa.eu>'

            >>> blob.setRights(u'Manually changed object rights')
            >>> blob.getField('rights').getAccessor(blob)()
            'Manually changed object rights'

            >>> source.link
            ''

            >>> source.owner
            'Manually changed object rights'

        """
        owner, link = self.copyrights
        owner = value
        self.copyrights = (owner, link)
