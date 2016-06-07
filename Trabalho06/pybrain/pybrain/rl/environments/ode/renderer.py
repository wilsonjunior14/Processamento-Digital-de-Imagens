__author__ = 'Thomas Rueckstiess, ruecksti@in.tum.de'

from OpenGL.GL import * #@UnusedWildImport
from OpenGL.GLU import * #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

from math import pi, acos, sqrt
from tools.mathhelpers import dotproduct, crossproduct, norm
from pybrain.rl.environments.renderer import Renderer 
           
import ode
import time
import threading 

import Image


class ODERenderer(Renderer):
    def __init__(self):
        Renderer.__init__(self)
        
        # initialize the viewport size
        self.width = 800
        self.height = 600  
        
        # initialize object which the camera follows
        self.centerObj = None
        self.mouseView = True
        self.viewDistance = 30
        self.lastx = -0.5
        self.lasty = 1
        self.lastz = -1
        
        self.dt = 1
        self.fps = 50
        self.lasttime = time.time()
        self.starttime = time.time()
        self.captureScreen = False
        self.isCapturing = False
        self.isFloorGreen = True
        
        self.body_geom = None
        self.keyboardCallback = None 
        
        self.dataLock = threading.Lock()  
        
        # capture only every frameT. frame
        self.counter = 0
        self.frameT = 25
    
    def _render(self):
        self.init_GL()  
        
        # Set call-back function for keyboard if available
        if (self.keyboardCallback):
            glutKeyboardFunc (self.keyboardCallback)
                
        # set own callback functions
        glutMotionFunc (self._motionfunc)
        glutPassiveMotionFunc(self._passivemotionfunc)
        glutDisplayFunc (self._drawfunc) 
        glutIdleFunc (self._idlefunc)
        
        self.dt = 1.0/self.fps
        self.lasttime = time.time()
        self.starttime = self.lasttime
        
        # start the OpenGL main loop
        while True:
            glutMainLoop()
    
    def setFrameRate(self, fps):
        self.dataLock.acquire() 
        self.fps = fps
        self.dt = 1.0/self.fps
        self.dataLock.release()   
        
    def setCaptureScreen(self, capture):
        self.dataLock.acquire() 
        self.captureScreen = capture
        self.dataLock.release()

    def getCaptureScreen(self):
        return self.captureScreen

    def waitScreenCapturing(self):
        self.isCapturing = True
        
    def isScreenCapturing(self):
        return self.isCapturing
    
    def setCenterObj(self, obj):
        self.centerObj = obj
    
    def setKeyboardCallback(self, callback):
        self.dataLock.acquire() 
        self.keyboardCallback = callback
        self.dataLock.release() 
    
    def updateData(self, bgPairs):
        self.dataLock.acquire()
        self.body_geom = bgPairs
        self.dataLock.release()                      

    def init_GL(self, width=800, height=600):
        """ initialize OpenGL. This function has to be called only once before drawing. """
        glutInit([])

        # Open a window
        glutInitDisplayMode (GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        self.width = width
        self.height = height
        glutInitWindowPosition (500, 0)
        glutInitWindowSize (self.width, self.height)
        self._myWindow = glutCreateWindow ("virtual world")

        # Initialize Viewport and Shading
        glViewport(0, 0, self.width, self.height)
        glShadeModel(GL_SMOOTH)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glClearColor(1.0, 1.0, 1.0, 0.0)

        # Initialize Depth Buffer
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        # Initialize Lighting
        glEnable(GL_LIGHTING)
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
        glLightfv(GL_LIGHT1, GL_POSITION,[0.0, 5.0, 5.0, 1.0])
        glEnable(GL_LIGHT1)

        # enable material coloring
        glEnable(GL_COLOR_MATERIAL);
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE);

        glEnable(GL_NORMALIZE)
    
    def prepare_GL(self):
        """Prepare drawing. This function is called in every step. It clears the screen and sets the new camera position"""
        # Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Projection mode
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective (45,1.3333,0.2,500)

        # Initialize ModelView matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # View transformation (if "centerOn(...)" is set, keep camera to specific object)
        if self.centerObj is not None:
            (centerX, centerY, centerZ) = self.centerObj.getPosition()
        else:
            centerX = centerY = centerZ = 0
        # use the mouse to shift eye sensor on a hemisphere
        eyeX = self.viewDistance * self.lastx
        eyeY = self.viewDistance * self.lasty + centerY
        eyeZ = self.viewDistance * self.lastz
        gluLookAt (eyeX, eyeY, eyeZ, centerX, centerY, centerZ, 0, 1, 0)
    
    def draw_body_geom(self, body, geom):
        """Draw an ODE body. Also draws a (bodyless) plane. """
        # check if external texture with "addTexture(...)" is set
        # if body and body.name in self.textures.keys():
        #     # load texture (with function from the "MyOpenGLTools" module)
        #     tex = self._loadTexture(self.textures[body.name])
        #     glEnable(GL_TEXTURE_2D)
        #     glBindTexture(GL_TEXTURE_2D, tex[2])
        # elif geom.name in self.textures.keys():
        #     # in case of plane, no body is present. Load texture anyway.
        #     tex = self._loadTexture(self.textures[geom.name])
        #     glEnable(GL_TEXTURE_2D)
        #     glBindTexture(GL_TEXTURE_2D, tex[2])
        # else:                                    
            # no texture request found for this object, disable textures
        glDisable(GL_TEXTURE_2D)
        
        glPushMatrix()
        # draw real bodies (boxes, spheres, ...)
        if body != None:
            # set color of object (currently dark gray)
            glColor3f(0.3, 0.3, 0.3)

            # transform (rotate, translate) body accordingly
            (x,y,z) = body.getPosition()
            R = body.getRotation()

            rot = [R[0], R[3], R[6], 0.0,
                   R[1], R[4], R[7], 0.0,
                   R[2], R[5], R[8], 0.0,
                      x,    y,    z, 1.0]
            glMultMatrixd(rot)

            # switch different geom objects
            if type(geom) == ode.GeomBox:
                # cube
                (sx, sy, sz) = geom.getLengths()
                glScaled(sx, sy, sz)
                glutSolidCube(1)
            elif type(geom) == ode.GeomSphere:
                # sphere
                radius = geom.getRadius()
                glutSolidSphere(radius, 20, 20)
                
            elif type(geom) == ode.GeomCCylinder:
                # capped cylinder
                radius = geom.getParams()[0]
                length = geom.getParams()[1] - 2*radius
                quad = gluNewQuadric()
                # draw cylinder and two spheres, one at each end
                glTranslate(0.0, 0.0, -length/2)
                gluCylinder(quad, radius, radius, length, 32, 32)
                glutSolidSphere(radius, 20, 20)
                glTranslate(0.0, 0.0, length)
                glutSolidSphere(radius, 20, 20)

            # FIXME: sometimes cylinder attribute is undefined; this has something to
            # to with the pyODE hack, but we don't know anymore where it came from...  X-(
            elif hasattr(ode, 'GeomCylinder'):
                if type(geom) == ode.GeomCylinder:
                    # solid cylinder
                    radius = geom.getParams()[0]
                    length = geom.getParams()[1]
                    glTranslate(0.0, 0.0, -length/2)
                    quad = gluNewQuadric()
                    gluDisk(quad, 0, radius, 32, 1)
                    quad = gluNewQuadric()
                    gluCylinder(quad, radius, radius, length, 32, 32)
                    glTranslate(0.0, 0.0, length)
                    quad = gluNewQuadric()
                    gluDisk(quad, 0, radius, 32, 1)                
            else:
                # TODO: add other geoms here
                pass

        else:
            # no body found, then it must be a plane (we only draw planes)
            if type(geom) == ode.GeomPlane:
                # set color of plane (currently green)
                if self.isFloorGreen:
                    glColor3f(0.2, 0.6, 0.3)
                else:
                    glColor3f(0.2, 0.3, 0.8)

                # for planes, we need a Quadric object
                quad = gluNewQuadric()
                gluQuadricTexture(quad, GL_TRUE)

                p = geom.getParams()[0] # the normal vector to the plane
                d = geom.getParams()[1] # the distance to the origin
                q = (0.0, 0.0, 1.0)     # the normal vector of default gluDisks (z=0 plane)

                # calculate the cross product to get the rotation axis
                c = crossproduct(p,q)
                # calculate the angle between default normal q and plane normal p
                theta = acos(dotproduct(p,q) / (norm(p)*norm(q))) / pi * 180

                # rotate the plane
                glPushMatrix()
                glTranslate(d*p[0], d*p[1], d*p[2])
                glRotate(-theta, c[0], c[1], c[2])
                gluDisk(quad, 0, 20, 20, 1)
                glPopMatrix()

        glPopMatrix()
    
    @staticmethod
    def _loadTexture(textureFile):
        image = open(textureFile)
        ix = image.size[0]
        iy = image.size[1]

        image = image.tostring("raw", "RGBX", 0, -1)

        # Create Texture
        textures = glGenTextures(3)
        glBindTexture(GL_TEXTURE_2D, textures[0])       # 2d texture (x and y size)

        glPixelStorei(GL_UNPACK_ALIGNMENT,1)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_BYTE, image)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

        # Create Linear Filtered Texture 
        glBindTexture(GL_TEXTURE_2D, textures[1])
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)

        # Create MipMapped Texture
        glBindTexture(GL_TEXTURE_2D, textures[2])
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR_MIPMAP_NEAREST)
        gluBuild2DMipmaps(GL_TEXTURE_2D, 3, ix, iy, GL_RGBA, GL_UNSIGNED_BYTE, image)
        return textures 

    
    def _drawfunc (self):
        """ draw callback function """
        # Draw the scene
        self.prepare_GL()
        
        self.dataLock.acquire()
        if self.body_geom != None:
            for (b,g) in self.body_geom:
                self.draw_body_geom(b,g)
        self.dataLock.release()
        
        glutSwapBuffers()
        if self.captureScreen:
            self._screenshot()  
    
    def _idlefunc(self):
        t = self.dt - (time.time() - self.lasttime)
        if (t > 0):
            time.sleep(t)
        self.lasttime = time.time()
        glutPostRedisplay () 
    
    def _motionfunc(self, x, z):
        """Control the zoom factor"""
        if not self.mouseView: return
        zn = 2.75*float(z)/self.height + 0.25   # [0.25,3]
        self.viewDistance = 3.0 * zn*zn
        self._passivemotionfunc(x, z)

    def _passivemotionfunc(self, x, z):
        """ Store the mouse coordinates (relative to center and normalized)
         the eye does not exactly move on a unit hemisphere; we fudge the projection
         a little by shifting the hemisphere into the ground by 0.1 units,
         such that approaching the perimeter dows not cause a huge change in the
         viewing direction. The limit for l is thus cos(arcsin(0.1))."""
        if not self.mouseView: return
        x1 = 3*float(x)/self.width  - 1.5
        z1 = -3*float(z)/self.height + 1.5
        lsq  = x1*x1 + z1*z1
        l = sqrt(lsq)
        if l > 0.994987:
            # for mouse outside window, project onto the unit circle
            x1 = x1/l
            z1 = z1/l
            y1 = 0
        else:
            y1 = max(0.0,sqrt(1.0 - x1*x1-z1*z1) - 0.1)
        self.lasty = y1
        self.lastx = x1
        self.lastz = z1
    
    def _screenshot(self, path_prefix='.', format='PNG'):
        """Saves a screenshot of the current frame buffer.
        The save path is <path_prefix>/.screenshots/shot<num>.png
        The path is automatically created if it does not exist.
        Shots are automatically numerated based on how many files
        are already in the directory."""

        if self.counter == self.frameT:
            self.counter=1
            dir = os.path.join(path_prefix, 'screenshots')
            if not os.path.exists(dir):
                os.makedirs(dir)
 
            num_present = len(os.listdir(dir))
            num_digits = len(str(num_present))
            index = '0' * (5-num_digits) + str(num_present) 

            path = os.path.join(dir, 'shot' + index +'.'+format.lower())
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            data = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
            image = Image.fromstring("RGB", (self.width, self.height), data)
            image = image.transpose( Image.FLIP_TOP_BOTTOM)
            image.save(path, format)
            print 'Image saved to %s'% (os.path.basename(path))
        else:
            self.counter+=1
        
        self.isCapturing = False

    def stop(self):
        sys.exit();
    

