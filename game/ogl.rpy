init python:

    from __future__ import division
    from functools import partial
    import ctypes
    import math
    import pygame
    import random

    import THREE
    from OpenGL.GL import *

    def displayableToTexture( displayable ):

        displayable = renpy.displayable( displayable )

        image = renpy.load_surface( displayable )

        tex = THREE.Texture()
        tex.image = pygame.transform.flip( image, False, True )
        bytesize = tex.image.get_bytesize()

        if bytesize == 1:

            tex.image = tex.image.convert( ( 0xff, 0xff00, 0xff0000, 0xff000000 ) )
            bytesize = tex.image.get_bytesize()

        tex.format = THREE.RGBAFormat if bytesize == 4 else THREE.RGBFormat
        tex.needsUpdate = True

        return tex

    def renderTargetToTextureGrid( renderTarget ):

        width = renderTarget.width
        height = renderTarget.height
        renderer = THREE.OpenGLRenderer

        surface = pygame.Surface( (width, height), pygame.SRCALPHA )

        surface.lock()
        glPixelStorei( GL_PACK_ROW_LENGTH, surface.get_pitch() // surface.get_bytesize() )
        renderer.readRenderTargetPixels( renderTarget, 0, 0, width, height, surface._pixels_address )
        glPixelStorei( GL_PACK_ROW_LENGTH, 0 )
        surface.unlock()

        surface = pygame.transform.flip( surface, False, True )
        textureGrid = renpy.gl.gltexture.texture_grid_from_surface( surface, True )

        return textureGrid
        # return surface

    class OGL(renpy.Displayable):

        def __init__(self, childs, **kwargs):
            super(OGL, self).__init__(**kwargs)

            self.childs = childs

            self.importantState = [
                ( GL_COLOR_CLEAR_VALUE, glGetFloatv, glClearColor ),
                ( GL_COLOR_WRITEMASK, glGetBooleanv, glColorMask ),
                ( GL_DEPTH_CLEAR_VALUE, glGetFloatv, glClearDepth ),
                ( GL_DEPTH_FUNC, glGetIntegerv, glDepthFunc ),
                ( GL_DEPTH_TEST, glGetBooleanv, glEnable ),
                ( GL_CULL_FACE, glGetBooleanv, glEnable ),
                ( GL_BLEND, glGetBooleanv, glEnable ),
                ( GL_SCISSOR_TEST, glGetBooleanv, glEnable ),
                ( GL_SCISSOR_BOX, glGetIntegerv, glScissor ),
                ( GL_VIEWPORT, glGetIntegerv, glViewport ),
                ( GL_ACTIVE_TEXTURE, glGetIntegerv, glActiveTexture ),
                ( GL_TEXTURE_BINDING_2D, glGetIntegerv, partial( glBindTexture, GL_TEXTURE_2D ) ),
                ( GL_DRAW_FRAMEBUFFER_BINDING, glGetIntegerv, partial( glBindFramebuffer, GL_DRAW_FRAMEBUFFER ) ),
                ( GL_READ_FRAMEBUFFER_BINDING, glGetIntegerv, partial( glBindFramebuffer, GL_READ_FRAMEBUFFER ) ),
                ( GL_RENDERBUFFER_BINDING, glGetIntegerv, partial( glBindRenderbuffer, GL_RENDERBUFFER ) ),
                ( GL_ARRAY_BUFFER_BINDING, glGetIntegerv, partial( glBindBuffer, GL_ARRAY_BUFFER ) ),
                ( GL_ELEMENT_ARRAY_BUFFER_BINDING, glGetIntegerv, partial( glBindBuffer, GL_ELEMENT_ARRAY_BUFFER ) ),
                ( ( GL_BLEND_SRC_RGB, GL_BLEND_DST_RGB, GL_BLEND_SRC_ALPHA, GL_BLEND_DST_ALPHA ), glGetIntegerv, glBlendFuncSeparate ),
                ( ( GL_BLEND_EQUATION_RGB, GL_BLEND_EQUATION_ALPHA ), glGetIntegerv, glBlendEquationSeparate ),
            ]

            width = config.screen_width
            height = config.screen_height

            self.x = width / 2
            self.y = height / 2

            scene = THREE.Scene()
            scene.background = THREE.Color().setHSL( 0.5, 0.1, 0.8 )
            scene.fog = THREE.FogExp2( 0x000000, 0.001 )
            camera = THREE.PerspectiveCamera( 75, width / height, 1, 3000 )
            camera.position.z = 1000

            renderTarget = THREE.OpenGLRenderTarget( width, height )

            geometry = THREE.Geometry()
            
            for i in xrange( 10000 ):

                vertex = THREE.Vector3()
                vertex.x = random.uniform( -1000, 1000 )
                vertex.y = random.uniform( -1000, 1000 )
                vertex.z = random.uniform( -1000, 1000 )

                geometry.vertices.append( vertex )

            parameters = [
                [ [1.0, 0.2, 0.5], None, 20 ],
                [ [0.95, 0.1, 0.5], None, 15 ],
                [ [0.90, 0.05, 0.5], None, 10 ],
                [ [0.85, 0, 0.5], None, 8 ],
                [ [0.80, 0, 0.5], None, 5 ]
            ]

            materials = []

            for param in parameters:

                # color = param[0]
                color = [0.5,0.1,0.25]
                size = param[2]

                mat = THREE.PointsMaterial( size = size, blending = THREE.AdditiveBlending, depthTest = False, transparent = True )
                mat.color.setHSL( color[0], color[1], color[2] )
                materials.append( mat )

                particles = THREE.Points( geometry, mat )

                particles.rotation.x = random.uniform( 0, 2 * math.pi )
                particles.rotation.y = random.uniform( 0, 2 * math.pi )
                particles.rotation.z = random.uniform( 0, 2 * math.pi )

                scene.add( particles )

            self.materials = materials
            self.parameters = parameters
            self.scene = scene
            self.camera = camera
            self.renderTarget = renderTarget
            self.initMaterial = False
            
        def saveState(self):

            state = {}

            for s in self.importantState:

                if isinstance( s[0], tuple ):
                    for comps in s[0]:
                        state[ comps ] = s[1](comps)
                else:
                    state[ s[0] ] = s[1](s[0])
            
            return state

        def loadState( self, state ):

            for s in self.importantState:

                if isinstance( s[0], tuple ):

                    v = map( lambda comps: state[ comps ], s[0] )

                    s[2]( *v )

                else:

                    v = state[ s[0] ]

                    if s[2] == glEnable:

                        if v: glEnable( s[0] )
                        else: glDisable( s[0] )
                    
                    else:

                        if isinstance( v, ctypes.Array ): s[2]( *v )
                        else: s[2]( v )

        def updateScene( self, st, at ):

            if not self.initMaterial:
                self.initMaterial = True
                childs = self.childs
                parameters = self.parameters
                parameters[0][1] = displayableToTexture(childs[1])
                parameters[1][1] = displayableToTexture(childs[2])
                parameters[2][1] = displayableToTexture(childs[0])
                parameters[3][1] = displayableToTexture(childs[4])
                parameters[4][1] = displayableToTexture(childs[3])

                for i in xrange( len( self.parameters ) ):
                    sprite = self.parameters[i][1]
                    self.materials[i].map = sprite
            
            x = self.x
            y = self.y
            x -= config.screen_width / 2
            y -= config.screen_height / 2
            self.camera.position.x += ( x - self.camera.position.x ) * 0.05
            self.camera.position.y += ( - y - self.camera.position.y ) * 0.05
            self.camera.lookAt( self.scene.position )

            scene = self.scene

            for i in xrange( len( scene.children ) ):

                object = scene.children[ i ]

                if isinstance( object, THREE.Points ):

                    object.rotation.y = at * 0.1 * ( i + 1 if i < 4 else - ( i + 1 ) )

        def render(self, width, height, st, at):

            ## update scene

            # self.scene.background = THREE.Color( random.uniform(0,1), 1, 0 )
            self.updateScene( st, at )
            
            ## render

            renderTarget = self.renderTarget
            state = self.saveState()
            print(state)
            renderer = THREE.OpenGLRenderer
            renderer.init()
            renderer.setSize( renderTarget.width, renderTarget.height )
            renderer.setRenderTarget( renderTarget )
            renderer.render( self.scene, self.camera, renderTarget )
            renderer.reset()
            self.loadState( state )

            ## copy to surface

            ret = renpy.Render( renderTarget.width, renderTarget.height )

            textureGrid = renderTargetToTextureGrid( renderTarget )

            ret.blit( textureGrid, (0, 0) )

            renpy.redraw( self, 1/60 )

            return ret

        def event(self, ev, x, y, st):

            if ev.type == pygame.MOUSEMOTION:

                self.x = x
                self.y = y

            pass

        def visit(self):
            return []