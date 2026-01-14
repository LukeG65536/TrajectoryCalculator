import trajectory_math

v = 12
t = .75
g=-10

a = trajectory_math.get_a(v,t,-10)
b = trajectory_math.get_b(t)
c = -2

u = trajectory_math.get_u(a,b,c)
dist = (-b-u**.5)*(.5)*(1/a)
dtdx = trajectory_math.get_dtdx(v,t,c)
dvdx = trajectory_math.get_dvdx(v,t,c)
dadt = trajectory_math.get_da(v,t,0,1,g)
dadv = trajectory_math.get_da(v,t,1,0,g)

print('a'+str(a))
print('b'+str(b))
print('c'+str(c))

print('u'+str(u))
print('dist'+str(dist))
print('dtdx'+str(dtdx))
print('dvdx'+str(dvdx))
print('dadt'+str(dadt))
print('dadv'+str(dadv))