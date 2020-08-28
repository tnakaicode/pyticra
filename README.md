pyticra
=======

A Python library for handling TICRA Tools simulation design and output.

Definition and Normalization of Field Components
------

$$\begin{aligned}
    E &= \frac{1}{k \sqrt{2\zeta}} E_{SI} \\
    H &= \frac{1}{k} \sqrt{\frac{\zeta}{2}} H_{SI} \\
    J^e &= \frac{1}{k} \sqrt{\frac{\zeta}{2}} J^e_{SI} \\
    J^m &= \frac{1}{k \sqrt{2\zeta}} J^m_{SI} \\
\end{aligned} $$

$$\begin{aligned}
    [E_{SI}] &= volts / meters \\
    [H_{SI}] &= ampere / meters \\
    [J^e_{SI}] &= ampere / meters \\
    [J^m_{SI}] &= volts / meters \\
\end{aligned} $$

$$\begin{aligned}
    P &= \frac{1}{2} Re(E_{SI} \times H^*_{SI}) \\
    &= k^2 Re(E \times H^*)
\end{aligned}$$

Planar Grid Polarizarition
-----

- linear
- circular
- rho_phi
- major_minor
- liner_xpd
  - cross-polar discrimination ratio
- circular_xpd
- rho_phi_xpd
- majo_minor_xpd
- power
- poynting
  - unit [Watts/m^2]

IGRID
---

- 1  uv-grid
- 2  $\rho\phi$-grid
- 3  xy-grid
- 4  Elevation over Azimuth
- 5  Elevation and  Azimuth
- 6  Azimuth   over Elevation
- 7  $\theta\phi$-grid
- 8  $\phi z$-grid
- 9  Azimuth over Elevation (EDX Definition)
- 10 Elevation over Azimuth (EDX Definition)

IGRID uv-grid
---

r = (u, v, $\sqrt{1-u^2-v^2}$)  
u = $\sin\theta\cos\phi$  
v = $\sin\theta\sin\phi$  

IGRID $\rho\phi$-grid
---

r = $-\sin(Az)\cos(El)$, $\sin(El)$, $\cos(Az)\cos(El)$  
