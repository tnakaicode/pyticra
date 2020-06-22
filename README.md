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
