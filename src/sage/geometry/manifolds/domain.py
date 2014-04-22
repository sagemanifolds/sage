r"""
Domains on a manifold

The class :class:`Domain` implements subsets on a differentiable manifold 
over `\RR`. 

The class :class:`Domain` inherits from the generic Sage class
:class:`~sage.structure.parent.Parent`  
and is declared to belong to the category of sets (Sage category 
:class:`~sage.categories.sets_cat.Sets`).
The corresponding Sage :class:`~sage.structure.element.Element`'s are 
implemented via the class :class:`~sage.geometry.manifolds.point.Point`. 

The subclass :class:`OpenDomain` is devoted to open subsets, with respect to
the manifold topology. 

AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2013, 2014): initial version

EXAMPLES:

Two domains on a manifold::

    sage: M = Manifold(2, 'M')
    sage: a = M.domain('A') ; a
    domain 'A' on the 2-dimensional manifold 'M'
    sage: b = M.domain('B') ; b
    domain 'B' on the 2-dimensional manifold 'M'
    sage: M.domains
    {'A': domain 'A' on the 2-dimensional manifold 'M',
     'B': domain 'B' on the 2-dimensional manifold 'M',
     'M': 2-dimensional manifold 'M'}

The intersection of the two domains::

    sage: c = a.intersection(b) ; c
    domain 'A_inter_B' on the 2-dimensional manifold 'M'

Their union::

    sage: d = a.union(b) ; d
    domain 'A_union_B' on the 2-dimensional manifold 'M'

State of various data members after the above operations::

    sage: M.domains
    {'A': domain 'A' on the 2-dimensional manifold 'M', 
     'A_inter_B': domain 'A_inter_B' on the 2-dimensional manifold 'M',
     'B': domain 'B' on the 2-dimensional manifold 'M', 
     'M': 2-dimensional manifold 'M', 
     'A_union_B': domain 'A_union_B' on the 2-dimensional manifold 'M'}
    sage: a.subdomains
    set([domain 'A_inter_B' on the 2-dimensional manifold 'M', 
         domain 'A' on the 2-dimensional manifold 'M'])
    sage: a.superdomains
    set([domain 'A_union_B' on the 2-dimensional manifold 'M', 
         2-dimensional manifold 'M', 
         domain 'A' on the 2-dimensional manifold 'M'])
    sage: c.superdomains
    set([domain 'A' on the 2-dimensional manifold 'M', 
         2-dimensional manifold 'M', 
         domain 'A_inter_B' on the 2-dimensional manifold 'M', 
         domain 'A_union_B' on the 2-dimensional manifold 'M', 
         domain 'B' on the 2-dimensional manifold 'M'])
    sage: c.subdomains
    set([domain 'A_inter_B' on the 2-dimensional manifold 'M'])
    sage: d.subdomains
    set([domain 'B' on the 2-dimensional manifold 'M', 
         domain 'A_union_B' on the 2-dimensional manifold 'M', 
         domain 'A_inter_B' on the 2-dimensional manifold 'M', 
         domain 'A' on the 2-dimensional manifold 'M'])
    sage: d.superdomains
    set([domain 'A_union_B' on the 2-dimensional manifold 'M', 
         2-dimensional manifold 'M'])

"""
#*****************************************************************************
#       Copyright (C) 2013, 2014 Eric Gourgoulhon <eric.gourgoulhon@obspm.fr>
#       Copyright (C) 2013, 2014 Michal Bejger <bejger@camk.edu.pl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.structure.parent import Parent
from sage.structure.unique_representation import UniqueRepresentation
from sage.categories.sets_cat import Sets
from point import Point

#class Domain(UniqueRepresentation, Parent):
class Domain(Parent):
    r"""
    Subset of a differentiable manifold over `\RR`.
    
    For an open subset, use the class :class:`OpenDomain` instead.
    
    INPUT:
    
    - ``manifold`` -- manifold on which the domain is defined
    - ``name`` -- name given to the domain
    - ``latex_name`` --  (default: None) LaTeX symbol to denote the domain; if
      none is provided, it is set to ``name``
    
    EXAMPLES:
    
    A domain on a manifold::
    
        sage: M = Manifold(2, 'M')
        sage: from sage.geometry.manifolds.domain import Domain
        sage: A = Domain(M, 'A', latex_name=r'\mathcal{A}') ; A
        domain 'A' on the 2-dimensional manifold 'M'
        sage: latex(A)
        \mathcal{A}
        sage: A.is_subdomain(M)
        True
    
    Instead of importing Domain in the global namespace, it is recommended to
    use the method :meth:`domain` to create a new domain::
        
        sage: B = M.domain('B', latex_name=r'\mathcal{B}') ; B
        domain 'B' on the 2-dimensional manifold 'M'
        sage: M.domains
        {'A': domain 'A' on the 2-dimensional manifold 'M',
         'B': domain 'B' on the 2-dimensional manifold 'M',
         'M': 2-dimensional manifold 'M'}

    The manifold is itself a domain::
    
        sage: isinstance(M, Domain)
        True
        
    Actually, it is an instance of the subclass 
    :class:`~sage.geometry.manifolds.domain.OpenDomain`, for it is 
    (by definition) open::
    
        sage: isinstance(M, sage.geometry.manifolds.domain.OpenDomain)
        True
    
    Instances of :class:`Domain` are Sage parents (in the category of sets), 
    the elements of which are points on the manifold 
    (class :class:`~sage.geometry.manifolds.point.Point`)::
    
        sage: isinstance(A, Parent)
        True
        sage: A.category()
        Category of sets
        sage: p = A.an_element() ; p
        point on 2-dimensional manifold 'M'
        sage: p.parent()
        domain 'A' on the 2-dimensional manifold 'M'
        sage: p in A
        True
        sage: p in M
        True


        
    """
    
    Element = Point
    
    def __init__(self, manifold, name, latex_name=None):
        Parent.__init__(self, category=Sets())
        self.manifold = manifold
        if self != manifold:
            if name not in manifold.domains:
                self.name = name
                manifold.domains[name] = self
                manifold.subdomains.add(self)
                # set of domains containing self:
                self.superdomains = set([manifold, self]) 
            else:
                raise ValueError("The name '" + name + "' is already used for "
                                 + "another domain on " + str(manifold))
        else: # case where the domain is the full manifold
            self.name = name
            self.superdomains = set([self])
        if latex_name is None:
            self.latex_name = self.name
        else:
            self.latex_name = latex_name
        self.subdomains = set([self]) # domains contained in self
        self.intersections = {} # dict. of intersections with other domains
        self.unions = {} # dict. of unions with other domains
        self.atlas = []  # list of charts defined on subdomains of self
        self.def_chart = None  # default chart
        self.coord_changes = {} # dictionary of transition maps 
        self.frames = []  # list of vector frames defined on subdomains of self
        self.def_frame = None  # default frame
        self.frame_changes = {} # dictionary of changes of frames
        self.coframes = []  # list of coframes defined on subdomains of self

    #### Methods required for any Parent in the category of sets:
    def _element_constructor_(self, coords=None, chart=None, name=None, 
                 latex_name=None):
        r"""
        Construct a point on the domain from its coordinates in some chart. 
        """
        return self.element_class(self, coords, chart, name, latex_name)

    def _an_element_(self):
        r"""
        Construct some (unamed) point on the domain
        """
        from sage.rings.infinity import Infinity
        if self.def_chart is None:
            return self.element_class(self)
        chart = self.def_chart
        coords = []
        for coord_range in chart.bounds:
            xmin = coord_range[0][0]
            xmax = coord_range[1][0]
            if xmin == -Infinity:
                if xmax == Infinity:
                    x = 0
                else:
                    x = xmax - 1
            else:
                if xmax == Infinity:
                    x = xmin + 1
                else:
                    x = (xmin + xmax)/2
            coords.append(x)
        return self.element_class(self, coords, chart)
            
    #### End of methods required for any Parent in the category of sets

    def _repr_(self):
        r"""
        Special Sage function for the string representation of the object.
        """
        return "domain '" + self.name + "' on the " + str(self.manifold)

    def _latex_(self):
        r"""
        Special Sage function for the LaTeX representation of the object.
        """
        return self.latex_name

    def domain(self, name, latex_name=None, is_open=False):
        r"""
        Create a subdomain of the current domain. 

        A *subdomain* is a domain that is included in ``self``. 
        
        INPUT: 
        
        - ``name`` -- name given to the subdomain
        - ``latex_name`` --  (default: None) LaTeX symbol to denote the 
          subdomain; if none is provided, it is set to ``name``
        - ``is_open`` -- (default: False) if True, the created domain is
          assumed to be open with respect to the manifold's topology

        OUTPUT:
        
        - the subdomain, as an instance of :class:`Domain`, or of 
          :class:`OpenDomain` if ``is_open`` is True. 
        
        EXAMPLES:
        
        Creating a domain on a manifold::
        
            sage: M = Manifold(2, 'M')
            sage: a = M.domain('A') ; a                   
            domain 'A' on the 2-dimensional manifold 'M'

        Creating a subdomain of A::
        
            sage: b = a.domain('B', latex_name=r'\mathcal{B}') ; b
            domain 'B' on the 2-dimensional manifold 'M'
            sage: latex(b)
            \mathcal{B}

        B is then a subdomain of A and A is a superdomain of B::
        
            sage: a.subdomains
            set([domain 'B' on the 2-dimensional manifold 'M', 
                 domain 'A' on the 2-dimensional manifold 'M'])
            sage: b.superdomains
            set([domain 'B' on the 2-dimensional manifold 'M', 
                 2-dimensional manifold 'M', 
                 domain 'A' on the 2-dimensional manifold 'M'])

        Creating an open subdomain of A::
        
            sage: c = a.domain('C', is_open=True) ; c
            open domain 'C' on the 2-dimensional manifold 'M'
            
        """
        if is_open:
            res = OpenDomain(self.manifold, name, latex_name)
        else:
            res = Domain(self.manifold, name, latex_name)
        res.superdomains.update(self.superdomains)
        for sd in self.superdomains:
            sd.subdomains.add(res)
        return res
            
    def superdomain(self, name, latex_name=None, is_open=False):
        r"""
        Create a superdomain of the current domain. 
        
        A *superdomain* is a domain in which ``self`` is included. 
        
        INPUT: 
        
        - ``name`` -- name given to the superdomain
        - ``latex_name`` --  (default: None) LaTeX symbol to denote the 
          superdomain; if none is provided, it is set to ``name``
        - ``is_open`` -- (default: False) if True, the created domain is
          assumed to be open with respect to the manifold's topology

        OUTPUT:
        
        - the superdomain, as an instance of :class:`Domain` or of 
          :class:`OpenDomain` if ``is_open==True``. 
     
        EXAMPLES:
        
        Creating some superdomain of a given domain::
        
            sage: M = Manifold(2, 'M')
            sage: a = M.domain('A')
            sage: b = a.superdomain('B') ; b
            domain 'B' on the 2-dimensional manifold 'M'
            sage: b.subdomains
            set([domain 'B' on the 2-dimensional manifold 'M', 
                 domain 'A' on the 2-dimensional manifold 'M'])
            sage: a.superdomains
            set([domain 'B' on the 2-dimensional manifold 'M', 
                 2-dimensional manifold 'M', 
                 domain 'A' on the 2-dimensional manifold 'M'])
            
        The superdomain of the manifold is itself::
        
            sage: M.superdomain('SM') is M
            True
            
        Two superdomains of a given domain are a priori different::
        
            sage: c = a.superdomain('C') 
            sage: c == b
            False

        """
        if self is self.manifold:
            return self
        if is_open:
            res = OpenDomain(self.manifold, name, latex_name)
        else:
            res = Domain(self.manifold, name, latex_name)
        res.subdomains.update(self.subdomains)
        for sd in self.subdomains:
            sd.superdomains.add(res)
        res.atlas = list(self.atlas)
        res.coord_changes = dict(self.coord_changes)
        res.frames = list(self.frames)
        res.frame_changes = dict(self.frame_changes)
        res.coframes = list(self.coframes)
        res.def_chart = self.def_chart
        res.def_frame = self.def_frame
        return res
            

    def intersection(self, other, name=None, latex_name=None):
        r"""
        Return the intersection of ``self`` with another domain. 
            
        INPUT: 
        
        - ``other`` -- another domain on the same manifold
        - ``name`` -- (default: None) name given to the intersection in the
          case the latter has to be created; the default is 
          ``self.name`` inter ``other.name``
        - ``latex_name`` --  (default: None) LaTeX symbol to denote the 
          intersection in the case the latter has to be created; the default
          is built upon the symbol `\cap`

        OUTPUT:
        
        - instance of :class:`Domain` (or :class:`OpenDomain` if both domains
          are open) representing the domain that is the intersection of 
          ``self`` with ``other``

        EXAMPLES: 
        
        Intersection of two domains::
        
            sage: M = Manifold(2, 'M')
            sage: a = M.domain('A')
            sage: b = M.domain('B')
            sage: c = a.intersection(b) ; c
            domain 'A_inter_B' on the 2-dimensional manifold 'M'
            sage: a.subdomains
            set([domain 'A_inter_B' on the 2-dimensional manifold 'M', 
                 domain 'A' on the 2-dimensional manifold 'M'])
            sage: b.subdomains
            set([domain 'B' on the 2-dimensional manifold 'M', 
                 domain 'A_inter_B' on the 2-dimensional manifold 'M'])
            sage: c.superdomains
            set([domain 'A' on the 2-dimensional manifold 'M', 
                 2-dimensional manifold 'M', 
                 domain 'A_inter_B' on the 2-dimensional manifold 'M', 
                 domain 'B' on the 2-dimensional manifold 'M'])
        
        Some checks::
            
            sage: (a.intersection(b)).is_subdomain(a)
            True
            sage: (a.intersection(b)).is_subdomain(a)
            True
            sage: a.intersection(b) is b.intersection(a) 
            True
            sage: a.intersection(a.intersection(b)) is a.intersection(b)
            True
            sage: (a.intersection(b)).intersection(a) is a.intersection(b)
            True
            sage: M.intersection(a) is a
            True
            sage: a.intersection(M) is a
            True
            
        """
        if other.manifold != self.manifold:
            raise TypeError(
                "The two domains do not belong to the same manifold.")
        # Particular cases:
        if self is self.manifold:
            return other
        if other is self.manifold:
            return self
        if self in other.subdomains:
            return self
        if other in self.subdomains:
            return other
        # Generic case:
        if other.name in self.intersections:
            # the intersection has already been created:
            return self.intersections[other.name]
        else:
            # the intersection must be created:
            if latex_name is None:
                if name is None:
                    latex_name = self.latex_name + r'\cap ' + other.latex_name
                else:
                    latex_name = name
            if name is None:
                name = self.name + "_inter_" + other.name
            if isinstance(self, OpenDomain) and isinstance(other, OpenDomain):
                res = self.open_domain(name, latex_name)
            else:
                res = self.domain(name, latex_name)
            res.superdomains.update(other.superdomains)
            for sd in other.superdomains:
                sd.subdomains.add(res)
            self.intersections[other.name] = res
            other.intersections[self.name] = res
            return res
        
    def union(self, other, name=None, latex_name=None):
        r"""
        Return the union of ``self`` with another domain. 
            
        INPUT: 
        
        - ``other`` -- another domain on the same manifold
        - ``name`` -- (default: None) name given to the union in the
          case the latter has to be created; the default is 
          ``self.name`` union ``other.name``
        - ``latex_name`` --  (default: None) LaTeX symbol to denote the 
          union in the case the latter has to be created; the default
          is built upon the symbol `\cup`

        OUTPUT:
        
        - instance of :class:`Domain` (or :class:`OpenDomain` if both domains 
          are open) representing the domain that is the the union of ``self`` 
          with ``other``

        EXAMPLES:
        
        Union of two domains::
        
            sage: M = Manifold(2, 'M')
            sage: a = M.domain('A')
            sage: b = M.domain('B')
            sage: c = a.union(b) ; c 
            domain 'A_union_B' on the 2-dimensional manifold 'M'
            sage: a.superdomains
            set([domain 'A_union_B' on the 2-dimensional manifold 'M', 
                 2-dimensional manifold 'M', 
                 domain 'A' on the 2-dimensional manifold 'M'])
            sage: b.superdomains
            set([domain 'B' on the 2-dimensional manifold 'M', 
                 2-dimensional manifold 'M', 
                 domain 'A_union_B' on the 2-dimensional manifold 'M'])
            sage: c.subdomains
            set([domain 'A_union_B' on the 2-dimensional manifold 'M', 
                domain 'A' on the 2-dimensional manifold 'M', 
                domain 'B' on the 2-dimensional manifold 'M'])
        
        Some checks::
        
            sage: a.is_subdomain(a.union(b))
            True
            sage: b.is_subdomain(a.union(b))
            True
            sage: a.union(b) is b.union(a) 
            True
            sage: a.union(a.union(b)) is a.union(b)
            True
            sage: (a.union(b)).union(a) is a.union(b)
            True
            sage: a.union(M) is M
            True
            sage: M.union(a) is M
            True
            
        """
        if other.manifold != self.manifold:
            raise TypeError(
                "The two domains do not belong to the same manifold.")
        # Particular cases:
        if (self is self.manifold) or (other is self.manifold):
            return self.manifold
        if self in other.subdomains:
            return other
        if other in self.subdomains:
            return self
        # Generic case:
        if other.name in self.unions:
            # the union has already been created:
            return self.unions[other.name]
        else:
            # the union must be created:
            if latex_name is None:
                if name is None:
                    latex_name = self.latex_name + r'\cup ' + other.latex_name
                else:
                    latex_name = name
            if name is None:
                name = self.name + "_union_" + other.name
            res_open = isinstance(self, OpenDomain) and \
                       isinstance(other, OpenDomain)
            res = self.superdomain(name, latex_name, is_open=res_open)
            res.subdomains.update(other.subdomains)
            for sd in other.subdomains:
                sd.superdomains.add(res)
            for chart in other.atlas:
                if chart not in res.atlas:
                    res.atlas.append(chart)
            res.coord_changes.update(other.coord_changes)
            for frame in other.frames:
                if frame not in res.frames:
                    res.frames.append(frame)
            res.frame_changes.update(other.frame_changes)
            for coframe in other.coframes:
                if coframe not in res.coframes:
                    res.coframes.append(coframe)
            self.unions[other.name] = res
            other.unions[self.name] = res
            return res
        
    def is_subdomain(self, other):
        r"""
        Return ``True`` iff ``self`` is included in ``other``. 
        
        EXAMPLES:
        
        Subdomains on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M')
            sage: a = M.domain('A')
            sage: b = a.domain('B')
            sage: c = M.domain('C')
            sage: a.is_subdomain(M)
            True
            sage: b.is_subdomain(a)
            True
            sage: b.is_subdomain(M) 
            True
            sage: a.is_subdomain(b)
            False
            sage: c.is_subdomain(a)
            False
        
        """
        return self in other.subdomains
        
    def __contains__(self, point):
        r"""
        Check whether a point is contained in the domain. 
        """
        if point.parent().is_subdomain(self):
            return True
        for chart in self.atlas:
            if chart in point.coordinates:
                if chart.valid_coordinates( *(point.coordinates[chart]) ):
                    return True
        for chart in point.coordinates:
            for schart in chart.subcharts:
                if schart in self.atlas and schart.valid_coordinates( 
                                          *(point.coordinates[chart]) ):
                    return True
        return False

    def point(self, coords=None, chart=None, name=None, latex_name=None):
        r"""
        Define a point in the domain. 
        
        See :class:`~sage.geometry.manifolds.point.Point` for a complete 
        documentation. 

        INPUT:
        
        - ``coords`` -- the point coordinates (as a tuple or a list) in the 
          chart specified by ``chart``
        - ``chart`` -- (default: None) chart in which the point coordinates are
          given; if none is provided, the coordinates are assumed to refer to 
          the domain's default chart
        - ``name`` -- (default: None) name given to the point
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the point; 
          if none is provided, the LaTeX symbol is set to ``name``
          
        OUTPUT:
        
        - the declared point, as an instance of 
          :class:`~sage.geometry.manifolds.point.Point`. 
        
        EXAMPLES:
        
        Points on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M')
            sage: c_xy = M.chart('x y')
            sage: p = M.point((1,2), name='p') ; p
            point 'p' on 2-dimensional manifold 'M'
            sage: p in M
            True
            sage: a = M.open_domain('A')
            sage: c_uv = a.chart('u v')
            sage: q = a.point((-1,0), name='q') ; q
            point 'q' on 2-dimensional manifold 'M'
            sage: q in a   
            True
            sage: p.coordinates
            {chart (M, (x, y)): (1, 2)}
            sage: q.coordinates
            {chart (A, (u, v)): (-1, 0)}

        """
        return self.element_class(self, coords, chart, name, latex_name)
        
    def default_chart(self):
        r"""
        Return the default chart defined on the domain. 
        
        Unless changed via :meth:`set_default_chart`, the *default chart* 
        is the first one defined on a subdomain of the current domain 
        (possibly itself). 
        
        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.chart.Chart` 
          representing the default chart.
        
        EXAMPLES:
                    
        Default chart on a 2-dimensional manifold and on some subdomains::
            
            sage: M = Manifold(2, 'M')
            sage: M.chart('x y')
            chart (M, (x, y))
            sage: M.chart('u v')
            chart (M, (u, v))
            sage: M.default_chart()
            chart (M, (x, y))
            sage: a = M.domain('A')     
            sage: b = a.domain('B', is_open=True)    
            sage: b.chart('t z')
            chart (B, (t, z))
            sage: a.default_chart()
            chart (B, (t, z))
            sage: b.default_chart()
            chart (B, (t, z))

        """
        return self.def_chart
        
    def set_default_chart(self, chart):
        r"""
        Changing the default chart on the current domain.
        
        INPUT:
    
        - ``chart`` -- a chart (must be defined on some subdomain of the
          current domain)

        EXAMPLES:
                    
        Charts on a 2-dimensional manifold::
            
            sage: M = Manifold(2, 'M')
            sage: c_xy = M.chart('x y')
            sage: c_uv = M.chart('u v')
            sage: M.default_chart()
            chart (M, (x, y))
            sage: M.set_default_chart(c_uv)
            sage: M.default_chart()
            chart (M, (u, v))

        """
        from chart import Chart
        if not isinstance(chart, Chart):
            raise TypeError(str(chart) + " is not a chart.")
        if chart not in self.atlas:
            raise ValueError("The chart must be defined on the " + 
                             str(self))
        self.def_chart = chart

    def coord_change(self, chart1, chart2):
        r"""
        Return a change of coordinates (transition map) defined on some
        subdomain of the current domain.
        
        INPUT:
        
        - ``chart1`` -- chart 1
        - ``chart2`` -- chart 2
        
        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.chart.CoordChange` 
          representing the transition map from chart 1 to chart 2 
        
        EXAMPLES:
        
        Change of coordinates on a 2-dimensional manifold::
            
            sage: M = Manifold(2, 'M')
            sage: c_xy.<x,y> = M.chart('x y')
            sage: c_uv.<u,v> = M.chart('u v')
            sage: c_xy.transition_map(c_uv, (x+y, x-y)) # defines the coordinate change
            coordinate change from chart (M, (x, y)) to chart (M, (u, v))
            sage: M.coord_change(c_xy, c_uv) # returns the coordinate change defined above
            coordinate change from chart (M, (x, y)) to chart (M, (u, v))

        """
        if (chart1, chart2) not in self.coord_changes:
            raise TypeError("The change of coordinates from " + str(chart1) + 
                            " to " + str(chart2) + " has not been " + 
                            "defined on the " + str(self))
        return self.coord_changes[(chart1, chart2)]


    def default_frame(self):
        r"""
        Return the default vector frame defined on the domain. 
        
        By 'vector frame' it is meant a field on the domain that provides, 
        at each point p, a vector basis of the tangent space at p.

        Unless changed via :meth:`set_default_frame`, the default frame is the 
        first one defined on the domain, usually implicitely as the coordinate
        basis associated with the first chart defined on the domain. 
        
        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.vectorframe.VectorFrame`
          representing the default vector frame.
        
        EXAMPLES:
                    
        The default vector frame is often the coordinate frame associated
        with the first chart defined on the domain::
            
            sage: M = Manifold(2, 'M')
            sage: c_xy = M.chart('x y')
            sage: M.default_frame()
            coordinate frame (M, (d/dx,d/dy))

        """
        return self.def_frame

    def set_default_frame(self, frame):
        r"""
        Changing the default vector frame on the domain.
        
        INPUT:
    
        - ``frame`` -- a vector frame (instance of 
          :class:`~sage.geometry.manifolds.vectorframe.VectorFrame`) defined 
          on the current domain
          
        EXAMPLE::
        
            sage: M = Manifold(2, 'M')
            sage: c_xy = M.chart('x y')
            sage: e = M.vector_frame('e')
            sage: M.default_frame()
            coordinate frame (M, (d/dx,d/dy))                 
            sage: M.set_default_frame(e)
            sage: M.default_frame()
            vector frame (M, (e_0,e_1))  

        """
        from vectorframe import VectorFrame
        if not isinstance(frame, VectorFrame):
            raise TypeError(str(frame) + " is not a vector frame.")
        if not frame.domain.is_subdomain(self):
            raise TypeError("The frame must be defined on the domain.")
        self.def_frame = frame
        frame.fmodule.set_default_basis(frame)

    def frame_change(self, frame1, frame2):
        r"""
        Return a change of vector frames defined on the domain.
                
        INPUT:
        
        - ``frame1`` -- vector frame 1
        - ``frame2`` -- vector frame 2
        
        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.rank2field.AutomorphismField` 
          representing, at each point, the vector space automorphism `P` 
          that relates frame 1, `(e_i)` say, to frame 2, `(n_i)` say, 
          according to `n_i = P(e_i)`
        
        EXAMPLES:
        
        Change of vector frames induced by a change of coordinates::
        
            sage: M = Manifold(2, 'M')
            sage: c_xy.<x,y> = M.chart('x y')
            sage: c_uv.<u,v> = M.chart('u v')
            sage: c_xy.transition_map(c_uv, (x+y, x-y))
            coordinate change from chart (M, (x, y)) to chart (M, (u, v))
            sage: M.frame_change(c_xy.frame, c_uv.frame)
            field of tangent-space automorphisms on the 2-dimensional manifold 'M'
            sage: M.frame_change(c_xy.frame, c_uv.frame)[:]
            [ 1/2  1/2]
            [ 1/2 -1/2]
            sage: M.frame_change(c_uv.frame, c_xy.frame)
            field of tangent-space automorphisms on the 2-dimensional manifold 'M'
            sage: M.frame_change(c_uv.frame, c_xy.frame)[:]
            [ 1  1]
            [ 1 -1]
            sage: M.frame_change(c_uv.frame, c_xy.frame) ==  M.frame_change(c_xy.frame, c_uv.frame).inverse()
            True            

        """
        if (frame1, frame2) not in self.frame_changes:
            raise TypeError("The change of frame from '" + repr(frame1) + 
                            "' to '" + repr(frame2) + "' has not been " + 
                            "defined on the " + repr(self))
        return self.frame_changes[(frame1, frame2)]
    
    def is_manifestly_coordinate_domain(self):
        r"""
        Returns True if self is known to be the domain of some coordinate 
        chart and False otherwise. 
        
        If False is returned, either self cannot be the domain of some 
        coordinate chart or no such chart has been declared yet. 
        """
        if not isinstance(self, OpenDomain):
            return False
        return not self.covering_charts == [] 

    def is_manifestly_parallelizable(self):
        r"""
        Returns True if self is known to be a parallelizable domain and False
        otherwise.
        
        If False is returned, either self is not parallelizable or no vector
        frame has been defined on self yet.
        """
        if not isinstance(self, OpenDomain):
            return False
        return not self.covering_frames == [] 

#******************************************************************************

class OpenDomain(Domain):
    r"""
    This class is devoted to open subsets of a differentiable manifold 
    over `\RR`.
    
    The class :class:`OpenDomain` inherits from the class :class:`Domain`.
    Via the latter, it inherits also from the generic Sage class 
    :class:`~sage.structure.parent.Parent`  and is declared to belong to the 
    category of sets (Sage category :class:`~sage.categories.sets_cat.Sets`).
    The corresponding Sage :class:`~sage.structure.element.Element`'s are 
    implemented via the class :class:`~sage.geometry.manifolds.point.Point`. 
    
    INPUT:
    
    - ``manifold`` -- manifold on which the open domain is defined
    - ``name`` -- name given to the open domain
    - ``latex_name`` --  (default: None) LaTeX symbol to denote the open 
      domain; if none is provided, it is set to ``name``
    
    EXAMPLES:
    
    A open domain on a manifold::
    
        sage: M = Manifold(2, 'M')
        sage: from sage.geometry.manifolds.domain import OpenDomain
        sage: A = OpenDomain(M, 'A', latex_name=r'\mathcal{A}') ; A
        open domain 'A' on the 2-dimensional manifold 'M'
        sage: latex(A)
        \mathcal{A}
        
    Instead of importing OpenDomain in the global namespace, it is recommended
    to use the method :meth:`open_domain` to create a new open domain::
        
        sage: B = M.open_domain('B', latex_name=r'\mathcal{B}') ; B
        open domain 'B' on the 2-dimensional manifold 'M'
        sage: M.domains
        {'A': open domain 'A' on the 2-dimensional manifold 'M',
         'B': open domain 'B' on the 2-dimensional manifold 'M',
         'M': 2-dimensional manifold 'M'}
         
    The manifold is itself an open domain (by definition!)::
    
        sage: isinstance(M, OpenDomain)
        True
    
    Open domains are Sage :class:`~sage.structure.parent.Parent`, the 
    :class:`~sage.structure.element.Element` of which are the manifold points 
    (class :class:`~sage.geometry.manifolds.point.Point`)::
    
        sage: p = A.an_element() ; p
        point on 2-dimensional manifold 'M'
        sage: p.parent()
        open domain 'A' on the 2-dimensional manifold 'M'
        sage: A.category()
        Category of sets

    Consequently, points can be created by providing their coordinates in some
    chart via the operator () applied to the domain::

        sage: chart1 = A.chart('x y')
        sage: p = A((-2,3)) ; p   
        point on 2-dimensional manifold 'M'
        sage: p.coord()
        (-2, 3)
        
    Other arguments can be specified::
    
        sage: p = A((-2,3), chart=chart1, name='p') ; p
        point 'p' on 2-dimensional manifold 'M'

    It is equivalent to use the method :meth:`point`::
    
        sage: A((-2,3)) == A.point((-2,3))
        True

    """
    def __init__(self, manifold, name, latex_name=None):
        from scalarfield import ZeroScalarField
        Domain.__init__(self, manifold, name, latex_name)
        # list of charts that individually cover the domain, i.e. whose 
        # domains are self (if non-empty, self is coordinate domain):
        self.covering_charts = [] 
        # list of vector frames that individually cover the domain, i.e. whose 
        # domains are self (if non-empty, self is parallelizable):
        self.covering_frames = [] 
        # ring of scalar fields defined on self (not contructed yet) 
        self._scalar_field_ring = None 
        # The zero scalar field is constructed:
        if self.name != 'field R':  
            #!# to avoid circular import of RealLine
            self.zero_scalar_field = ZeroScalarField(self)
        # dict. of vector field modules along self:
        self._vector_field_modules = {}
        # dict. of tensor field modules along self: 
        self._tensor_field_modules = {}
    
    def _repr_(self):
        r"""
        Special Sage function for the string representation of the object.
        """
        return "open domain '" + self.name + "' on the " + str(self.manifold)

    def open_domain(self, name, latex_name=None):
        r"""
        Create an open subdomain of the current domain. 

        An open subdomain is a set that is (i) included in ``self`` and (ii)
        open with respect to the manifold's topology.
        
        INPUT: 
        
        - ``name`` -- name given to the open subdomain
        - ``latex_name`` --  (default: None) LaTeX symbol to denote the 
          subdomain; if none is provided, it is set to ``name``

        OUTPUT:
        
        - the open subdomain, as an instance of :class:`OpenDomain`.
        
        EXAMPLES:
        
        Creating an open domain on a manifold::
        
            sage: M = Manifold(2, 'M')
            sage: a = M.open_domain('A') ; a                   
            open domain 'A' on the 2-dimensional manifold 'M'

        Creating an open subdomain of A::
        
            sage: b = a.open_domain('B') ; b
            open domain 'B' on the 2-dimensional manifold 'M'

        B is then a subdomain of A and A is a superdomain of B::
        
            sage: a.subdomains
            set([open domain 'A' on the 2-dimensional manifold 'M', 
                 open domain 'B' on the 2-dimensional manifold 'M'])
            sage: b.superdomains
            set([open domain 'A' on the 2-dimensional manifold 'M', 
                 2-dimensional manifold 'M', 
                 open domain 'B' on the 2-dimensional manifold 'M'])

        """
        return self.domain(name, latex_name=latex_name, is_open=True)

    def chart(self, coordinates, names=None):
        r"""
        Define a chart on the open domain. 
        
        A *chart* is a pair `(U,\varphi)`, where `U` is the open domain 
        represented by ``self`` and `\varphi: U \rightarrow V \subset \RR^n` 
        is a homeomorphism from `U` to an open domain `V` of `\RR^n`. 
        
        The components `(x^1,\ldots,x^n)` of `\varphi`, defined by 
        `\varphi(p) = (x^1(p),\ldots,x^n(p))`, are called the *coordinates* 
        of the chart `(U,\varphi)`.

        See :class:`~sage.geometry.manifolds.chart.Chart` for a complete 
        documentation.  
    
        INPUT:
        
        - ``coordinates`` -- single string defining the coordinate symbols and 
          ranges: the coordinates are separated by ' ' (space) and each 
          coordinate has at most three fields, separated by ':': 
            
            1. The coordinate symbol (a letter or a few letters)
            2. (optional) The interval `I` defining the coordinate range: if not
               provided, the coordinate is assumed to span all `\RR`; otherwise 
               `I` must be provided in the form (a,b) (or equivalently ]a,b[)
               The bounds a and b can be +/-Infinity, Inf, infinity, inf or oo.
               For *singular* coordinates, non-open intervals such as [a,b] and 
               (a,b] (or equivalently ]a,b]) are allowed. 
               Note that the interval declaration must not contain any space 
               character.
            3. (optional) The LaTeX spelling of the coordinate; if not provided the
               coordinate symbol given in the first field will be used.
          
          The order of the fields 2 and 3 does not matter and each of them can 
          be omitted.
          If it contains any LaTeX expression, the string ``coordinates`` must 
          be declared with the prefix 'r' (for "raw") to allow for a proper 
          treatment of the backslash character (see examples below). 
        - ``names`` -- (default: None) unused argument (present only to enable
          the use of the shortcut operator <,>). 
        
        OUTPUT:
        
        - the created chart, as an instance of 
          :class:`~sage.geometry.manifolds.chart.Chart`.
        
        EXAMPLES: 
        
        Chart on a 2-dimensional manifold::
        
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U')
            sage: X = U.chart('x y') ; X
            chart (U, (x, y))
            sage: X[0]
            x
            sage: X[1]
            y
            sage: X[:]
            (x, y)

        The declared coordinates are not known at the global level::
        
            sage: y
            Traceback (most recent call last):
            ...
            NameError: name 'y' is not defined
        
        They can be recovered by the Chart method [:]::
        
            sage: (x, y) = X[:]
            sage: y
            y
            sage: type(y)
            <type 'sage.symbolic.expression.Expression'>

        But a shorter way to proceed is to use the operator <,> in the chart
        declaration::
        
            sage: M = Manifold(2, 'M')
            sage: U = M.open_domain('U')
            sage: X.<x,y> = U.chart('x y') ; X
            chart (U, (x, y))
            
        Indeed, the declared coordinates are then known at the global level::
        
            sage: y
            y
            sage: (x,y) == X[:]
            True
    
        Actually the instruction ``X.<x,y> = U.chart('x y')`` is
        equivalent to the two instructions ``X = U.chart('x y')`` 
        and ``(x,y) = X[:]``. 
            
        See the documentation of class 
        :class:`~sage.geometry.manifolds.chart.Chart` for more examples, 
        especially regarding the coordinates ranges and restrictions. 
        
        """
        from chart import Chart
        return Chart(self, coordinates)

    def scalar_field_ring(self):
        r"""
        Returns the ring of scalar fields defined on ``self``.
        
        See :class:`~sage.geometry.manifolds.scalarfield_ring.ScalarFieldRing` 
        for a complete documentation.  
        
        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.scalarfield_ring.ScalarFieldRing`
          representing the algebra `C^\infty(U)` of all scalar fields defined
          on `U` = ``self``.
          
        EXAMPLE:
        
        Scalar ring of a 3-dimensional open domain::
        
            sage: M = Manifold(3, 'M')
            sage: U = M.open_domain('U')
            sage: CU = U.scalar_field_ring() ; CU
            ring of scalar fields on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: CU.category()
            Category of commutative rings
            sage: CU.zero()
            zero scalar field on the open domain 'U' on the 3-dimensional manifold 'M'
          
        """
        from scalarfield_ring import ScalarFieldRing
        if self._scalar_field_ring is None:
            self._scalar_field_ring = ScalarFieldRing(self)
        return self._scalar_field_ring

    def vector_field_module(self, dest_map=None):
        r"""
        Returns the set of vector fields defined on ``self``, possibly 
        within some ambient manifold, as a module over the ring of scalar
        fields defined on ``self``.

        See :class:`~sage.geometry.manifolds.vectorfield_module.VectorFieldModule` 
        for a complete documentation.  
        
        INPUT:
        
        - ``dest_map`` -- (default: None) destination map 
          `\Phi:\ U \rightarrow V`, where `U` is ``self`` 
          (type: :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`); 
          if none is provided, the identity is assumed (case of vector fields 
          *on* `U`)
        
        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.vectorfield_module.VectorFieldModule`
          representing the module `\mathcal{X}(U,\Phi)` of vector fields on the 
          open domain `U`=``self`` taking values on 
          `\Phi(U)\subset V\subset M`. 
        
        EXAMPLES:
        
        Vector field module `\mathcal{X}(U)` of the complement `U` of the two 
        poles on the sphere `\mathbb{S}^2`::
        
            sage: S2 = Manifold(2, 'S^2')
            sage: U = S2.open_domain('U')  # the complement of the two poles
            sage: spher_coord.<th,ph> = U.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi') # spherical coordinates
            sage: XU = U.vector_field_module() ; XU
            free module X(U) of vector fields on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: XU.category()
            Category of modules over ring of scalar fields on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: XU.base_ring()
            ring of scalar fields on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: XU.base_ring() is U.scalar_field_ring()
            True

        `\mathcal{X}(U)` is a free module because `U` is parallelizable (being
        a chart domain)::
        
            sage: U.is_manifestly_parallelizable()
            True
            
        Its rank is the manifold's dimension::
        
            sage: XU.rank()
            2

        The elements of `\mathcal{X}(U)` are vector fields on `U`::
        
            sage: XU.an_element()
            vector field on the open domain 'U' on the 2-dimensional manifold 'S^2'
            sage: XU.an_element().view()
            2 d/dth + 2 d/dph

        Vector field module `\mathcal{X}(U,\Phi)` of the 
        `\mathbb{R}^3`-valued vector fields along `U`, associated with the 
        embedding `\Phi` of `\mathbb{S}^2` into `\mathbb{R}^3`::
        
            sage: R3 = Manifold(3, 'R^3')
            sage: cart_coord.<x, y, z> = R3.chart('x y z')
            sage: Phi = U.diff_mapping(R3, [sin(th)*cos(ph), sin(th)*sin(ph), cos(th)], name='Phi')
            sage: XU_R3 = U.vector_field_module(dest_map=Phi) ; XU_R3
            free module X(U,Phi) of vector fields along the open domain 'U' on the 2-dimensional manifold 'S^2' mapped into the 3-dimensional manifold 'R^3'
            sage: XU_R3.base_ring()
            ring of scalar fields on the open domain 'U' on the 2-dimensional manifold 'S^2'
            
        `\mathcal{X}(U,\mathbb{R}^3)` is a free module because `\mathbb{R}^3`
        is parallelizable and its rank is 3::
        
            sage: XU_R3.rank()
            3

        """
        from vectorfield_module import VectorFieldFreeModule
        if dest_map is None:
            dest_map_name = 'Id'
        else:
            dest_map_name = dest_map.name
        if dest_map_name not in self._vector_field_modules:
            #!# if dest_map.codomain.is_manifestly_parallelizable():
            self._vector_field_modules[dest_map_name] = \
                     VectorFieldFreeModule(self, dest_map=dest_map)
            # else:
        return self._vector_field_modules[dest_map_name]

    def tensor_field_module(self, tensor_type, dest_map=None):
        r"""
        Returns the set of tensor fields of a given type defined on ``self``, 
        possibly within some ambient manifold, as a module over the ring of 
        scalar fields defined on ``self``.

        See :class:`~sage.geometry.manifolds.tensorfield_module.TensorFieldModule` 
        for a complete documentation.  
        
        INPUT:
        
        - ``tensor_type`` -- pair `(k,l)` with `k` being the contravariant 
          rank and `l` the covariant rank
        - ``dest_map`` -- (default: None) destination map 
          `\Phi:\ U \rightarrow V`, where `U` is ``self`` 
          (type: :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`); 
          if none is provided, the identity is assumed (case of tensor fields 
          *on* `U`)

        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.tensorfield_module.TensorFieldModule`
          representing the module `\mathcal{T}^{(k,l)}(U,\Phi)` of type-`(k,l)` 
          tensor fields on the open domain `U` = ``self`` taking values on 
          `\Phi(U)\subset V\subset M`. 
        
        EXAMPLE:
        
        Module of type-(2,1) tensor fields on a 3-dimensional open domain::
        
            sage: M = Manifold(3, 'M')
            sage: U = M.open_domain('U')
            sage: c_xyz.<x,y,z> = U.chart('x y z')
            sage: TU = U.tensor_field_module((2,1)) ; TU
            free module TF^(2,1)(U) of type-(2,1) tensors fields on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: TU.category()
            Category of modules over ring of scalar fields on the open domain 'U' on the 3-dimensional manifold 'M'            
            sage: TU.base_ring()
            ring of scalar fields on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: TU.base_ring() is U.scalar_field_ring()
            True
            sage: TU.an_element()
            tensor field of type (2,1) on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: TU.an_element().view()
            2 d/dx*d/dx*dx

        """
        from tensorfield_module import TensorFieldFreeModule
        if tensor_type == (1,0):
            return self.vector_field_module(dest_map=dest_map)
        if dest_map is None:
            dest_map_name = 'Id'
        else:
            dest_map_name = dest_map.name
        ttype = tuple(tensor_type)
        if (ttype, dest_map_name) not in self._tensor_field_modules:
            #!# if self.is_manifestly_parallelizable():
            self._tensor_field_modules[(ttype, dest_map_name)] = \
              TensorFieldFreeModule(self.vector_field_module(dest_map=dest_map),
                                    ttype)
            # else:
        return self._tensor_field_modules[(ttype, dest_map_name)]


    def scalar_field(self, coord_expression=None, chart=None, name=None, 
                     latex_name=None):
        r"""
        Define a scalar field on the domain.

        See :class:`~sage.geometry.manifolds.scalarfield.ScalarField` for a 
        complete documentation. 

        INPUT:
    
        - ``coord_expression`` -- (default: None) coordinate expression of the 
          scalar field
        - ``chart`` -- (default:None) chart defining the coordinates used in 
          ``coord_expression``; if none is provided and a coordinate expression
           is given, the domain default chart is assumed.
        - ``name`` -- (default: None) name given to the scalar field
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the scalar 
          field; if none is provided, the LaTeX symbol is set to ``name``

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.scalarfield.ScalarField` 
          representing the defined scalar field. 
          
        EXAMPLE:

        A scalar field defined by its coordinate expression::
    
            sage: M = Manifold(3, 'M')
            sage: U = M.open_domain('U')
            sage: c_xyz.<x,y,z> = U.chart('x y z')
            sage: f = U.scalar_field(sin(x)*cos(y) + z, name='F'); f
            scalar field 'F' on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: f.view()
            F: (x, y, z) |--> cos(y)*sin(x) + z
            sage: f.parent()
            ring of scalar fields on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: f in U.scalar_field_ring()
            True

        See the documentation of class 
        :class:`~sage.geometry.manifolds.scalarfield.ScalarField` for more 
        examples.
        
        """
        from scalarfield import ScalarField
        return ScalarField(self, coord_expression, chart, name, latex_name) 


    def vector_field(self, name=None, latex_name=None, dest_map=None):
        r"""
        Define a vector field on the domain.

        See :class:`~sage.geometry.manifolds.vectorfield.VectorField` for a 
        complete documentation. 

        INPUT:
    
        - ``name`` -- (default: None) name given to the vector field
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the vector 
          field; if none is provided, the LaTeX symbol is set to ``name``
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of a vector field *on* ``self``)

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.vectorfield.VectorField` 
          representing the defined vector field. 

        EXAMPLES:

        A vector field on a 3-dimensional open domain::
    
            sage: M = Manifold(3, 'M')
            sage: U = M.open_domain('U')
            sage: c_xyz.<x,y,z> = U.chart('x y z')
            sage: v = U.vector_field('v'); v
            vector field 'v' on the open domain 'U' on the 3-dimensional manifold 'M'
            
        Vector fields on `U` form the set `\mathcal{X}(U)`, which is a module 
        over the algebra `C^\infty(U)` of smooth scalar fields on `U`::
         
            sage: v.parent()
            free module X(U) of vector fields on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: v in U.vector_field_module()
            True


        See the documentation of class 
        :class:`~sage.geometry.manifolds.vectorfield.VectorField` for more 
        examples.
    
        """
        from vectorfield import VectorFieldParal
        if self.is_manifestly_parallelizable():
            return VectorFieldParal(self.vector_field_module(dest_map), 
                                    name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("VectorField not implemented yet")


    def tensor_field(self, k, l, name=None, latex_name=None, sym=None, 
        antisym=None, dest_map=None):
        r"""
        Define a tensor field on the domain.
        
        See :class:`~sage.geometry.manifolds.tensorfield.TensorField` for a 
        complete documentation.

        INPUT:
    
        - ``k`` -- the contravariant rank, the tensor type being (k,l)
        - ``l`` -- the covariant rank, the tensor type being (k,l)
        - ``name`` -- (default: None) name given to the tensor field
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the tensor 
          field; if none is provided, the LaTeX symbol is set to ``name``
        - ``sym`` -- (default: None) a symmetry or a list of symmetries among
          the tensor arguments: each symmetry is described by a tuple containing 
          the positions of the involved arguments, with the convention position=0
          for the first argument. For instance:
            * sym=(0,1) for a symmetry between the 1st and 2nd arguments 
            * sym=[(0,2),(1,3,4)] for a symmetry between the 1st and 3rd
              arguments and a symmetry between the 2nd, 4th and 5th arguments.
        - ``antisym`` -- (default: None) antisymmetry or list of antisymmetries 
          among the arguments, with the same convention as for ``sym``. 
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of a tensor field *on* ``self``)

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.tensorfield.TensorField` 
          representing the defined tensor field. 

        EXAMPLES:

        A tensor field of type (2,0) on a 3-dimensional open domain::
    
            sage: M = Manifold(3, 'M')
            sage: U = M.open_domain('U')
            sage: c_xyz.<x,y,z> = U.chart('x y z')
            sage: t = U.tensor_field(2, 0, 'T'); t
            tensor field 'T' of type (2,0) on the open domain 'U' on the 3-dimensional manifold 'M'

        Type-(2,0) tensor fields on `U` form the set `\mathcal{T}^{(2,0)}(U)`, 
        which is a module over the algebra `C^\infty(U)` of smooth scalar 
        fields on `U`::

            sage: t.parent()
            free module TF^(2,0)(U) of type-(2,0) tensors fields on the open domain 'U' on the 3-dimensional manifold 'M'
            sage: t in U.tensor_field_module((2,0))
            True
            
        See the documentation of class 
        :class:`~sage.geometry.manifolds.tensorfield.TensorField` for more 
        examples.

        """
        from tensorfield import TensorFieldParal
        if self.is_manifestly_parallelizable():
            return TensorFieldParal(self.vector_field_module(dest_map), 
                                    (k,l), name, latex_name, sym, antisym)
        else:
            raise NotImplementedError("TensorField not implemented yet")


    def sym_bilin_form_field(self, name=None, latex_name=None, 
                             dest_map=None):  
        r"""
        Define a field of symmetric bilinear forms on the domain.

        See :class:`~sage.geometry.manifolds.rank2field.SymBilinFormField` for 
        a complete documentation. 

        INPUT:
    
        - ``name`` -- (default: None) name given to the field
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the field; 
          if none is provided, the LaTeX symbol is set to ``name``
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of a field of symmetric bilinear forms *on* ``self``)

        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.rank2field.SymBilinFormField` 
          representing the defined symmetric bilinear form field. 

        EXAMPLE:

        A field of symmetric bilinear forms on a 3-dimensional manifold::
    
            sage: M = Manifold(3, 'M')
            sage: c_xyz.<x,y,z> = M.chart('x y z')
            sage: t = M.sym_bilin_form_field('T'); t
            field of symmetric bilinear forms 'T' on the 3-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.rank2field.SymBilinFormField` for more 
        examples.

        """
        from rank2field import SymBilinFormFieldParal
        if self.is_manifestly_parallelizable():
            return SymBilinFormFieldParal(
                                      self.vector_field_module(dest_map), 
                                      name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("SymBilinFormField not implemented yet")


    def endomorphism_field(self, name=None, latex_name=None, 
                           dest_map=None):  
        r"""
        Define a field of endomorphisms (i.e. linear operators in the tangent 
        spaces = tensors of type (1,1)) on the domain.

        See :class:`~sage.geometry.manifolds.rank2field.EndomorphismField` for 
        a complete documentation. 

        INPUT:
    
        - ``name`` -- (default: None) name given to the field
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the field; 
          if none is provided, the LaTeX symbol is set to ``name``
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of an endomorphism field *on* ``self``)

        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.rank2field.EndomorphismField` 
          representing the defined field of endomorphisms.

        EXAMPLE:

        A field of endomorphisms on a 3-dimensional manifold::
    
            sage: M = Manifold(3, 'M', start_index=1)
            sage: c_xyz.<x,y,z> = M.chart('x y z')
            sage: t = M.endomorphism_field('T'); t
            field of endomorphisms 'T' on the 3-dimensional manifold 'M'
            sage: t.parent()
            free module TF^(1,1)(M) of type-(1,1) tensors fields on the 3-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.rank2field.EndomorphismField` for more 
        examples.

        """
        from rank2field import EndomorphismFieldParal
        if self.is_manifestly_parallelizable():
            return EndomorphismFieldParal(
                                      self.vector_field_module(dest_map), 
                                      name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("EndomorphismField not implemented yet")


    def automorphism_field(self, name=None, latex_name=None, 
                           dest_map=None):  
        r"""
        Define a field of automorphisms (invertible endomorphisms in each 
        tangent space) on the domain.

        See :class:`~sage.geometry.manifolds.rank2field.AutomorphismField` for 
        a complete documentation. 

        INPUT:
    
        - ``name`` -- (default: None) name given to the field
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the field; 
          if none is provided, the LaTeX symbol is set to ``name``
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of an automorphism field *on* ``self``)

        OUTPUT:
        
        - instance of 
          :class:`~sage.geometry.manifolds.rank2field.AutomorphismField` 
          representing the defined field of automorphisms. 

        EXAMPLE:

        A field of automorphisms on a 3-dimensional manifold::
    
            sage: M = Manifold(3,'M')
            sage: c_xyz.<x,y,z> = M.chart('x y z')
            sage: a = M.automorphism_field('A') ; a
            field of tangent-space automorphisms 'A' on the 3-dimensional manifold 'M'
            sage: a.parent()
            free module TF^(1,1)(M) of type-(1,1) tensors fields on the 3-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.rank2field.AutomorphismField` for more 
        examples.

        """
        from rank2field import AutomorphismFieldParal
        if self.is_manifestly_parallelizable():
            return AutomorphismFieldParal(
                                      self.vector_field_module(dest_map), 
                                      name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("AutomorphismField not implemented yet")
            

    def identity_map(self, name=None, latex_name=None, dest_map=None):  
        r"""
        Define the identity map in the tangent spaces on the domain.

        See :class:`~sage.geometry.manifolds.rank2field.IdentityMap` for a 
        complete documentation. 

        INPUT:
    
        - ``name`` -- (default: None) name given to the identity map; if none
          is provided, the value 'Id' is set. 
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the identity
          map; if none is provided, the LaTeX symbol is set to `\mathrm{Id}`
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of a tangent-space identity map field *on* ``self``)

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.rank2field.IdentityMap`
          representing the field of identity maps. 

        EXAMPLE:

        Identity map on a 3-dimensional manifold::
    
            sage: M = Manifold(3, 'M', start_index=1)
            sage: c_xyz.<x,y,z> = M.chart('x y z')
            sage: a = M.identity_map(); a
            field of tangent-space identity maps 'Id' on the 3-dimensional manifold 'M'
            sage: a.comp()
            Kronecker delta of size 3x3            

        See the documentation of class 
        :class:`~sage.geometry.manifolds.rank2field.IdentityMap` for more 
        examples.

        """
        from rank2field import IdentityMapParal
        if name is None:
            name = 'Id'
        if self.is_manifestly_parallelizable():
            return IdentityMapParal(self.vector_field_module(dest_map), 
                                    name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("IdentityMap not implemented yet")


    def vector_frame(self, symbol=None, latex_symbol=None, dest_map=None,
                     from_frame=None): 
        r"""
        Define a vector frame on the domain.
        
        A *vector frame* is a field on the domain that provides, at each point 
        p of the domain, a vector basis of the tangent space at p. 

        See :class:`~sage.geometry.manifolds.vectorframe.VectorFrame` for a 
        complete documentation. 

        INPUT:
    
        - ``symbol`` -- (default: None) a letter (of a few letters) to denote a 
          generic vector of the frame; can be set to None if the parameter
          ``from_frame`` is filled.
        - ``latex_symbol`` -- (default: None) symbol to denote a generic vector 
          of the frame; if None, the value of ``symbol`` is used. 
        - ``dest_map`` -- (default: None) destination map 
          `\Phi:\ U \rightarrow V` 
          (type: :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`); 
          if none is provided, the identity is assumed (case of a vector frame 
          *on* `U`)
        - ``from_frame`` -- (default: None) vector frame `\tilde e` on the 
          codomain `V` of the destination map `\Phi`; 
        - ``from_frame`` -- (default: None) vector frame `\tilde e` on the 
          codomain `V` of the destination map `\Phi`; the returned frame `e` is 
          then such that `\forall p \in U, e(p) = \tilde e(\Phi(p))`
    
        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.vectorframe.VectorFrame`
          representing the defined vector frame. 

        EXAMPLES:

        Setting a vector frame on a 3-dimensional open domain::
    
            sage: M = Manifold(3, 'M')
            sage: A = M.open_domain('A', latex_name=r'\mathcal{A}'); A 
            open domain 'A' on the 3-dimensional manifold 'M'
            sage: c_xyz.<x,y,z> = A.chart('x y z')
            sage: e = A.vector_frame('e'); e 
            vector frame (A, (e_0,e_1,e_2))
            sage: e[0]
            vector field 'e_0' on the open domain 'A' on the 3-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.vectorframe.VectorFrame` for more 
        examples.

        """
        from vectorframe import VectorFrame 
        return VectorFrame(self.vector_field_module(dest_map=dest_map), 
                           symbol=symbol, latex_symbol=latex_symbol,
                           from_frame=from_frame)

    def metric(self, name, signature=None, latex_name=None): 
        r"""
        Define a pseudo-Riemannian metric on the domain.

        See :class:`~sage.geometry.manifolds.metric.Metric` for a complete 
        documentation.

        INPUT:
    
        - ``name`` -- name given to the metric
        - ``signature`` -- (default: None) signature `S` of the metric as a single 
          integer: `S = n_+ - n_-`, where `n_+` (resp. `n_-`) is the number of 
          positive terms (resp. number of negative terms) in any diagonal writing 
          of the metric components; if ``signature`` is not provided, `S` is set to 
          the manifold's dimension (Riemannian signature)
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
          none, it is formed from ``name``      

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.metric.Metric` 
          representing the defined pseudo-Riemannian metric. 

        EXAMPLE:
    
        Metric on a 3-dimensional manifold::
    
            sage: M = Manifold(3, 'M', start_index=1)
            sage: c_xyz.<x,y,z> = M.chart('x y z')
            sage: #!# g = M.metric('g'); g 
            pseudo-Riemannian metric 'g' on the 3-dimensional manifold 'M'
        
        See the documentation of class 
        :class:`~sage.geometry.manifolds.metric.Metric` for more examples.

        """
        from metric import Metric
        return Metric(self, name, signature, latex_name)


    def riemann_metric(self, name, latex_name=None):
        r"""
        Define a Riemannian metric on the domain.

        A Riemannian metric is a field of positive-definite symmetric bilinear 
        forms on the domain. 

        See :class:`~sage.geometry.manifolds.metric.RiemannMetric` for a 
        complete documentation. 
    
        INPUT:
    
        - ``name`` -- name given to the metric
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
          none, it is formed from ``name``      

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.metric.RiemannMetric` 
          representing the defined Riemannian metric.

        EXAMPLE:
    
        Standard metric on the 2-sphere `S^2`::
    
            sage: M = Manifold(2, 'S^2', start_index=1)
            sage: c_spher.<th,ph> = M.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: #!# g = M.riemann_metric('g'); g
            Riemannian metric 'g' on the 2-dimensional manifold 'S^2'
            sage: #!# g[1,1], g[2,2] = 1, sin(th)^2
            sage: #!# g.view()
            g = dth*dth + sin(th)^2 dph*dph
            sage: #!# g.signature() 
            2

        See the documentation of class 
        :class:`~sage.geometry.manifolds.metric.RiemannMetric` for more examples.

        """  
        from metric import RiemannMetric
        return RiemannMetric(self, name, latex_name)


    def lorentz_metric(self, name, signature='positive', latex_name=None):
        r"""
        Define a Lorentzian metric on the domain.

        A Lorentzian metric is a field of nondegenerate symmetric bilinear 
        forms with signature `(-,+,\cdots,+)` or `(+,-,\cdots,-)`. 

        See :class:`~sage.geometry.manifolds.metric.LorentzMetric` for a 
        complete documentation. 
    
        INPUT:
    
        - ``name`` -- name given to the metric
        - ``signature`` -- (default: 'positive') sign of the metric signature: 
          * if set to 'positive', the signature is n-2, where n is the manifold's
            dimension, i.e. `(-,+,\cdots,+)`
          * if set to 'negative', the signature is -n+2, i.e. `(+,-,\cdots,-)`
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the metric; if
          none, it is formed from ``name``      

        OUTPUT:
        
        - instance of :class:`~sage.geometry.manifolds.metric.LorentzMetric` 
          representing the defined Lorentzian metric.

        EXAMPLE:
    
        Metric of Minkowski spacetime::
    
            sage: M = Manifold(4, 'M')
            sage: c_cart = M.chart('t x y z')
            sage: #!# g = M.lorentz_metric('g'); g
            Lorentzian metric 'g' on the 4-dimensional manifold 'M'
            sage: #!# g[0,0], g[1,1], g[2,2], g[3,3] = -1, 1, 1, 1
            sage: #!# g.view()
            g = -dt*dt + dx*dx + dy*dy + dz*dz
            sage: #!# g.signature()
            2 

        See the documentation of class 
        :class:`~sage.geometry.manifolds.metric.LorentzMetric` for more 
        examples.

        """
        from metric import LorentzMetric
        return LorentzMetric(self, name, signature, latex_name)


    def diff_form(self, degree, name=None, latex_name=None, 
                  dest_map=None):
        r"""

        Define a differential form on the domain.

        See :class:`~sage.geometry.manifolds.diffform.DiffForm` for a complete 
        documentation. 
    
        INPUT:
    
        - ``degree`` -- the degree `p` of the differential form (i.e. its 
          tensor rank)
        - ``name`` -- (default: None) name given to the differential form
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          differential form; if none is provided, the LaTeX symbol is set to ``name``
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of a differential form *on* ``self``)

        OUTPUT:
        
        - the `p`-form, as an instance of 
          :class:`~sage.geometry.manifolds.diffform.DiffForm`

        EXAMPLE:
    
        A 2-form on a 4-dimensional open domain::
    
            sage: M = Manifold(4, 'M')
            sage: A = M.open_domain('A', latex_name=r'\mathcal{A}'); A 
            open domain 'A' on the 4-dimensional manifold 'M'
            sage: c_xyzt.<x,y,z,t> = A.chart('x y z t')
            sage: f = A.diff_form(2, 'F'); f
            2-form 'F' on the open domain 'A' on the 4-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.diffform.DiffForm` for more examples.

        """
        from diffform import DiffFormParal
        if self.is_manifestly_parallelizable():
            return DiffFormParal(self.vector_field_module(dest_map), 
                                 degree, name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("DiffForm not implemented yet")


    def one_form(self, name=None, latex_name=None, dest_map=None):
        r"""    
        Define a 1-form on the domain.

        See :class:`~sage.geometry.manifolds.diffform.OneForm` for a complete 
        documentation. 

        INPUT:
    
        - ``name`` -- (default: None) name given to the 1-form
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 1-form; 
          if none is provided, the LaTeX symbol is set to ``name``
        - ``dest_map`` -- (default: None) instance of 
          class :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
          representing the destination map `\Phi:\ U \rightarrow V`, where `U` 
          is ``self``; if none is provided, the identity map is assumed (case 
          of a 1-form *on* ``self``)

        OUTPUT:
        
        - the 1-form, as an instance of 
          :class:`~sage.geometry.manifolds.diffform.OneForm`

        EXAMPLE:
    
        A 1-form on a 3-dimensional open domain::
    
            sage: M = Manifold(3, 'M')
            sage: A = M.open_domain('A', latex_name=r'\mathcal{A}')
            sage: X.<x,y,z> = A.chart('x y z')                      
            sage: om = A.one_form('omega', r'\omega') ; om  
            1-form 'omega' on the open domain 'A' on the 3-dimensional manifold 'M'
            sage: om.parent()
            free module TF^(0,1)(A) of type-(0,1) tensors fields on the open domain 'A' on the 3-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.diffform.OneForm` for more examples.

        """
        from diffform import OneFormParal
        if self.is_manifestly_parallelizable():
            return OneFormParal(self.vector_field_module(dest_map), 
                                name=name, latex_name=latex_name)
        else:
            raise NotImplementedError("OneForm not implemented yet")


    def diff_mapping(self, domain, coord_functions=None, chart_from=None, 
                     chart_to=None, name=None, latex_name=None):
        r"""
        Define a differentiable mapping between the current domain and another
        domain (possibly on another manifold). 
        
        See :class:`~sage.geometry.manifolds.diffmapping.DiffMapping` for a 
        complete documentation. 
        
        INPUT:

        - ``domain`` -- domain on the arrival manifold 
        - ``coord_functions`` -- (default: None) the coordinate symbolic expression 
          of the mapping: list (or tuple) of the coordinates of the image expressed 
          in terms of the coordinates of the considered point; if the dimension of 
          the arrival manifold is 1, a single expression is expected 
          (not a list with a single element)
        - ``chart_from`` -- (default: None) chart in which the 
          coordinates are given on the domain being mapped; if none is provided, 
          the coordinates are assumed to refer to domain's default chart
        - ``chart_to`` -- (default: None) chart in which the 
          coordinates are given on the image domain; if none is provided, the coordinates 
          are assumed to refer to the domain's default chart
        - ``name`` -- (default: None) name given to the differentiable mapping
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          differentiable mapping; if none is provided, the LaTeX symbol is set to 
          ``name``

        OUTPUT:
        
        - the differentiable mapping, as an instance of 
          :class:`~sage.geometry.manifolds.diffmapping.DiffMapping`
    
        EXAMPLE:
    
        A mapping between the sphere `S^2` and `\RR^3`::

            sage: M = Manifold(2, 'S^2')
            sage: U = M.open_domain('U') # the subdomain of S^2 covered by regular spherical coordinates
            sage: c_spher.<th,ph> = U.chart(r'th:(0,pi):\theta ph:(0,2*pi):\phi')
            sage: N = Manifold(3, 'R^3', r'\RR^3')
            sage: c_cart.<x,y,z> = N.chart('x y z')  # Cartesian coord. on R^3
            sage: Phi = U.diff_mapping(N, (sin(th)*cos(ph), sin(th)*sin(ph), cos(th)), name='Phi', latex_name=r'\Phi')

        See the documentation of class 
        :class:`~sage.geometry.manifolds.diffmapping.DiffMapping` for more 
        examples.

        """
        from diffmapping import DiffMapping
        return DiffMapping(self, domain, coord_functions, chart_from, 
                           chart_to, name, latex_name)


    def diffeomorphism(self, domain, coord_functions=None, chart_from=None, 
                       chart_to=None, name=None, latex_name=None):
        r"""
        Define a diffeomorphism between the current domain and another
        domain (possibly on another manifold). 
        
        See :class:`~sage.geometry.manifolds.diffmapping.Diffeomorphism` for a 
        complete documentation. 

        INPUT:

        - ``domain`` -- domain on the arrival manifold 
        - ``coord_functions`` -- the coordinate symbolic expression of the mapping: 
          list (or tuple) of the coordinates of the image expressed in terms of the
          coordinates of the considered point
        - ``chart_from`` -- (default: None) chart in which the
          coordinates are given on the domain being mapped; if none is provided, 
          the coordinates are assumed to refer to the domain's default chart
        - ``chart_to`` -- (default: None) chart in which the
          coordinates are given on the image domain; if none is provided, the coordinates 
          are assumed to refer to the domain's default chart
        - ``name`` -- (default: None) name given to the differentiable mapping
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the 
          differentiable mapping; if none is provided, the LaTeX symbol is set to 
          ``name``

        OUTPUT:
        
        - the diffeomorphism, as an instance of 
          :class:`~sage.geometry.manifolds.diffmapping.Diffeomorphism`

        EXAMPLE:
    
        A diffeomorphism between two 2-dimensional domains::

            sage: M = Manifold(2, 'M', r'{\cal M}')
            sage: U = M.open_domain('U')
            sage: c_xv.<x,y> = U.chart(r'x:(-pi/2,+oo) y:(-pi/2,+oo)')
            sage: N = Manifold(2, 'N', r'{\cal N}')
            sage: V = N.open_domain('V')
            sage: c_zt.<z,t> = V.chart(r'z t')
            sage: Phi = U.diffeomorphism(V, (arctan(x), arctan(y)), name='Phi', latex_name=r'\Phi')

        See the documentation of class 
        :class:`~sage.geometry.manifolds.diffmapping.Diffeomorphism` for more 
        examples.

        """
        from diffmapping import Diffeomorphism
        return Diffeomorphism(self, domain, coord_functions, chart_from, 
                              chart_to, name, latex_name)


    def aff_connection(self, name, latex_name=None):
        r"""
        Define an affine connection on the domain. 
        
        See :class:`~sage.geometry.manifolds.connection.AffConnection` for a 
        complete documentation. 

        INPUT:
    
        - ``name`` -- name given to the affine connection
        - ``latex_name`` -- (default: None) LaTeX symbol to denote the affine 
          connection
          
        OUTPUT:
        
        - the affine connection, as an instance of 
          :class:`~sage.geometry.manifolds.connection.AffConnection`

        EXAMPLE:
    
        Affine connection on a 3-dimensional domain::
    
            sage: M = Manifold(3, 'M', start_index=1)
            sage: A = M.open_domain('A', latex_name=r'\mathcal{A}')
            sage: #!# nab = A.aff_connection('nabla', r'\nabla') ; nab
            affine connection 'nabla' on the domain 'A' on the 3-dimensional manifold 'M'

        See the documentation of class 
        :class:`~sage.geometry.manifolds.connection.AffConnection` for more 
        examples.

        """
        from connection import AffConnection
        return AffConnection(self, name, latex_name)

