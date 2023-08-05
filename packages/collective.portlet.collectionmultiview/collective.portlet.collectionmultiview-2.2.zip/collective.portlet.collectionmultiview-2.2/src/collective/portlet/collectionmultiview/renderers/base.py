from collective.portlet.collectionmultiview.interfaces import (
        ICollectionMultiViewRenderer
)
from zope.component import adapts
from zope.interface import implements
from Acquisition import aq_inner


class DataProvider(object):

    def __init__(self, data, schema):
        self._data = data
        self._schema = schema

    def __getattr__(self, key):
        # FIXME: check against the schema
        return getattr(self._data, key, None)

class CollectionMultiViewBaseRenderer(object):
#    adapts(ICollectionMultiViewBaseRenderer)
    """
        This is the base renderer class, it does the magic of rendering the
        portlet
    """
    adapts(None)
    implements(ICollectionMultiViewRenderer)

    def __init__(self, base):
        if base is None:
            """ hack to allow us to query for all adapters """
            return

        self.request = base.request
        self.context = aq_inner(base.context)  
        if getattr(self, 'schema', None):
            self.data = DataProvider(base.data, self.schema)
        else:
            self.data = base.data
        self.results = base.results
        self.collection_url = base.collection_url
        self.collection = base.collection
        self.css_class = base.css_class
        self.base = base

    def render(self, *args, **kwargs):
        return self.template(*args, **kwargs)

    def tag(self, obj, scale='tile', css_class='tileImage'):
        context = aq_inner(obj)
        # test for leadImage and normal image
        for fieldname in ['leadImage', 'image']:
            field = context.getField(fieldname)
            if field is not None:
                if field.get_size(context) != 0:
                    return field.tag(context, scale=scale, css_class=css_class)
        return ''
