# -*- coding: utf-8 -*-
# Ported to mathutf (onp ypi)
import ubelt as ub


class MathSymbolsUnicode:
    """
    https://en.wikipedia.org/wiki/Mathematical_operators_and_symbols_in_Unicode

    https://www.quora.com/What-do-mathbb-C-mathbb-F-mathbb-H-mathbb-N-mathbb-Q-mathbb-R-mathbb-S-and-mathbb-Z-mean

    https://mathworld.wolfram.com/Doublestruck.html

    https://peterjamesthomas.com/maths-science/a-brief-taxonomy-of-numbers/

    http://xahlee.info/comp/unicode_math_operators.html

    # Example:
    #     >>>
    """
    sym_elementof   = 'ϵ'
    sym_finitefield = '𝔽'

    sym_natural     = 'ℕ'
    sym_integral    = 'ℤ'
    sym_rational    = 'ℚ'

    sym_complex     = 'ℂ'
    sym_quaternions = 'ℍ'
    sym_octernion   = '𝕆'

    sym_irrational  = 'ℙ'
    sym_real        = 'ℝ'

    sym_floating    = '𝕃'
    sym_list        = '[]'

    _greek_alphabet = ub.codeblock(
        """
        Α    α      Alpha     a
        Β    β      Beta      b
        Γ    γ      Gamma     g
        Δ    δ      Delta     d
        Ε    ε      Epsilon   e
        Ζ    ζ      Zeta      z
        Η    η      Eta       h
        Θ    θ      Theta     th
        Ι    ι      Iota      i
        Κ    κ      Kappa     k
        Λ    λ      Lambda    l
        Μ    μ      Mu        m
        Ν    ν      Nu        n
        Ξ    ξ      Xi        x
        Ο    ο      Omicron   o
        Π    π      Pi        p
        Ρ    ρ      Rho       r
        Σ    σ,ς *  Sigma     s
        Τ    τ      Tau       t
        Υ    υ      Upsilon   u
        Φ    φ      Phi       ph
        Χ    χ      Chi       ch
        Ψ    ψ      Psi       ps
        Ω    ω      Omega     o

        Superscripts: ⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁺ ⁻ ⁼ ⁽ ⁾ ⁿ ⁱ
        Subscripts: ₀ ₁ ₂ ₃ ₄ ₅ ₆ ₇ ₈ ₉ ₊ ₋ ₌ ₍ ₎ ₐ ₑ ₕ ᵢ ⱼ ₖ ₗ ₘ ₙ ₒ ₚ ᵣ ₛ ₜ ᵤ ᵥ ₓ
        """)

    _notes = ub.codeblock(
        """
        # Variables
        alpha = α
        beta = β
        delta = δ
        epsilon = ε
        theta = θ
        lambda = λ
        mu = μ
        phi = φ
        psi = ψ
        omega = Ω

        alpha   = α
        beta    = β
        gamma   = γ
        delta   = δ
        epsilon = ε
        zeta    = ζ
        eta     = η
        theta   = θ
        iota    = ι
        kappa   = κ
        lambda  = λ
        nu      = ν
        mu      = μ
        xi      = ξ
        omicron = ο
        pi      = π
        rho     = ρ
        sigma   = σ
        tau     = τ
        upsilon = υ
        phi     = φ
        chi     = χ
        psi     = ψ
        omega   = ω


        # Special meta-numeric symbols
        pi            = π  # 3.14... ratio of circle circumference to the diameter
        tau           = 𝜏  # 6.28... ratio of circle circumference to its radius... it makes a tad more sense
        infinity      = ∞

        # Existential quantifiers
        forall        = ∀
        exists        = ∃
        forall        = ∀
        not_exists    = ∄

        delta_upper   = ∆

        # Calculus
        partial       = ∂
        integral      = ∫

        # Relational
        eq        = =
        ne        = ≠
        le        = ≦
        ge        = ≥
        lt        = <
        gt        = >
        approx_eq = ≈
        approx_ne = ≇
        strict_approx_ne = ≆
        propor    = ∝
        equiv     = ≡
        not_equiv = ≢

        # n-ary operations
        product       = ∏
        sumation      = ∑
        big_isect     = ⋂
        big_union     = ⋃

        union = ∪

        # Root operations
        square_root   = √
        cube_root     = ∛
        quad_root     = ∜

        # Logical
        and           = ∧
        or            = ∨
        not           = ¬

        # Set operations
        emptyset      = ∅
        isect         = ∩

        # Membership
        elementof     = ϵ
        not_elementof = ∉

        subset_lt = ⊂  # strict subset of
        subset_gt = ⊃  # strict superset of
        subset_le = ⊆  # subset
        subset_ge = ⊇  # superset
        subset_not_ge = ⊉
        subset_not_gt = ⊅
        subset_not_lt = ⊄
        subset_not_le = ⊈
        """)

