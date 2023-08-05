import sys
from collections import MutableMapping

from django.db.models.fields import FieldDoesNotExist
from django.utils.text import capfirst
from django.db.models.options import get_verbose_name

from mongoengine.fields import ReferenceField

def create_verbose_name(name):
    name = get_verbose_name(name)
    name.replace('_', ' ')
    return name

class PkWrapper(object):
    def __init__(self, wrapped):
        self.obj = wrapped
    
    def __getattr__(self, attr):
        if attr in dir(self.obj):
            return getattr(self.obj, attr)
        raise AttributeError
        
    def __setattr__(self, attr, value):
        if attr != 'obj' and hasattr(self.obj, attr):
            setattr(self.obj, attr, value)
        super(PkWrapper, self).__setattr__(attr, value)

class DocumentMetaWrapper(MutableMapping):
    """
    Used to store mongoengine's _meta dict to make the document admin
    as compatible as possible to django's meta class on models. 
    """
    _pk = None
    pk_name = None
    _app_label = None
    module_name = None
    _verbose_name = None
    has_auto_field = False
    object_name = None
    proxy = []
    parents = {}
    many_to_many = []
    _field_cache = None
    document = None
    _meta = None
    concrete_model = None
    
    def __init__(self, document):
        self.document = document
        # used by Django to distinguish between abstract and concrete models
        # here for now always the document
        self.concrete_model = document
        self._meta = getattr(document, '_meta', {})
        
        try:
            self.object_name = self.document.__name__
        except AttributeError:
            self.object_name = self.document.__class__.__name__
        
        self.module_name = self.object_name.lower()
        
        # EmbeddedDocuments don't have an id field.
        try:
            self.pk_name = self._meta['id_field']
            self._init_pk()
        except KeyError:
            pass
    
    @property
    def app_label(self):
        if self._app_label is None:
            model_module = sys.modules[self.document.__module__]
            self._app_label = model_module.__name__.split('.')[-2]
        return self._app_label
            
    @property
    def verbose_name(self):
        """
        Returns the verbose name of the document.
        
        Checks the original meta dict first. If it is not found 
        then generates a verbose name from from the object name.
        """
        if self._verbose_name is None:
            try:
                self._verbose_name = capfirst(create_verbose_name(self._meta['verbose_name']))
            except KeyError:
                self._verbose_name = capfirst(create_verbose_name(self.object_name))
                
        return self._verbose_name
    
    @property
    def verbose_name_raw(self):
        return self.verbose_name
    
    @property
    def verbose_name_plural(self):
        return "%ss" % self.verbose_name
    
    @property    
    def pk(self):
        if not hasattr(self._pk, 'attname'):
            self._init_pk()
        return self._pk
        
    def _init_pk(self):
        """
        Adds a wrapper around the documents pk field. The wrapper object gets the attributes
        django expects on the pk field, like name and attname.
        
        The function also adds a _get_pk_val method to the document.
        """
        if self.id_field is None:
            return
        
        try:
            pk_field = getattr(self.document, self.id_field)
            self._pk = PkWrapper(pk_field)
            self._pk.name = self.id_field
            self._pk.attname = self.id_field
            self._pk_name = self.id_field
                
            self.document._pk_val = getattr(self.document, self.pk_name)
            # avoid circular import
            from mongodbforms.util import patch_document
            def _get_pk_val(self):
                return self._pk_val
            patch_document(_get_pk_val, self.document)
        except AttributeError:
            return      
                
    def get_add_permission(self):
        return 'add_%s' % self.object_name.lower()

    def get_change_permission(self):
        return 'change_%s' % self.object_name.lower()

    def get_delete_permission(self):
        return 'delete_%s' % self.object_name.lower()
    
    def get_ordered_objects(self):
        return []
    
    def get_field_by_name(self, name):
        """
        Returns the (field_object, model, direct, m2m), where field_object is
        the Field instance for the given name, model is the model containing
        this field (None for local fields), direct is True if the field exists
        on this model, and m2m is True for many-to-many relations. When
        'direct' is False, 'field_object' is the corresponding RelatedObject
        for this field (since the field doesn't have an instance associated
        with it).

        Uses a cache internally, so after the first access, this is very fast.
        """
        try:
            try:
                return self._field_cache[name]
            except TypeError:
                self._init_field_cache()
                return self._field_cache[name]
        except KeyError:
            raise FieldDoesNotExist('%s has no field named %r'
                    % (self.object_name, name))
            
        
    def _init_field_cache(self):
        if self._field_cache is None:
            self._field_cache = {}
        
        for f in self.document._fields.values():
            # Yay, more glue. Django expects fields to have a rel attribute
            # at least in the admin, probably in more places. So we add them here
            # and hope that this is the common path to access the fields.
            if not hasattr(f, 'rel'):
                f.rel = None
            if getattr(f, 'verbose_name', None) is None:
                f.verbose_name = capfirst(create_verbose_name(f.name))
            if not hasattr(f, 'flatchoices'):
                flat = []
                if f.choices is not None:
                    for choice, value in f.choices:
                        if isinstance(value, (list, tuple)):
                            flat.extend(value)
                        else:
                            flat.append((choice,value))
                f.flatchoices = flat
            if isinstance(f, ReferenceField):
                document = f.document_type
                document._meta = DocumentMetaWrapper(document)
                document._admin_opts = document._meta
                self._field_cache[document._meta.module_name] = (f, document, False, False)
            else:
                self._field_cache[f.name] = (f, None, True, False)
                
        return self._field_cache
         
    def get_field(self, name, many_to_many=True):
        """
        Returns the requested field by name. Raises FieldDoesNotExist on error.
        """
        return self.get_field_by_name(name)[0]
    
    def __getattr__(self, name):
        try:
            return self._meta[name]
        except KeyError:
            raise AttributeError
        
    def __setattr__(self, name, value):
        if not hasattr(self, name):
            self._meta[name] = value
        else:
            super(DocumentMetaWrapper, self).__setattr__(name, value)
    
    def __contains__(self,key):
        return key in self._meta
    
    def __getitem__(self, key):
        return self._meta[key]
    
    def __setitem__(self, key, value):
        self._meta[key] = value

    def __delitem__(self, key):
        return self._meta.__delitem__(key)

    def __iter__(self):
        return self._meta.__iter__()

    def __len__(self):
        return self._meta.__len__()

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
    
    def get_parent_list(self):
        return []
    
    def get_all_related_objects(self, *args, **kwargs):
        return []

    def iteritems(self):
        return iter(self._meta.items())
