"""XTest input helper for the isolated display owned by run_visual_checks.py."""
import ctypes,os,time,sys
x=ctypes.CDLL('libX11.so.6');t=ctypes.CDLL('libXtst.so.6')
ptr=ctypes.c_void_p;ul=ctypes.c_ulong;ui=ctypes.c_uint
x.XOpenDisplay.argtypes=[ctypes.c_char_p];x.XOpenDisplay.restype=ptr
d=x.XOpenDisplay(os.environ['DISPLAY'].encode());assert d
x.XDefaultRootWindow.argtypes=[ptr];x.XDefaultRootWindow.restype=ul
x.XQueryTree.argtypes=[ptr,ul,ctypes.POINTER(ul),ctypes.POINTER(ul),ctypes.POINTER(ctypes.POINTER(ul)),ctypes.POINTER(ui)]
x.XFetchName.argtypes=[ptr,ul,ctypes.POINTER(ctypes.c_char_p)]
x.XSetInputFocus.argtypes=[ptr,ul,ctypes.c_int,ul]
x.XFlush.argtypes=[ptr]
x.XGetInputFocus.argtypes=[ptr,ctypes.POINTER(ul),ctypes.POINTER(ctypes.c_int)]
root=ul();parent=ul();children=ctypes.POINTER(ul)();count=ui()
x.XQueryTree(d,x.XDefaultRootWindow(d),ctypes.byref(root),ctypes.byref(parent),ctypes.byref(children),ctypes.byref(count))
for i in range(count.value):
 name=ctypes.c_char_p();x.XFetchName(d,children[i],ctypes.byref(name))
 print(hex(children[i]),name.value)
 if name.value and b'Furnace' in name.value:
  x.XSetInputFocus(d,children[i],2,0)
x.XFlush(d);time.sleep(.05)
t.XTestFakeMotionEvent.argtypes=[ptr,ctypes.c_int,ctypes.c_int,ctypes.c_int,ul]
t.XTestFakeButtonEvent.argtypes=[ptr,ui,ctypes.c_int,ul]
t.XTestFakeKeyEvent.argtypes=[ptr,ui,ctypes.c_int,ul]
x.XKeysymToKeycode.argtypes=[ptr,ul];x.XKeysymToKeycode.restype=ui
x.XStringToKeysym.argtypes=[ctypes.c_char_p];x.XStringToKeysym.restype=ul
for a in sys.argv[1:]:
 p=a.split(',')
 if p[0]=='move':t.XTestFakeMotionEvent(d,-1,int(p[1]),int(p[2]),0)
 elif p[0]=='click':
  t.XTestFakeButtonEvent(d,int(p[1]),1,0);x.XFlush(d);time.sleep(.04)
  t.XTestFakeButtonEvent(d,int(p[1]),0,0)
 elif p[0] in ('down','up'):
  code=x.XKeysymToKeycode(d,x.XStringToKeysym(p[1].encode()));t.XTestFakeKeyEvent(d,code,p[0]=='down',0)
 elif p[0]=='wait':time.sleep(float(p[1]))
 x.XFlush(d);time.sleep(.04)
