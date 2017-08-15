'''OpenGL extension NV.sample_locations

This module customises the behaviour of the 
OpenGL.raw.GL.NV.sample_locations to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/sample_locations.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.sample_locations import *
from OpenGL.raw.GL.NV.sample_locations import _EXTENSION_NAME

def glInitSampleLocationsNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION