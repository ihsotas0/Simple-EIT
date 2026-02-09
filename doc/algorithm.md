# Lumped Element Model Problem

Using Kirchhoff's Current Law at all 4 nodes gives a generalized problem statement:

$$

\begin{pmatrix}
0 \\
0 \\
0 \\
0
\end{pmatrix}

=

\underbrace{
\begin{pmatrix}
Y_{12}+Y_{13}+Y_{14} & -Y_{12} & -Y_{13} & -Y_{14} \\
-Y_{12} & Y_{12}+Y_{23}+Y_{24} & -Y_{23} & -Y_{24} \\
Y_{13} & Y_{23} & -Y_{13}-Y_{23}-Y_{34} & Y_{34} \\
Y_{14} & Y_{24} & Y_{34} & -Y_{14}-Y_{24}-Y_{34}
\end{pmatrix}
}_{\mathbf{Y}}

\underbrace{
\begin{pmatrix}
V_{1} \\
V_{2} \\
V_{3} \\
V_{4}
\end{pmatrix}
}_{\vec v}

$$

$$ 0 = \mathbf{Y} \vec v \qquad \mathbf{Y} = \text{recip}(\mathbf{Z}) =
\mathbf{Z}^{\circ -1} $$

Or, in terms of voltage differences (which will not be used since the matrix is
not square):

$$

\begin{pmatrix}
0 \\
0 \\
0 \\
0
\end{pmatrix}

= 
\begin{pmatrix}
Y_{12} & Y_{13} & Y_{14} & 0 & 0 & 0 \\
-Y_{12} & 0 & 0 & Y_{23} & Y_{24} & 0 \\
0 & Y_{13} & 0 & Y_{23} & 0 & -Y_{34} \\
0 & 0 & Y_{14} & 0 & Y_{24} & Y_{34}
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

Forward problem: The complex matrix $\mathbf{Z}$ is known. Given a value $v_i = c$,
where $c \neq 0$, and an adjacent ground node, calculate $v_j \,|\, j \neq i$.

To do this, we first find the null space vector:

$$

\begin{pmatrix}
1 & 0 & 0 & -1 \\
0 & 1 & 0 & -1 \\
0 & 0 & 1 & -1 \\
0 & 0 & 0 & 0
\end{pmatrix}

\rightarrow

\begin{cases}
    V_1 - V_4 = 0 \\
    V_2 - V_4 = 0 \\
    V_3 - V_4 = 0 \\
\end{cases}

$$

(This logic applies for all possible values of $i$.)

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

# Network Model

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


$$ \vec i = \mathbf{Y} \vec v_d $$

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
Y_{12} & 0 & 0 & 0 & 0 & 0 \\
0 & Y_{13} & 0 & 0 & 0 & 0 \\
0 & 0 & Y_{14} & 0 & 0 & 0 \\
0 & 0 & 0 & Y_{23} & 0 & 0 \\
0 & 0 & 0 & 0 & Y_{24} & 0 \\
0 & 0 & 0 & 0 & 0 & Y_{34}
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
Y_{12} & 0 & 0 & 0 & 0 & 0 \\
0 & Y_{13} & 0 & 0 & 0 & 0 \\
0 & 0 & Y_{14} & 0 & 0 & 0 \\
0 & 0 & 0 & Y_{23} & 0 & 0 \\
0 & 0 & 0 & 0 & Y_{24} & 0 \\
0 & 0 & 0 & 0 & 0 & Y_{34}
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




