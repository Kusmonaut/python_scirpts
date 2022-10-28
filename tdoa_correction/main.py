from sympy import *

tdoa = 1160
z1 = 2893
z2 = 2563
d = 10310

Piecewise((-sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3)/2 - sqrt(4*d/sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3) + 8*tdoa/3 - 8*z1**2/3 + 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 4/3)/2, Eq(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2, 1/12)), (-sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2 - sqrt(4*d/sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3))) + 8*tdoa/3 - 8*z1**2/3 - 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 4/3 + 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2, True))
Piecewise((-sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3)/2 + sqrt(4*d/sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3) + 8*tdoa/3 - 8*z1**2/3 + 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 4/3)/2, Eq(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2, 1/12)), (-sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2 + sqrt(4*d/sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3))) + 8*tdoa/3 - 8*z1**2/3 - 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 4/3 + 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2, True))
Piecewise((sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3)/2 - sqrt(-4*d/sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3) + 8*tdoa/3 - 8*z1**2/3 + 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 4/3)/2, Eq(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2, 1/12)), (sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2 - sqrt(-4*d/sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3))) + 8*tdoa/3 - 8*z1**2/3 - 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 4/3 + 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2, True))
Piecewise((sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3)/2 + sqrt(-4*d/sqrt(4*tdoa/3 - 4*z1**2/3 - 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 2/3) + 8*tdoa/3 - 8*z1**2/3 + 2*(-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**(1/3) + 4/3)/2, Eq(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2, 1/12)), (sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2 + sqrt(-4*d/sqrt(4*tdoa/3 - 4*z1**2/3 + 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 2/3 - 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3))) + 8*tdoa/3 - 8*z1**2/3 - 2*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3) + 4/3 + 2*(d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)/(3*(d**2/4 + sqrt((-d**2/2 - (-2*tdoa + 2*z1**2 - 1)**3/108 + (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/3)**2/4 + (d**2 - 4*tdoa**2/3 + 8*tdoa*z1**2/3 - tdoa/3 - 4*z1**4/3 + z1**2/3 + z2**2 - 1/12)**3/27) + (-2*tdoa + 2*z1**2 - 1)**3/216 - (-2*tdoa + 2*z1**2 - 1)*(-d**2 + tdoa**2 - 2*tdoa*z1**2 + z1**4 - z2**2)/6)**(1/3)))/2, True))

if __name__ == "__main__":
    
    z1, z2, d, tdoa, x, y = symbols('z1 z2 d tdoa x y', real=True)
    eq = Eq(tdoa + root((d-x)**2 + z2**2,2), x**2 + z1**2)
    # eq = Eq(root((a-x)**2 + b**2, 2) - x**2 , c**2)
    # eq = Eq(x**4 + 2*x**2*c -x**2- 2*a*x -a**2 - b**2 - c**2, 0)

    sol = solveset(eq, symbol=x)
    print(sol)