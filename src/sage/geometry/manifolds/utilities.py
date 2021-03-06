r"""
Utilities for calculus and graphical outputs

This module defines helper functions which are used for simplifications of
symbolic expressions or for graphical outputs.

AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2013-2015) : initial version

"""

#******************************************************************************
#       Copyright (C) 2015 Eric Gourgoulhon <eric.gourgoulhon@obspm.fr>
#       Copyright (C) 2015 Michal Bejger <bejger@camk.edu.pl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.structure.sage_object import SageObject
from sage.version import version

def simple_determinant(aa):
    r"""
    Compute the determinant of a square matrix.

    This function, which is based on Laplace's cofactor expansion, is a
    workaround for a bug in Sage method
    :meth:`~sage.matrix.matrix2.Matrix.determinant`
    (cf. http://trac.sagemath.org/ticket/14403).

    NB: this bug was fixed in Sage 6.2.

    EXAMPLE::

        sage: a = matrix([[sqrt(x),0,0,0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        sage: a.determinant() # this resulted in an error in Sage < 6.2
        sqrt(x)
        sage: from sage.geometry.manifolds.utilities import simple_determinant
        sage: simple_determinant(a)
        sqrt(x)

    """
    from sage.matrix.constructor import matrix
    n = aa.nrows()
    if n == 1:
        return aa[0,0]
    res = 0
    sign = True
    for i in range(n):
        b = []
        for k in range(i):
            r = []
            for l in range(1,n):
               r.append(aa[k,l])
            b.append(r)
        for k in range(i+1,n):
            r = []
            for l in range(1,n):
               r.append(aa[k,l])
            b.append(r)
        bb = matrix(b)
        if sign:
            res += aa[i,0] * simple_determinant(bb)
        else:
            res -= aa[i,0] * simple_determinant(bb)
        sign = not sign
    return res

def simplify_sqrt_real(expr):
    r"""
    Simplify sqrt in symbolic expressions in the real domain.

    EXAMPLES:

    Simplifications of basic expressions::

        sage: from sage.geometry.manifolds.utilities import simplify_sqrt_real
        sage: simplify_sqrt_real( sqrt(x^2) )
        abs(x)
        sage: assume(x<0)
        sage: simplify_sqrt_real( sqrt(x^2) )
        -x
        sage: simplify_sqrt_real( sqrt(x^2-2*x+1) )
        -x + 1
        sage: simplify_sqrt_real( sqrt(x^2) + sqrt(x^2-2*x+1) )
        -2*x + 1

    This improves over Sage's
    :meth:`~sage.symbolic.expression.Expression.canonicalize_radical` which yields
    incorrect results when x<0::

        sage: forget()  # removes the assumption x<0
        sage: sqrt(x^2).canonicalize_radical()
        x
        sage: assume(x<0)
        sage: sqrt(x^2).canonicalize_radical() # wrong output
        x
        sage: sqrt(x^2-2*x+1).canonicalize_radical() # wrong output
        x - 1
        sage: ( sqrt(x^2) + sqrt(x^2-2*x+1) ).canonicalize_radical() # wrong output
        2*x - 1

    Simplification of nested sqrt's::

        sage: forget()  # removes the assumption x<0
        sage: simplify_sqrt_real( sqrt(1 + sqrt(x^2)) )
        sqrt(abs(x) + 1)
        sage: assume(x<0)
        sage: simplify_sqrt_real( sqrt(1 + sqrt(x^2)) )
        sqrt(-x + 1)
        sage: simplify_sqrt_real( sqrt(x^2 + sqrt(4*x^2) + 1) )
        -x + 1

    Again, :meth:`~sage.symbolic.expression.Expression.canonicalize_radical`
    fails on the last one::

        sage: (sqrt(x^2 + sqrt(4*x^2) + 1)).canonicalize_radical()  # wrong output
        x + 1

    """
    from sage.symbolic.ring import SR
    from sage.calculus.calculus import maxima
    from sage.functions.other import sqrt
    # 1/ Search for the sqrt's in expr
    sexpr = str(expr)
    if 'sqrt(' not in sexpr:  # no sqrt to simplify
        return expr
    if 'D[' in sexpr:
        return expr    #!# the code below is not capable of simplifying
                       # expressions with symbolic derivatives denoted by Pynac
                       # symbols of the type D[0]
    # Lists to store the positions of all the top-level sqrt's in sexpr:
    pos_sqrts = []  # position of first character, i.e. 's' of 'sqrt(...)'
    pos_after = []  # position of character immediatelty after 'sqrt(...)'
    the_sqrts = []  # the sqrt sub-expressions in sexpr, i.e. 'sqrt(...)'
    pos_max = len(sexpr) - 6
    pos = 0
    while pos < pos_max:
        if sexpr[pos:pos+5] == 'sqrt(':
            pos_sqrts.append(pos)
            parenth = 1
            scan = pos+5
            while parenth != 0:
                if sexpr[scan] == '(': parenth += 1
                if sexpr[scan] == ')': parenth -= 1
                scan += 1
            the_sqrts.append( sexpr[pos:scan] )
            pos_after.append(scan)
            pos = scan
        else:
            pos += 1
    # 2/ Search for sub-sqrt's:
    for i in range(len(the_sqrts)):
        argum = the_sqrts[i][5:-1]  # the sqrt argument
        if 'sqrt(' in argum:
            simpl = simplify_sqrt_real(SR(argum))
            the_sqrts[i] = 'sqrt(' + str(simpl) + ')'
    # 3/ Simplifications of the sqrt's
    new_expr = ""    # will contain the result
    pos0 = 0
    for i, pos in enumerate(pos_sqrts):
        # radcan is called on each sqrt:
        x = SR(the_sqrts[i])
        argum = x.operands()[0] # the argument of sqrt
        den = argum.denominator()
        if den != 1:  # the argument of sqrt is a fraction
            num = argum.numerator()
            if num < 0 or den < 0:
                x = sqrt(-num) / sqrt(-den)  # new equivalent expression for x
        simpl = SR(x._maxima_().radcan())
        if str(simpl)[:5] != 'sqrt(':
            # the absolute value of radcan's output is taken, the call to simplify()
            # taking into account possible assumptions regarding the sign of simpl:
            ssimpl = str(abs(simpl).simplify())
        else:
            ssimpl = str(simpl)
        # search for abs(1/sqrt(...)) term to simplify it into 1/sqrt(...):
        pstart = ssimpl.find('abs(1/sqrt(')
        if pstart != -1:
            ssimpl = ssimpl[:pstart] + ssimpl[pstart+3:] # getting rid of 'abs'
        new_expr += sexpr[pos0:pos] + '(' + ssimpl + ')'
        pos0 = pos_after[i]
    new_expr += sexpr[pos0:]
    return SR(new_expr)

def simplify_abs_trig(expr):
    r"""
    Simplify abs(sin(...)) in symbolic expressions.

    EXAMPLES::

        sage: forget()  # for doctests only
        sage: M = Manifold(3, 'M')
        sage: X.<x,y,z> = M.chart(r'x y:(0,pi) z:(-pi/3,0)')
        sage: X.coord_range()
        x: (-oo, +oo); y: (0, pi); z: (-1/3*pi, 0)

    Since ``x`` spans all `\RR`, no simplification of ``abs(sin(x))``
    occurs, while ``abs(sin(y))`` and ``abs(sin(3*z))`` are correctly
    simplified, given that `y \in (0,\pi)` and `z \in (-\pi/3,0)`::

        sage: from sage.geometry.manifolds.utilities import simplify_abs_trig
        sage: simplify_abs_trig( abs(sin(x)) + abs(sin(y)) + abs(sin(3*z)) )
        abs(sin(x)) + sin(y) - sin(3*z)

    Note that neither Sage's function
    :meth:`~sage.symbolic.expression.Expression.simplify_trig` nor
    :meth:`~sage.symbolic.expression.Expression.simplify_full`
    works in this case::

        sage: s = abs(sin(x)) + abs(sin(y)) + abs(sin(3*z))
        sage: s.simplify_trig()
        abs(4*cos(z)^2 - 1)*abs(sin(z)) + abs(sin(x)) + abs(sin(y))
        sage: s.simplify_full()
        abs(4*cos(z)^2 - 1)*abs(sin(z)) + abs(sin(x)) + abs(sin(y))

    despite the following assumptions hold::

        sage: assumptions()
        [x is real, y is real, y > 0, y < pi, z is real, z > -1/3*pi, z < 0]

    Additional checks are::

        sage: simplify_abs_trig( abs(sin(y/2)) )  # shall simplify
        sin(1/2*y)
        sage: simplify_abs_trig( abs(sin(2*y)) )  # must not simplify
        abs(sin(2*y))
        sage: simplify_abs_trig( abs(sin(z/2)) )  # shall simplify
        -sin(1/2*z)
        sage: simplify_abs_trig( abs(sin(4*z)) )  # must not simplify
        abs(sin(4*z))

    """
    from sage.symbolic.ring import SR
    from sage.symbolic.constants import pi
    sexpr = str(expr)
    if 'abs(sin(' not in sexpr:  # nothing to simplify
        return expr
    tp = []
    val = []
    for pos in range(len(sexpr)):
        if sexpr[pos:pos+8] == 'abs(sin(':
            # finding the end of abs argument:
            scan = pos+4 # start of abs
            parenth = 1
            while parenth != 0:
                if sexpr[scan] == '(': parenth += 1
                if sexpr[scan] == ')': parenth -= 1
                scan += 1
            pos_abs_end = scan
            # finding the end of sin argument:
            scan = pos+8 # start of sin
            parenth = 1
            while parenth != 0:
                if sexpr[scan] == '(': parenth += 1
                if sexpr[scan] == ')': parenth -= 1
                scan += 1
            pos_sin_end = scan
            # if the abs contains only the sinus, the simplification can be tried:
            if pos_sin_end == pos_abs_end-1:
                tp.append(pos)
                val.append( sexpr[pos:pos_abs_end] )
    simp = []
    for v in val:
        # argument of the sinus:
        sx = v[8:-2]
        x = SR(sx)
        if x>=0 and x<=pi:
            simp.append('sin(' + sx + ')')
        elif x>=-pi and x<=0:
            simp.append('(-sin(' + sx + '))')
        else:
            simp.append(v)  # no simplification is applicable
    nexpr = ""
    pos0 = 0
    for i, pos in enumerate(tp):
        nexpr += sexpr[pos0:pos] + simp[i]
        pos0 = pos + len(val[i])
    nexpr += sexpr[pos0:]
    return SR(nexpr)



def simplify_chain(expr):
    r"""
    Apply a chain of simplications to a symbolic expression.

    This is the simplification chain used in calculus involving functions
    of coordinates in a given chart, as implemented in
    :class:`~sage.geometry.manifolds.chart.FunctionChart`.

    The chain is formed by the following functions, called
    successively:

    #. :meth:`~sage.symbolic.expression.Expression.simplify_factorial`
    #. :meth:`~sage.symbolic.expression.Expression.simplify_trig`
    #. :meth:`~sage.symbolic.expression.Expression.simplify_rational`
    #. :func:`simplify_sqrt_real`
    #. :func:`simplify_abs_trig`
    #. :meth:`~sage.symbolic.expression.Expression.canonicalize_radical`
       (for Sage >= 6.5) or
       :meth:`~sage.symbolic.expression.Expression.simplify_radical` (for
       Sage < 6.5)
    #. :meth:`~sage.symbolic.expression.Expression.simplify_log`
    #. :meth:`~sage.symbolic.expression.Expression.simplify_rational`
    #. :meth:`~sage.symbolic.expression.Expression.simplify_trig`

    """
    expr = expr.simplify_factorial()
    expr = expr.simplify_trig()
    expr = expr.simplify_rational()
    expr = simplify_sqrt_real(expr)
    expr = simplify_abs_trig(expr)
    # In Sage 6.5, simplify_radical() has been renamed canonicalize_radical()
    #  (cf. http://trac.sagemath.org/11912):
    ver_pieces = version.split('.')
    mversion = float(ver_pieces[0] + '.' + ver_pieces[1])
    if mversion >= 6.5:
        expr = expr.canonicalize_radical()
    else:
        expr = expr.simplify_radical()
    expr = expr.simplify_log('one')
    expr = expr.simplify_rational()
    expr = expr.simplify_trig()
    return expr

def set_axes_labels(graph, xlabel, ylabel, zlabel, **kwds):
    r"""
    Set axes labels for a 3D graphics object.

    This is a workaround for the lack of axes labels in Sage 3D plots; it
    sets the labels as text3d objects at locations determined from the
    bounding box of the graphic object ``graph``.

    INPUT:

    - ``graph`` -- a 3D graphic object, as an instance of
      :class:`~sage.plot.plot3d.base.Graphics3d`
    - ``xlabel`` -- string for the x-axis label
    - ``ylabel`` -- string for the y-axis label
    - ``zlabel`` -- string for the z-axis label
    - ``**kwds`` -- options (e.g. color) for text3d

    OUTPUT:

    - the 3D graphic object with text3d labels added.

    """
    from sage.plot.plot3d.shapes2 import text3d
    xmin, ymin, zmin = graph.bounding_box()[0]
    xmax, ymax, zmax = graph.bounding_box()[1]
    dx = xmax - xmin
    dy = ymax - ymin
    dz = zmax - zmin
    x1 = xmin + dx / 2
    y1 = ymin + dy / 2
    z1 = zmin + dz / 2
    xmin1 = xmin - dx / 20
    xmax1 = xmax + dx / 20
    ymin1 = ymin - dy / 20
    zmin1 = zmin - dz / 20
    graph += text3d('  ' + xlabel, (x1, ymin1, zmin1), **kwds)
    graph += text3d('  ' + ylabel, (xmax1, y1, zmin1), **kwds)
    graph += text3d('  ' + zlabel, (xmin1, ymin1, z1), **kwds)
    return graph



from sage.symbolic.expression import Expression

class ExpressionNice(Expression):
    r"""
    Modification of the Expression class for a ''human-friendly''
    display of derivatives.

    INPUT:

    - ``ex`` -- symbolic expression

    OUTPUT:

    - modified string or LaTeX representation of the expression.

    """

    def __init__(self, ex):
        r"""
        Construct an instance of ExpressionNice using expression.

        TESTS::

            sage: f = function('f', x)
            sage: df = f.diff(x)
            sage: df
            D[0](f)(x)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: df_nice = ExpressionNice(df)
            sage: df_nice
            d(f)/dx

        """

        from sage.symbolic.ring import SR
        self._parent = SR
        Expression.__init__(self, SR, x=ex)

    def _repr_(self):
        r"""
        String representation of the object.

        EXAMPLES::

            sage: var('x y z')
            (x, y, z)
            sage: f = function('f', x, y)
            sage: g = f.diff(y).diff(x)
            sage: h = function('h', y, z)
            sage: k = h.diff(z)
            sage: fun = x*g + y*(k-z)^2
            sage: fun
            y*(z - D[1](h)(y, z))^2 + x*D[0, 1](f)(x, y)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            y*(z - d(h)/dz)^2 + x*d^2(f)/dxdy

        A check for a case when function variables are functions too:
        D[1](f)(x, g(x,y)) should render as d(f)/dg

            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y)
            sage: g = function('g', x, f)
            sage: fun = (g.diff(x))*x - x^2*f.diff(x,y)
            sage: fun
            -x^2*D[0, 1](f)(x, y) + (D[0](f)(x, y)*D[1](g)(x, f(x, y)) + D[0](g)(x, f(x, y)))*x
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            -x^2*d^2(f)/dxdy + (d(f)/dx*d(g)/df + d(g)/dx)*x

        Multiple differentiation over the same variable is grouped for brevity:
        D[0, 0](f)(x) should render as d^2(f)/dx^2

            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y)
            sage: fun = f.diff(x,x,y,y,x)*x
            sage: fun
            x*D[0, 0, 0, 1, 1](f)(x, y)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            x*d^5(f)/dx^3dy^2

        If diff operator is raised to some power, put brackets around:
        D[1](f)(x, y)^2 should render as (d(f)/dy)^2

            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y)
            sage: fun = f.diff(y)^2
            sage: fun
            D[1](f)(x, y)^2
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            (d(f)/dy)^2

        omit_function_args tests:
 
            sage: fun = fun*f
            sage: fun
            f(x, y)*D[1](f)(x, y)^2
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: omit_function_args(True)
            sage: ExpressionNice(fun)
            f*(d(f)/dy)^2

        """

        d = self._parent._repr_element_(self)

        import re
        # Fix for proper coercion of types:
        # http://www.sagemath.org/doc/faq/faq-usage.html#i-have-type-issues-using-scipy-cvxopt-or-numpy-from-sage
        Integer = int

        # find all occurences of diff
        list_d = []
        list_derivarives(self, list_d)

        # process the list
        for m in list_d:

            funcname = m[1]
            diffargs = m[3]
            numargs = len(diffargs)

            if numargs > 1:
                numargs = "^" + str(numargs)
            else:
                numargs = ""

            variables = m[4]

            # dictionary to group multiple occurences of differentiation: d/dxdx -> d/dx^2 etc.
            occ = dict((i, str(variables[i]) + "^" + str(diffargs.count(i)) if(diffargs.count(i)>1) else str(variables[i])) for i in diffargs)

            # re.sub for removing the brackets of possible composite variables
            res = "d" + str(numargs) + "(" + str(funcname) + ")/d" + "d".join([re.sub("\(.*?\)","", i) for i in occ.values()])

            # str representation of the operator
            s = self._parent._repr_element_(m[0])

            # if diff operator is raised to some power (m[4]), put brackets around
            if m[5]:
                res = "(" + res + ")^" + str(m[5])
                o = s + "^" + str(m[5])
            else:
                o = s

            d = d.replace(o, res)

        from sage.geometry.manifolds.chart import FunctionChart        
        if FunctionChart.omit_fargs: 

            list_f = [] 
            list_functions(self, list_f)

            for m in list_f:
                d = d.replace(m[1] + m[2], m[1])

        return d


    def _latex_(self):
        r"""
        LaTeX representation of the object.

        EXAMPLES::

            sage: var('x y z')
            (x, y, z)
            sage: f = function('f', x, y)
            sage: g = f.diff(y).diff(x)
            sage: h = function('h', y, z)
            sage: k = h.diff(z)
            sage: fun = x*g + y*(k-z)^2
            sage: fun
            y*(z - D[1](h)(y, z))^2 + x*D[0, 1](f)(x, y)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            y*(z - d(h)/dz)^2 + x*d^2(f)/dxdy
            sage: latex(ExpressionNice(fun))
            y {\left(z - \frac{\partial\,h}{\partial z}\right)}^{2} + x \frac{\partial^2\,f}{\partial x\partial y}

        A check for a case when function variables are functions too:
        D[1](f)(x, g(x,y)) should render as \frac{\partial\,f}{\partial g}

            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y)
            sage: g = function('g', x, f)
            sage: fun = (g.diff(x))*x - x^2*f.diff(x,y)
            sage: fun
            -x^2*D[0, 1](f)(x, y) + (D[0](f)(x, y)*D[1](g)(x, f(x, y)) + D[0](g)(x, f(x, y)))*x
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            -x^2*d^2(f)/dxdy + (d(f)/dx*d(g)/df + d(g)/dx)*x
            sage: latex(ExpressionNice(fun))
            -x^{2} \frac{\partial^2\,f}{\partial x\partial y} + {\left(\frac{\partial\,f}{\partial x} \frac{\partial\,g}{\partial f} + \frac{\partial\,g}{\partial x}\right)} x


        Multiple differentiation over the same variable is grouped for brevity:
        D[0, 0](f)(x) should render as \frac{\partial^2\,f}{\partial x^2}

            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y)
            sage: fun = f.diff(x,x,y,y,x)*x
            sage: fun
            x*D[0, 0, 0, 1, 1](f)(x, y)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            x*d^5(f)/dx^3dy^2
            sage: latex(ExpressionNice(fun))
            x \frac{\partial^5\,f}{\partial x^3\partial y^2}
            sage: f = function('f', x, y, latex_name=r"{\cal F}")
            sage: fun = f.diff(x,x,y,y,x)*x
            sage: latex(ExpressionNice(fun))
            x \frac{\partial^5\,{\cal F}}{\partial x^3\partial y^2}

        If diff operator is raised to some power, put brackets around:
        D[1](f)(x, y)^2 should render as (d(f)/dy)^2

            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y)
            sage: fun = f.diff(y)^2
            sage: fun
            D[1](f)(x, y)^2
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: ExpressionNice(fun)
            (d(f)/dy)^2
            sage: latex(ExpressionNice(fun))
            \left(\frac{\partial\,f}{\partial y}\right)^{2}

        omit_function_args() test:
 
            sage: var('x y')
            (x, y)
            sage: f = function('f', x, y, latex_name=r"{\cal F}")
            sage: fun = f*f.diff(y)^2
            sage: fun
            f(x, y)*D[1](f)(x, y)^2
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: omit_function_args(True)
            sage: latex(ExpressionNice(fun))
            {\cal F} \left(\frac{\partial\,{\cal F}}{\partial y}\right)^{2}
            sage: omit_function_args(False)     # bring back the default behavior  

        Testing the behavior if no latex_name of the function is given: 

            sage: var('x y')
            (x, y)
            sage: f = function('f_x', x, y)
            sage: fun = f.diff(y)
            sage: fun
            D[1](f_x)(x, y)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: latex(ExpressionNice(fun))
            \frac{\partial\,f_{x}}{\partial y}

        If latex_name, it should be used in LaTeX output:  

            sage: var('x y')
            (x, y)
            sage: f = function('f_x', x, y, latex_name=r"{\cal F}")
            sage: fun = f.diff(y)
            sage: fun
            D[1](f_x)(x, y)
            sage: from sage.geometry.manifolds.utilities import ExpressionNice
            sage: latex(ExpressionNice(fun))
            \frac{\partial\,{\cal F}}{\partial y}

        A test using Lie derivative from SageManifolds:

            sage: M = Manifold(2, 'M')
            sage: X.<x,y> = M.chart()
            sage: h = M.scalar_field(function('H', x, y), name='h')
            sage: dh = h.differential()
            sage: dh.display()
            dh = d(H)/dx dx + d(H)/dy dy
            sage: u = M.vector_field(name='u')
            sage: u[:] = [function('u_x', x,y), function('u_y', x,y)]
            sage: lu_dh = dh.lie_der(u)
            sage: latex(lu_dh.display())
            \left( u_{x}\left(x, y\right) \frac{\partial^2\,H}{\partial x^2} + u_{y}\left(x, y\right) \frac{\partial^2\,H}{\partial x\partial y} + \frac{\partial\,H}{\partial x} \frac{\partial\,u_{x}}{\partial x} + \frac{\partial\,H}{\partial y} \frac{\partial\,u_{y}}{\partial x} \right) \mathrm{d} x + \left( u_{x}\left(x, y\right) \frac{\partial^2\,H}{\partial x\partial y} + u_{y}\left(x, y\right) \frac{\partial^2\,H}{\partial y^2} + \frac{\partial\,H}{\partial x} \frac{\partial\,u_{x}}{\partial y} + \frac{\partial\,H}{\partial y} \frac{\partial\,u_{y}}{\partial y} \right) \mathrm{d} y

        """

        d = self._parent._latex_element_(self)

        import re
        # Fix for proper coercion of types:
        # http://www.sagemath.org/doc/faq/faq-usage.html#i-have-type-issues-using-scipy-cvxopt-or-numpy-from-sage
        Integer = int

        # find all occurences of diff
        list_d = []
        list_derivarives(self, list_d)

        for m in list_d:
    
            if str(m[1])==str(m[2]):  
                funcname = str(m[1])
            else: 
                funcname = str(m[2])

            diffargs = m[3]
            numargs = len(diffargs)

            if numargs > 1:
                numargs = "^" + str(numargs)
            else:
                numargs = ""

            variables = m[4]

            # dictionary to group multiple occurences of differentiation: d/dxdx -> d/dx^2 etc.
            occ = dict((i, str(variables[i]) + "^" + str(diffargs.count(i)) if(diffargs.count(i)>1) else str(variables[i])) for i in diffargs)

            res = "\\frac{\partial" + numargs + "\," + funcname + "}{\partial " + "\partial ".join([re.sub("\(.*?\)", "", i) for i in occ.values()]) + "}"

            # representation of the operator
            s = self._parent._latex_element_(m[0])
    
            # if diff operator is raised to some power (m[4]), put brackets around
            if m[5]:
                res = "\left(" + res + "\\right)^{" + str(m[5]) + "}"
                o = s + "^{" + str(m[5]) + "}"
            else:
                o = s

            d = d.replace(o, res)
            
        # if omit_function_args(True): 
        from sage.geometry.manifolds.chart import FunctionChart        
        if FunctionChart.omit_fargs: 

            list_f = [] 
            list_functions(self, list_f)

            for m in list_f:
                d = d.replace(str(m[3]) + str(m[4]), str(m[3]))

        return d


def list_derivarives(ex, list_d, exponent=0):
    r"""
    Function to find the occurences of FDerivativeOperator in the expression;
    inspired by http://ask.sagemath.org/question/10256/how-can-extract-different-terms-from-a-symbolic-expression/?answer=26136#post-id-26136

    INPUT:

    - ``ex`` -- symbolic expression to be analyzed
    - ``exponent`` -- (optional) exponent of FDerivativeOperator, passed to a next level in the expression tree

    OUTPUT:

    - ``list_d`` -- tuple containing the details of FDerivativeOperator found, in a following order:

    1. operator
    2. function name 
    3. LaTeX function name 
    4. parameter set
    5. operands
    6. exponent (if found, else 0)

    TESTS::

        sage: f = function('f_x', x, latex_name=r"{\cal F}")
        sage: df = f.diff(x)^2
        sage: from sage.geometry.manifolds.utilities import list_derivarives
        sage: list_d = []
        sage: list_derivarives(df, list_d)
        sage: list_d
        [(D[0](f_x)(x), 'f_x', {\cal F}, [0], [x], 2)]

    """

    op = ex.operator()
    operands = ex.operands()

    import operator 
    from sage.misc.latex import latex, latex_variable_name 
    from sage.symbolic.operators import FDerivativeOperator

    if op:

        if op is operator.pow:
            if isinstance(operands[0].operator(), FDerivativeOperator):
                exponent = operands[1]

        if isinstance(op, FDerivativeOperator):

            parameter_set = op.parameter_set()
            function = repr(op.function())
            latex_function = latex(op.function()) 

            # case when no latex_name given 
            if function == latex_function: 
                latex_function = latex_variable_name(str(op.function()))

            list_d.append((ex, function, latex_function, parameter_set, operands, exponent))

        for operand in operands:
            list_derivarives(operand, list_d, exponent)


def list_functions(ex, list_f):
    r"""
    Function to find the occurences of symbolic functions in the expression. 

    INPUT:

    - ``ex`` -- symbolic expression to be analyzed

    OUTPUT:

    - ``list_f`` -- tuple containing the details of a symbolic function found, in a following order:

    1. operator
    2. function name 
    3. arguments 
    4. LaTeX version of function name 
    5. LaTeX version of arguments  

    TESTS::

        sage: var('x y z')
        (x, y, z)
        sage: f = function('f', x, y, latex_name=r"{\cal F}")
        sage: g = function('g_x', x, y)
        sage: d = sin(x)*g.diff(x)*x*f - x^2*f.diff(x,y)/g 
        sage: from sage.geometry.manifolds.utilities import list_functions
        sage: list_f = [] 
        sage: list_functions(d, list_f)
        sage: list_f
        [(f, 'f', '(x, y)', {\cal F}, \left(x, y\right)), (g_x, 'g_x', '(x, y)', 'g_{x}', \left(x, y\right))]
   
   """
 
    op = ex.operator()
    operands = ex.operands()

    from sage.misc.latex import latex, latex_variable_name  

    if op: 

        if str(type(op)) == "<class 'sage.symbolic.function_factory.NewSymbolicFunction'>": 
            repr_function = repr(op) 
            latex_function = latex(op)

            # case when no latex_name given 
            if repr_function == latex_function:
                latex_function = latex_variable_name(str(op))

            repr_args = repr(ex.arguments())
            # remove comma in case of singleton 
            if len(ex.arguments())==1: 
                repr_args = repr_args.replace(",","")

            latex_args = latex(ex.arguments())
           
            list_f.append((op, repr_function, repr_args, latex_function, latex_args))
            
        for operand in operands:    
            list_functions(operand, list_f)


def nice_derivatives(status):
    r"""
    Set the display mode of partial derivatives.

    INPUT:

    - ``status`` -- boolean specifying the type of display:

      - ``True``: nice (textbook) display
      - ``False``: standard Pynac notation

    EXAMPLES::

        sage: M = Manifold(2, 'M')
        sage: X.<x,y> = M.chart()
        sage: f = M.scalar_field(function('F', x, y), name='f')
        sage: f.display()
        f: M --> R
           (x, y) |--> F(x, y)
        sage: df = f.differential()
        sage: df.display()  # the default is the nice display
        df = d(F)/dx dx + d(F)/dy dy
        sage: latex(df.display())
        \mathrm{d}f = \frac{\partial\,F}{\partial x} \mathrm{d} x + \frac{\partial\,F}{\partial y} \mathrm{d} y

    Standard Pynac display of partial derivatives::

        sage: nice_derivatives(False)
        sage: df.display()
        df = D[0](F)(x, y) dx + D[1](F)(x, y) dy
        sage: latex(df.display())
        \mathrm{d}f = D[0]\left(F\right)\left(x, y\right) \mathrm{d} x + D[1]\left(F\right)\left(x, y\right) \mathrm{d} y

    Let us revert to nice display::

        sage: nice_derivatives(True)
        sage: df.display()
        df = d(F)/dx dx + d(F)/dy dy
        sage: latex(df.display())
        \mathrm{d}f = \frac{\partial\,F}{\partial x} \mathrm{d} x + \frac{\partial\,F}{\partial y} \mathrm{d} y

    """
    from sage.geometry.manifolds.chart import FunctionChart
    if not isinstance(status, bool):
        raise TypeError("the argument must be a boolean")
    FunctionChart.nice_output = status


def omit_function_args(status):
    r"""
    Set the display mode of expression to omit arguments of symbolic functions.

    INPUT:

    - ``status`` -- boolean specifying the type of display:

        - ``True``: arguments are not printed 
        - ``False``: standard Pynac notation 

    TESTS:: 

        sage: from sage.geometry.manifolds.utilities import ExpressionNice
        sage: f = function('f_x', x)
        sage: f = f*(1 + f^2)
        sage: ExpressionNice(f)
        (f_x(x)^2 + 1)*f_x(x)
        sage: omit_function_args(True)
        sage: ExpressionNice(f)
        (f_x^2 + 1)*f_x
        sage: omit_function_args(False)
        sage: latex(ExpressionNice(f))
        {\left(f_{x}\left(x\right)^{2} + 1\right)} f_{x}\left(x\right)
        sage: omit_function_args(True)
        sage: latex(ExpressionNice(f))
        {\left(f_{x}^{2} + 1\right)} f_{x}

    """
    from sage.geometry.manifolds.chart import FunctionChart
    if not isinstance(status, bool):
        raise TypeError("the argument must be a boolean")
    FunctionChart.omit_fargs = status

