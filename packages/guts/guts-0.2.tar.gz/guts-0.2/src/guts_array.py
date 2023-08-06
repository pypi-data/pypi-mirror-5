from guts import *
import numpy as num
from cStringIO import StringIO

class literal(str): 
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

import yaml
yaml.SafeDumper.add_representer(literal, literal_presenter)

class Array(Object):

    dummy_for = num.ndarray

    class __T(TBase):
        def __init__(self, shape=None, dtype=None, *args, **kwargs):
            TBase.__init__(self, *args, **kwargs)
            self.shape = shape
            self.dtype = dtype

        def regularize_extra(self, val):
            if isinstance(val, basestring):
                ndim = None
                if self.shape:
                    ndim = len(self.shape)

                val = num.loadtxt(StringIO(val), dtype=self.dtype, ndmin=ndim)
            else:
                val = num.asarray(val, dtype=self.dtype)

            return val

        def validate_extra(self, val):
            if self.dtype != val.dtype:
                raise ValidationError('array not of required type: need %s, got %s' % (self.dtype, val.dtype))

            if self.shape is not None:
                la, lb = len(self.shape), len(val.shape)
                if la != lb:
                    raise ValidationError('array dimension mismatch: need %i, got %i' % (la, lb))

                for a,b in zip(self.shape, val.shape):
                    if a is not None:
                        if a != b:
                            raise ValidationError('array shape mismatch: need %s, got: %s' % (self.shape, val.shape))

        def to_save(self, val):
            out = StringIO()
            num.savetxt(out, val, fmt='%12.7g')
            return literal(out.getvalue())

__all__ = [ 'Array' ]

