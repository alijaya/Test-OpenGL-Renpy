init python:

    from __future__ import division
    import math
    from OpenGL.GL import *
    import ctypes

    class OpenGLDisplayable(renpy.Displayable):

        def __init__(self, child, **kwargs):
            super(OpenGLDisplayable, self).__init__(**kwargs)

            self.child = renpy.displayable(child)

        def render(self, width, height, st, at):

            print(glGetString(GL_VERSION))

            # child_render = renpy.render(self.child, width, height, st, at)

            vertices = [
                -0.5, -0.5,
                -0.5, 0.5,
                0.5, -0.5,
                -0.5, 0.5,
                0.5, -0.5,
                0.5, 0.5
            ]
            uvs = [
                0, 0,
                0, 1,
                1, 0,
                0, 1,
                1, 0,
                1, 1
            ]
            vertices = ( ctypes.c_float * len( vertices ) )( *vertices )
            uvs = ( ctypes.c_float * len( uvs ) )( *uvs )

            vertexBuffer = glGenBuffers( 1 )
            glBindBuffer( GL_ARRAY_BUFFER, vertexBuffer )
            glBufferData( GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW )
            glBindBuffer( GL_ARRAY_BUFFER, 0 )

            uvBuffer = glGenBuffers( 1 )
            glBindBuffer( GL_ARRAY_BUFFER, uvBuffer )
            glBufferData( GL_ARRAY_BUFFER, uvs, GL_STATIC_DRAW )
            glBindBuffer( GL_ARRAY_BUFFER, 0 )

            vertexSource = """
            attribute vec2 pos;
            attribute vec2 uv;
            varying vec2 v_uv;
            void main() {
                gl_Position = vec4( pos, 1.0, 1.0 );
                v_uv = uv;
            }
            """

            fragmentSource = """
            uniform sampler2D map;
            varying vec2 v_uv;
            void main() {
                gl_FragColor = texture2D( map, v_uv );
            }
            """

            vertexShader = glCreateShader( GL_VERTEX_SHADER )
            glShaderSource( vertexShader, vertexSource )
            glCompileShader( vertexShader )

            fragmentShader = glCreateShader( GL_FRAGMENT_SHADER )
            glShaderSource( fragmentShader, fragmentSource )
            glCompileShader( fragmentShader )

            program = glCreateProgram()
            glAttachShader( program, vertexShader )
            glAttachShader( program, fragmentShader )
            glLinkProgram( program )
            glUseProgram( program )

            child_surface = im.load_surface( self.child )
            child_surface.lock()
            child_texture = glGenTextures( 1 )
            glPixelStorei( GL_UNPACK_ROW_LENGTH, child_surface.get_pitch() // child_surface.get_bytesize() )
            glBindTexture( GL_TEXTURE_2D, child_texture )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
            glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, child_surface.get_width(), child_surface.get_height(), 0, GL_RGBA, GL_UNSIGNED_BYTE, ctypes.c_void_p( child_surface._pixels_address ) )
            glBindTexture( GL_TEXTURE_2D, 0 )
            glPixelStorei( GL_UNPACK_ROW_LENGTH, 0 )
            child_surface.unlock()

            posLoc = glGetAttribLocation( program, "pos" )
            glEnableVertexAttribArray( posLoc )
            glBindBuffer( GL_ARRAY_BUFFER, vertexBuffer )
            glVertexAttribPointer( posLoc, 2, GL_FLOAT, False, 0, None )
            glBindBuffer( GL_ARRAY_BUFFER, 0 )

            uvLoc = glGetAttribLocation( program, "uv" )
            glEnableVertexAttribArray( uvLoc )
            glBindBuffer( GL_ARRAY_BUFFER, uvBuffer )
            glVertexAttribPointer( uvLoc, 2, GL_FLOAT, False, 0, None )
            glBindBuffer( GL_ARRAY_BUFFER, 0 )

            mapLoc = glGetUniformLocation( program, "map" )
            glUniform1i( mapLoc, 0 )

            texture = glGenTextures( 1 )
            glBindTexture( GL_TEXTURE_2D, texture )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST )
            glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST )
            glTexImage2D( GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_BGRA, GL_UNSIGNED_BYTE, None )
            glBindTexture( GL_TEXTURE_2D, 0 )

            framebuffer = glGenFramebuffers( 1 )
            glBindFramebuffer( GL_FRAMEBUFFER, framebuffer )
            glFramebufferTexture2D( GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0 )
            glBindFramebuffer( GL_FRAMEBUFFER, 0 )

            glBindFramebuffer( GL_FRAMEBUFFER, framebuffer )

            glViewport( 0, 0, width, height )

            glClearColor( 1.0, 1.0, 0.0, 1.0 )
            glClear( GL_COLOR_BUFFER_BIT )

            glActiveTexture( GL_TEXTURE0 )
            glBindTexture( GL_TEXTURE_2D, child_texture )
            glDrawArrays( GL_TRIANGLES, 0, len( vertices )// 2 )
            glBindTexture( GL_TEXTURE_2D, 0 )

            glBindFramebuffer( GL_FRAMEBUFFER, 0 )

            ret = renpy.Render( width, height )
            surface = ret.canvas().get_surface()
            surface.lock()

            glPixelStorei( GL_PACK_ROW_LENGTH, surface.get_pitch() // surface.get_bytesize() )
            glBindFramebuffer( GL_FRAMEBUFFER, framebuffer )
            glReadPixels( 0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, surface._pixels_address )
            glBindFramebuffer( GL_FRAMEBUFFER, 0 )
            glPixelStorei( GL_PACK_ROW_LENGTH, 0 )

            surface.unlock()

            return ret

        def event(self, ev, x, y, st):
            pass

        def visit(self):
            return [ self.child ]