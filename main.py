Cw = 1
Ch = 1
d = 1

Vw = 1# viewport widht
Vh = 1 # viewport height

def canvasToViewport(x, y):
    return  (x*Vw/Cw, y*Vh/Ch, d)

def traceRay(O, D, t_min, t_max): ...