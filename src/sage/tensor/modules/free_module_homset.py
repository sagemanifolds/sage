r"""
Sets of morphisms between free modules

The class :class:`FreeModuleHomset` implements sets (actually free modules) of
homomorphisms between two free modules of finite rank over the same 
commutative ring. 

AUTHORS:

- Eric Gourgoulhon, Michal Bejger (2014): initial version

"""
#******************************************************************************
#       Copyright (C) 2014 Eric Gourgoulhon <eric.gourgoulhon@obspm.fr>
#       Copyright (C) 2014 Michal Bejger <bejger@camk.edu.pl>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#******************************************************************************

from sage.categories.homset import Homset
from free_module_morphism import FiniteRankFreeModuleMorphism
from free_module_tensor import FreeModuleTensor

class FreeModuleHomset(Homset):
    r"""
    Set of homomorphisms between free modules of finite rank
    
    Given two free modules `M` and `N` of respective ranks `m` and `n` over a 
    commutative ring `R`, the class :class:`FreeModuleHomset` implements the 
    set `\mathrm{Hom}(M,N)` of homomorphisms `M\rightarrow N`. This is a 
    *parent* class, whose *elements* are instances of 
    :class:`~sage.tensor.modules.free_module_morphism.FiniteRankFreeModuleMorphism`

    The set `\mathrm{Hom}(M,N)` is actually a free module of rank `mn` over 
    `R`, but this aspect is not taken into account here. 

    INPUT:
    
    - ``fmodule1`` -- free module `M` (domain of the homomorphisms); must be
      an instance of 
      :class:`~sage.tensor.modules.finite_rank_free_module.FiniteRankFreeModule`
    - ``fmodule2`` -- free module `N` (codomain of the homomorphisms); must be
      an instance of 
      :class:`~sage.tensor.modules.finite_rank_free_module.FiniteRankFreeModule`
    - ``name`` -- (string; default: None) name given to the hom-set; if None, 
      Hom(M,N) will be used
    - ``latex_name`` -- (string; default: None) LaTeX symbol to denote the 
      hom-set; if None, `\mathrm{Hom}(M,N)` will be used

    EXAMPLES:
    
    Set of homomorphisms between two free modules over `\ZZ`::
    
        sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
        sage: N = FiniteRankFreeModule(ZZ, 2, name='N')
        sage: H = Hom(M,N) ; H
        Set of Morphisms from rank-3 free module M over the Integer Ring to rank-2 free module N over the Integer Ring in Category of modules over Integer Ring
        sage: type(H)
        <class 'sage.tensor.modules.free_module_homset.FreeModuleHomset_with_category_with_equality_by_id'>
        sage: H.category()
        Category of homsets of modules over Integer Ring

    Hom-sets are cached::
    
        sage: H is Hom(M,N)
        True

    The LaTeX formatting is::
    
        sage: latex(H)
        \mathrm{Hom}\left(M,N\right)

    As usual, the construction of an element is performed by the ``__call__`` 
    method; the argument can be the matrix representing the morphism in the 
    default bases of the two modules::
    
        sage: e = M.basis('e')
        sage: f = N.basis('f')
        sage: phi = H([[-1,2,0], [5,1,2]]) ; phi
        Generic morphism:
          From: rank-3 free module M over the Integer Ring
          To:   rank-2 free module N over the Integer Ring
        sage: phi.parent() is H
        True

    An example of construction from a matrix w.r.t. bases that are not the
    default ones::
    
        sage: ep = M.basis('ep', latex_symbol=r"e'")
        sage: fp = N.basis('fp', latex_symbol=r"f'")
        sage: phi2 = H([[3,2,1], [1,2,3]], bases=(ep,fp)) ; phi2
        Generic morphism:
          From: rank-3 free module M over the Integer Ring
          To:   rank-2 free module N over the Integer Ring

    The zero element::
    
        sage: z = H.zero() ; z
        Generic morphism:
          From: rank-3 free module M over the Integer Ring
          To:   rank-2 free module N over the Integer Ring
        sage: z.matrix(e,f)
        [0 0 0]
        [0 0 0]

    The test suite for H is passed::
    
        sage: TestSuite(H).run(verbose=True)
        running ._test_additive_associativity() . . . pass
        running ._test_an_element() . . . pass
        running ._test_category() . . . pass
        running ._test_elements() . . .
          Running the test suite of self.an_element()
          running ._test_category() . . . pass
          running ._test_eq() . . . pass
          running ._test_nonzero_equal() . . . pass
          running ._test_not_implemented_methods() . . . pass
          running ._test_pickling() . . . pass
          pass
        running ._test_elements_eq_reflexive() . . . pass
        running ._test_elements_eq_symmetric() . . . pass
        running ._test_elements_eq_transitive() . . . pass
        running ._test_elements_neq() . . . pass
        running ._test_eq() . . . pass
        running ._test_not_implemented_methods() . . . pass
        running ._test_pickling() . . . pass
        running ._test_some_elements() . . . pass
        running ._test_zero() . . . pass

    The set of homomorphisms `M\rightarrow M`, i.e. endomorphisms, is 
    obtained by the function ``End``::
    
        sage: End(M)
        Set of Morphisms from rank-3 free module M over the Integer Ring to rank-3 free module M over the Integer Ring in Category of modules over Integer Ring
        
    ``End(M)`` is actually identical to ``Hom(M,M)``::
    
        sage: End(M) is Hom(M,M)
        True

    There is a canonical identification between endomorphisms of `M` and 
    tensors of type (1,1) on `M`. Accordingly, coercion maps have been 
    implemented between `\mathrm{End}(M)` and `T^{(1,1)}(M)` (the module of
    all type-(1,1) tensor on `M`, see 
    :class:`~sage.tensor.modules.tensor_free_module.TensorFreeModule`)::
        
        sage: T11 = M.tensor_module(1,1) ; T11
        free module of type-(1,1) tensors on the rank-3 free module M over the Integer Ring
        sage: End(M).has_coerce_map_from(T11)
        True
        sage: T11.has_coerce_map_from(End(M))
        True

    See :class:`~sage.tensor.modules.tensor_free_module.TensorFreeModule` for
    examples of the above coercions.

    """

    Element = FiniteRankFreeModuleMorphism

    def __init__(self, fmodule1, fmodule2, name=None, latex_name=None):
        r"""
        TESTS::
        
            sage: from sage.tensor.modules.free_module_homset import FreeModuleHomset
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: N = FiniteRankFreeModule(ZZ, 2, name='N')
            sage: FreeModuleHomset(M, N)
            Set of Morphisms from rank-3 free module M over the Integer Ring to rank-2 free module N over the Integer Ring in Category of modules over Integer Ring
            sage: H = FreeModuleHomset(M, N, name='L(M,N)', latex_name=r'\mathcal{L}(M,N)')
            sage: latex(H)
            \mathcal{L}(M,N)
        
        """
        from finite_rank_free_module import FiniteRankFreeModule
        if not isinstance(fmodule1, FiniteRankFreeModule):
            raise TypeError("fmodule1 = " + str(fmodule1) + " is not an " + 
                            "instance of FiniteRankFreeModule.")
        if not isinstance(fmodule2, FiniteRankFreeModule):
            raise TypeError("fmodule1 = " + str(fmodule2) + " is not an " + 
                            "instance of FiniteRankFreeModule.")
        if fmodule1.base_ring() != fmodule2.base_ring():
            raise TypeError("The domain and codomain are not defined over " + 
                            "the same ring.")
        Homset.__init__(self, fmodule1, fmodule2)
        if name is None:
            self._name = "Hom(" + fmodule1._name + "," + fmodule2._name + ")"
        else:
            self._name = name
        if latex_name is None:
            self._latex_name = \
                    r"\mathrm{Hom}\left(" + fmodule1._latex_name + "," + \
                    fmodule2._latex_name + r"\right)"
        else:
            self._latex_name = latex_name
        
    def _latex_(self):
        r"""
        LaTeX representation of the object.
        
        EXAMPLES::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: N = FiniteRankFreeModule(ZZ, 2, name='N')
            sage: H = Hom(M,N)
            sage: H._latex_()
            '\\mathrm{Hom}\\left(M,N\\right)'
            sage: latex(H)  # indirect doctest
            \mathrm{Hom}\left(M,N\right)
        
        """
        if self._latex_name is None:
            return r'\mbox{' + str(self) + r'}'
        else:
           return self._latex_name
            
    def __call__(self, *args, **kwds):
        r"""
        To bypass Homset.__call__, enforcing Parent.__call__ instead.
        """
        from sage.structure.parent import Parent
        return Parent.__call__(self, *args, **kwds)
        
    #### Methods required for any Parent 

    def _element_constructor_(self, matrix_rep, bases=None, name=None, 
                              latex_name=None):
        r"""
        Construct an element of ``self``, i.e. a homomorphism M --> N, where
        M is the domain of ``self`` and N its codomain. 
        
        INPUT:
        
        - ``matrix_rep`` -- matrix representation of the homomorphism with 
          respect to the bases ``basis1`` and ``basis2``; this entry can actually
          be any material from which a matrix of size rank(N)*rank(M) can be 
          constructed
        - ``bases`` -- (default: None) pair (basis_M, basis_N) defining the 
          matrix representation, basis_M being a basis of module `M` and
          basis_N a basis of module `N` ; if None the pair formed by the 
          default bases of each module is assumed. 
        - ``name`` -- (string; default: None) name given to the homomorphism
        - ``latex_name`` -- (string; default: None) LaTeX symbol to denote the 
          homomorphism; if None, ``name`` will be used. 
         
        EXAMPLES:
    
        Construction of a homomorphism between two free `\ZZ`-modules::
        
            sage: M = FiniteRankFreeModule(ZZ, 3, name='M')
            sage: N = FiniteRankFreeModule(ZZ, 2, name='N')
            sage: e = M.basis('e') ; f = N.basis('f')
            sage: H = Hom(M,N)
            sage: phi = H._element_constructor_([[2,-1,3], [1,0,-4]], bases=(e,f), name='phi', latex_name=r'\phi')
            sage: phi
            Generic morphism:
              From: rank-3 free module M over the Integer Ring
              To:   rank-2 free module N over the Integer Ring
            sage: phi.matrix(e,f)
            [ 2 -1  3]
            [ 1  0 -4]
            sage: phi == H([[2,-1,3], [1,0,-4]], bases=(e,f), name='phi', latex_name=r'\phi')
            True

        Construction of an endomorphism::
        
            sage: EM = End(M) 
            sage: phi = EM._element_constructor_([[1,2,3],[4,5,6],[7,8,9]], name='phi', latex_name=r'\phi')
            sage: phi
            Generic endomorphism of rank-3 free module M over the Integer Ring
            sage: phi.matrix(e,e)
            [1 2 3]
            [4 5 6]
            [7 8 9]

        Coercion of a type-(1,1) tensor to an endomorphism::
        
            sage: a = M.tensor((1,1))
            sage: a[:] = [[1,2,3],[4,5,6],[7,8,9]]
            sage: EM = End(M)             
            sage: phi_a = EM._element_constructor_(a) ; phi_a
            Generic endomorphism of rank-3 free module M over the Integer Ring
            sage: phi_a.matrix(e,e)
            [1 2 3]
            [4 5 6]
            [7 8 9]
            sage: phi_a == phi
            True
            sage: phi_a1 = EM(a) ; phi_a1  # indirect doctest
            Generic endomorphism of rank-3 free module M over the Integer Ring
            sage: phi_a1 == phi
            True

        """
        if isinstance(matrix_rep, FreeModuleTensor):
            # coercion of a type-(1,1) tensor to an endomorphism
            tensor = matrix_rep # for readability
            if tensor.tensor_type() == (1,1) and \
                                         self.is_endomorphism_set() and \
                                         tensor.base_module() is self.domain():
                basis = tensor.pick_a_basis()
                tcomp = tensor.comp(basis)
                fmodule = tensor.base_module()
                mat = [[ tcomp[[i,j]] for j in fmodule.irange()] \
                                                     for i in fmodule.irange()]
                resu = self.element_class(self, mat, bases=(basis,basis), 
                                          name=tensor._name, 
                                          latex_name=tensor._latex_name)
            else:
                raise TypeError("Cannot coerce the " + str(tensor) +
                                " to an element of " + str(self) + ".")
        else:
            # Standard construction:
            resu = self.element_class(self, matrix_rep, bases=bases, name=name, 
                                      latex_name=latex_name)
        return resu
        
    def _an_element_(self):
        r"""
        Construct some (unamed) element.
        
        EXAMPLE::
        
        """
        ring = self.base_ring()
        m = self.domain().rank()
        n = self.codomain().rank()
        matrix_rep = [[ring.an_element() for i in range(m)] for j in range(n)]
        return self.element_class(self, matrix_rep)
            
    def _coerce_map_from_(self, other):
        r"""
        Determine whether coercion to self exists from other parent.
        """
        from tensor_free_module import TensorFreeModule
        if isinstance(other, TensorFreeModule):
            # Coercion of a type-(1,1) tensor to an endomorphism:
            if other.tensor_type() == (1,1):
                if self.is_endomorphism_set() and \
                                          other.base_module() is self.domain():
                    return True
        return False

    #### End of methods required for any Parent 
