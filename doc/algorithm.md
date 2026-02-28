# Problem Statements

Forward problem: The complex matrix $\mathbf{Z}$ is known. Given a value $v_i = c$,
where $c \neq 0$, and an adjacent ground node, calculate $v_j \,|\, j \neq i$.

Inverse problem: Find the complex matrix $\mathbf{Z}$ given 6 vectors, where
each represents a *different* possible $\vec v$ where $V_s = c$:

$$

\vec v = 

\begin{pmatrix}
V_s \\
\\
\\
\\
\\
V_{34} \\
\end{pmatrix}

,

\begin{pmatrix}
\\
V_s \\
\\
\\
V_{24} \\
\\
\end{pmatrix}

,

\begin{pmatrix}
\\
\\
V_s \\
V_{23} \\
\\
\\
\end{pmatrix}

,

\begin{pmatrix}
\\
\\
V_{14} \\
V_s \\
\\
\\
\end{pmatrix}

,

\begin{pmatrix}
\\
V_{13} \\
\\
\\
V_s \\
\\
\end{pmatrix}

,

\begin{pmatrix}
V_{12} \\
\\
\\
\\
\\
V_s \\
\end{pmatrix}
$$



Above equations are wrong. $V_{12} = V_{21}$, etc.

# Lumped Element Model Problem

Incidence matrix for voltage differences:

$$

\underbrace{

\begin{pmatrix}
V_{12} \\
V_{13} \\
V_{14} \\
V_{23} \\
V_{24} \\
V_{34}
\end{pmatrix}
}_{\vec v_d}

=

\underbrace{
\begin{pmatrix}
-1 & 1 & 0 & 0 \\
-1 & 0 & 1 & 0 \\
-1 & 0 & 0 & 1 \\
0 & -1 & 1 & 0 \\
0 & -1 & 0 & 1 \\
0 & 0 & -1 & 1
\end{pmatrix}
}_{\mathbf{A}}

\underbrace{
\begin{pmatrix}
V_1 \\
V_2 \\
V_3 \\
V_4
\end{pmatrix}
}_{\vec v}

$$

Nullspace of voltage difference incidence matrix (less important):

$$

N(\mathbf{A}) = c

\begin{pmatrix}
1 \\
1 \\
1 \\
1
\end{pmatrix}

$$

$$

\dim N(\mathbf{A}) = 1

$$

Kirchoff's Current Law:

$$

\begin{pmatrix}
0 \\
0 \\
0 \\
0 \\
\end{pmatrix}

=

\underbrace{

\begin{pmatrix}
-1 & -1 & -1 & 0 & 0 & 0 \\
1 & 0 & 0 & -1 & -1 & 0 \\
0 & 1 & 0 & 1 & 0 & -1 \\
0 & 0 & 1 & 0 & 1 & 1
\end{pmatrix}
}_{\mathbf{A^T}}

\underbrace{
\begin{pmatrix}
I_{12} \\
I_{13} \\
I_{14} \\
I_{23} \\
I_{24} \\
I_{34}
\end{pmatrix}
}_{\vec i}


$$

Nullspace of Kirchoff's Current Law (very important):

$$

N(\mathbf{A^T}) = c_1

\begin{pmatrix}
1 \\
-1 \\
0 \\
1 \\
0 \\
0
\end{pmatrix}

+ c_2

\begin{pmatrix}
1 \\
0 \\
-1 \\
0 \\
1 \\
0
\end{pmatrix}

+ c_3

\begin{pmatrix}
0 \\
1 \\
-1 \\
0 \\
0 \\
1
\end{pmatrix}

$$

$$

\dim N(\mathbf{A^T}) = 3

$$

Ohm's Law:


$$ \mathbf{Y} = \text{recip}(\mathbf{Z}) = \mathbf{Z}^{\circ -1} $$

$$ \vec i = -\mathbf{Y} \vec v_d $$

$$

\begin{pmatrix}
I_{12} \\
I_{13} \\
I_{14} \\
I_{23} \\
I_{24} \\
I_{34}
\end{pmatrix}

=

\begin{pmatrix}
-Y_{12} & 0 & 0 & 0 & 0 & 0 \\
0 & -Y_{13} & 0 & 0 & 0 & 0 \\
0 & 0 & -Y_{14} & 0 & 0 & 0 \\
0 & 0 & 0 & -Y_{23} & 0 & 0 \\
0 & 0 & 0 & 0 & -Y_{24} & 0 \\
0 & 0 & 0 & 0 & 0 & -Y_{34}
\end{pmatrix}

\begin{pmatrix}
V_{12} \\
V_{13} \\
V_{14} \\
V_{23} \\
V_{24} \\
V_{34}
\end{pmatrix}

$$


$$ \boxed{0 = \mathbf{A^T} \mathbf{Y} \mathbf{A} \vec v = \mathbf{B} \vec v} $$

$$ 

\begin{pmatrix}
0 \\
0 \\
0 \\
0 \\
\end{pmatrix}

=

\begin{pmatrix}
-1 & -1 & -1 & 0 & 0 & 0 \\
1 & 0 & 0 & -1 & -1 & 0 \\
0 & 1 & 0 & 1 & 0 & -1 \\
0 & 0 & 1 & 0 & 1 & 1
\end{pmatrix}

\begin{pmatrix}
-Y_{12} & 0 & 0 & 0 & 0 & 0 \\
0 & -Y_{13} & 0 & 0 & 0 & 0 \\
0 & 0 & -Y_{14} & 0 & 0 & 0 \\
0 & 0 & 0 & -Y_{23} & 0 & 0 \\
0 & 0 & 0 & 0 & -Y_{24} & 0 \\
0 & 0 & 0 & 0 & 0 & -Y_{34}
\end{pmatrix}

\begin{pmatrix}
-1 & 1 & 0 & 0 \\
-1 & 0 & 1 & 0 \\
-1 & 0 & 0 & 1 \\
0 & -1 & 1 & 0 \\
0 & -1 & 0 & 1 \\
0 & 0 & -1 & 1
\end{pmatrix}

\begin{pmatrix}
V_1 \\
V_2 \\
V_3 \\
V_4
\end{pmatrix}

$$

$$ 

\begin{pmatrix}
0 \\
0 \\
0 \\
0 \\
\end{pmatrix}

=

\begin{pmatrix}
-1 & -1 & -1 & 0 & 0 & 0 \\
1 & 0 & 0 & -1 & -1 & 0 \\
0 & 1 & 0 & 1 & 0 & -1 \\
0 & 0 & 1 & 0 & 1 & 1
\end{pmatrix}

\begin{pmatrix}
-Y_{12} & 0 & 0 & 0 & 0 & 0 \\
0 & -Y_{13} & 0 & 0 & 0 & 0 \\
0 & 0 & -Y_{14} & 0 & 0 & 0 \\
0 & 0 & 0 & -Y_{23} & 0 & 0 \\
0 & 0 & 0 & 0 & -Y_{24} & 0 \\
0 & 0 & 0 & 0 & 0 & -Y_{34}
\end{pmatrix}

\begin{pmatrix}
V_2-V_1 \\
V_3-V_1 \\
V_4-V_1 \\
V_3-V_2 \\
V_4-V_2 \\
V_4-V_3
\end{pmatrix}

$$

$$ 

\begin{pmatrix}
0 \\
0 \\
0 \\
0 \\
\end{pmatrix}

=

\begin{pmatrix}
-1 & -1 & -1 & 0 & 0 & 0 \\
1 & 0 & 0 & -1 & -1 & 0 \\
0 & 1 & 0 & 1 & 0 & -1 \\
0 & 0 & 1 & 0 & 1 & 1
\end{pmatrix}

\begin{pmatrix}
-Y_{12}(V_2-V_1) \\
-Y_{13}(V_3-V_1) \\
-Y_{14}(V_4-V_1) \\
-Y_{23}(V_3-V_2) \\
-Y_{24}(V_4-V_2) \\
-Y_{34}(V_4-V_3)
\end{pmatrix}

$$

$$

\begin{pmatrix}
-Y_{12}(V_2-V_1) \\
-Y_{13}(V_3-V_1) \\
-Y_{14}(V_4-V_1) \\
-Y_{23}(V_3-V_2) \\
-Y_{24}(V_4-V_2) \\
-Y_{34}(V_4-V_3)
\end{pmatrix}

=

c_1

\begin{pmatrix}
1 \\
-1 \\
0 \\
1 \\
0 \\
0
\end{pmatrix}

+ c_2

\begin{pmatrix}
1 \\
0 \\
-1 \\
0 \\
1 \\
0
\end{pmatrix}

+ c_3

\begin{pmatrix}
0 \\
1 \\
-1 \\
0 \\
0 \\
1
\end{pmatrix}

$$

$$

-Y_{12}(V_2-V_1) = c_1 + c_2 \\
-Y_{13}(V_3-V_1) = c_3 - c_1 \\
-Y_{14}(V_4-V_1) = - c_2 - c_3 \\
c_1 = -Y_{23}(V_3-V_2) \\
c_2 = -Y_{24}(V_4-V_2) \\
c_3 = -Y_{34}(V_4-V_3) \\

$$




