# Understanding and Modeling Polymers: The Challenge of Multiple Scales Friederike Schmid*

## I. INTRODUCTION



Multiscale problems are omnipresent in materials science. The properties of most materials result from a combination of many processes on vastly different length and time scales, ranging from electronic excitations and atomic or molecular vibrations on the Angstrom and femtosecond scale to material fatigue on time scales over several years. In polymeric systems, disentangling the different characteristic scales that determine their behavior is particularly difficult. This is because the relevant molecular length scales-which range from the scale of the local chemical monomer structure to the scale of chain conformations- strongly overlap with the relevant length scales of the next level of intermolecular and possibly supra-molecular organization, and these in turn overlap with the length scales of continuum mechanics on which materials are described in terms of elastohydrodynamic equations. Therefore, the all-inclusive, comprehensive modeling of a polymeric system1 remains a formidable challenge despite decades of theoretical efforts.2-17

In the present Perspective, we discuss some selected approaches to this problem, focusing on recent developments. Before doing so, we will quote a few examples of scale-bridging phenomena in polymers that inherently require multiscale descriptions.

The first and most basic example is the emerging viscoelasticity and viscoplasticity in polymer rheology, a field where the multiscale character of polymer-based systems is immediately apparent.18 Polymeric materials respond to applied stress with some time delay (memory), a clear signature of an

incomplete separation of time scales. This is because the time scales of intramolecular (internal chain) relaxation cannot be separated from the time scales of diffusion and intermolecular reorganization, in particular in the presence of entanglements.6

Another prominent classical multiscale phenomenon in polymer science is polymer crystallization," which involves local crystallization on the monomer scale, the formation of crystalline lamellae on the mesoscale, and the macroscale organization of lamellae, often into spherulites.20 Already the local structure is not necessarily unique,21 but may result from a competition of several polymorphs depending on the process- ing.22 Predicting such polymorphs requires accurate theoretical descriptions at the electronic structure level20 as well as multiscale modeling approaches to enable studying the kinetics of self-assembly.23,24 On the mesoscale, the mechanisms that determine and eventually constrain the growth of crystalline lamellae are still under debate.25 One particular intriguing phenomenon is the "melt memory" effect:20, Even after melting a polymer crystal, the melt retains some knowledge about the previous structure and tends to recrystallize at previously crystalline positions after cooling. Recent systematic

Received: September 2, 2022 Revised: October 14, 2022 Accepted: October 14, 2022 Published: November 14, 2022

POLYMERS Au

ACS Publications

@ 2022 The Author. Published by American Chemical Society

28

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

29

Perspective

## ACS Polymers Au



simulation studies by Luo, Sommer, and others have suggested that the thickness of crystalline lamellae is determined by the entanglement length in the melt prior to crystallization,28-33 consistent with the experimental observation that the time scale on which the melt memory survives roughly matches the time scale of re-entanglement kinetics.34 Such findings illustrate how mesoscale structure (entanglements) can have a profound effect on local structure (local packing), and vice versa, in polymers. The associated time scales can be very large, which offers unusually versatile opportunities to control local structure by processing35 (for example, in flow-induced crystallization36-40) or by tiny chemical modifications.41,42 On the other hand, the mesoscale structure and dynamics determines the elastic and plastic response of the materials to deformations43,44 and the inhomogeneous stress fields in the materials, which in turn drive the large-scale structure formation and spherulite growth.45

The interplay of multiple scales also determines the structural and dynamic properties of other multiphase polymer materials46 that are highly heterogeneous and filled by internal interfaces, such as polymer blends,47,48 19-32 block copolymer melts and solutions, ** or foams.53 It is particularly prominent in polymer nanocomposites, 54-58 where fillers are introduced, e.g., to improve the mechanical properties of a polymeric matrix. The molecular origins of the resulting mechanical reinforcement are diverse, they include a redistribution of strain in the polymer matrix39 as well as stretching of chains at the interfaces.60 A detailed knowledge of the structure of the material on both local and mesoscopic scales is thus necessary to understand the macroscopic viscoelastic properties of the materials. Likewise, transport properties such as the thermal conductivity61 depend on the microscopic structure in the bulk matrix as well as at interfaces, i.e., the Kapitza resistance,62-64 and on the mesoscale shape and spatial distribution of the fillers.

Finally, biomaterials provide some of the most sophisticated polymer-based multiscale materials, due to their characteristic hierarchical structure. A prominent example is spider silk, 65,66 which also showcases how the properties of such materials may crucially depend on the way how they has been processed (in this case spun).67 Other examples are fibers made of collagen, which are abundant in mammals.68-71 Collagen is found in the extracellular matrix of tissues as different as skin, fascia, cartilage and bones, and is to a great extent responsible for their superior material properties. Twenty-nine types of collagen have been reported in the literature,08 with the most frequent being collagen I, which is present in, e.g., dermis, tendon, and bone. The primary structure of collagen peptides is characterized by repeats of three residues Gly-X-Y, e.g., Gly-Pro-Hyp. The quaternary structure is a triple helix, where three polypeptide strands wrap around each other to form a helix of length ~300 nm, the tropocollagen. Staggered arrays of tropocollagen self- assemble (spontaneously72) to fibrils, the building blocks of fibers (with size roughly 10 um), which then aggregate to even larger structures.73 Remarkably, the collagen triple helix seems to be only marginally stable; it melts at temperatures just slightly above, or even below the body temperature. + This suggests, on the one hand, that the triple helix is stabilized by the fibrillar/ microfibrillar suprastructure,"but also, on the other hand, that collagen frequently unfolds and refolds on a local scale. The combination of strength and softness would then contribute to the unique material properties of collagen tissues, to their elasticity, and to their capacity to dissipate sudden energy bursts.

In the context of living tissues, protein fibers are only one building block in the even more complex multiscale structures

of, e.g., bones75,76 or skin.77 One important aspect of living materials is their dissipative character: They are kept alive by constant energy consumption and thus never reach thermal equilibrium, nor a thermally metastable state, but continuously produce entropy. Prominent representatives of such inherently nonequilibrium materials are protein filament structures which form the cytoskeleton of cells and are responsible for their mechanical elasticity as well as their motion and/or contrac- tion. Another example is the recently discovered phenom- enon of liquid-liquid phase separation (LLPS) in cells:80-87 Certain proteins mediate the formation of nanosized con- densates in cells-so-called membraneless organelles-which helps to organize cellular content and possibly contributes to gene regulation. Whereas the phase separation itself is driven by thermodynamic interactions, the size and location of the droplets is most likely controlled by nonequilibrium, energy- consuming processes.

These selected examples illustrate the omnipresence of multiscale phenomena in polymeric systems, in seemingly simple ones such as one-component polymer melts as well as in complex ones such as functional polymers in a nonequilibrium living matter context. The multiscale character of polymers presents an outstanding challenge for modellers.

Synthetic polymer systems have been among the first materials for which systematic multiscale modeling methods have been developed, which related particle-based coarse- grained models to real polymers such as polyethylene,88-93 polycarbonates, 94-98 and others. 99,100 These early studies already addressed key challenges that are still subject of active research today: (i) The coarse-graining procedure, i.e. constructing coarse-grained models using input from quantum chemical calculations and/or atomistic models; .. 88-91,94-96,99,100 (ii) reverse backmapping, i.e., the reconstruction of an atomistic configuration from a coarse-grained configuration; 92,97,98

(iii) dynamic mapping, 93,97 i.e., the question how to extract dynamical information from the coarse-grained simulations.

Since then, much progress has been made in the field of multiscale modeling of polymers and of soft matter systems in general, and several excellent reviews have highlighted different aspects of the problem, see, e.g., refs 4-8, 10, 12, 14-16, 101, and 102. Nevertheless, central challenges still persist. In the present Perspective, we discuss the current situation in the light of the state of the art and recent progress. We begin with a rough outline of models that are used to describe polymeric systems on different scales. Then we discuss a number of scale-bridging strategies that have been developed in the past and used for polymeric systems or might be applicable for them. We close with a brief outlook on open problems for the future.

## II. SCALES IN POLYMERS



To set the stage, we begin with discussing the different scales that are involved in our multiscale picture of polymers and introduce classes of polymer models that are used to study polymer materials at these different levels.

## II.A. Monomer/Oligomer Scale: The Scales of Chemical Specificity



The basic building blocks are the monomers. They can have a simple chemical structure, as in the case of many commodity polymers such as polystyrene, or a rather complicated structure, as in the case of biopolymers such as RNA, DNA, or proteins. The structure of the monomers on the monomer scale determines local properties such as the charges and the

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

polarization, the solubility in a solvent, 103 the existence and structure of a hydration shell,104 the local affinity to surfaces, 105 or, in studies of polymer reactions, the monomer reactivity.1 , 106 In general, these properties are also influenced by the larger-scale structure of polymer systems. For example, the effective monomer reactivity depends on the accessibility of the reactive sites, which is determined not only by the local electronic and steric monomer structure but also by the polymer conforma- tion. 106,107 Likewise, the effective charges and/or polarization of monomers depend on the local environment. 108,109 In most cases, however, the corrections due to the larger-scale environment are small compared to the intrinsic value imposed by the monomer structure. To study polymers on the monomer scale, atomistic models are used, and in some cases quantum mechanical modeling is necessary.110,111

The next level of organization is the oligomer scale, i.e., the scale of short polymer sections and monomer-monomer interactions. On that scale, cooperativity effects due to nonbonded or bonded interactions between monomers start to become prominent and even dominate. Here and in the following, the term "nonbonded" refers to general interactions between monomers of given types, no matter whether or not they belong to the same molecule (e.g., electrostatic interactions or van der Waals interactions), and the "bonded" interactions subsume the additional interactions between monomers that are close neighbors in the molecule (e.g., chemical bonds, bending or torsional potentials). Emerging properties of interest in the oligomer scale are, e.g., the effective monomer-monomer incompatibility,"12 ion-specific effects, 113,114 the propensity to

crystallize, 19 or solvency/cosolvency and cononsolvency effects.114-120 Again, these properties also depend on the higher order organization, e.g., as has been discussed in the introduction for the case of crystallization. The modeling at this level is still often based on atomistic force fields, but chemically specific coarse-grained force fields such as the celebrated MARTINI model121 are starting to become useful; see also the recent review by Dhamankar and Webb.15 In such coarse-grained models, several atoms are lumped into one effective particle, and the (bonded and nonbonded) interactions between particles are determined either in a bottom-up fashion from atomistic simulations, in a top-down fashion from experimentally accessible data, or by a combination of the two. For an overview over coarse-graining approaches, we refer to the excellent review of Noid5 (see also below, section III.A.1).

## II.B. Polymer Scale: The Scale of Conformations



The third level, the polymer scale, is the realm of classical polymer physics, where generic statistical mechanics approaches have celebrated successes.18,122,123 At this level, scaling laws have scored victories, both regarding static and dynamic properties of polymeric systems, and simple calculations based on "scaling blobs"123,124 can make meaningful predictions. This is because polymer molecules consisting of many identical monomer units start to exhibit universal behavior beyond a certain molecular weight. Therefore, renormalization groups concepts can be applied, according to which the fractal large-scale structure of polymer conformations does not depend on details of the local monomer structure. This results in the paradigm of the "Gaussian chain model",18 which describes a polymer molecule as a random walk in space. In the case of complex heteropolymer molecules such as intrinsically disordered peptides (IDPs), applying scaling concepts is more challenging, but still at least partially successful.125-127 Theoretical models at this level are

mostly based on effective phenomenological parameters18 such as the Kuhn length, the famous Flory-Huggins x-parameters characterizing polymer-solvent or monomer-monomer inter- actions, the monomer mobility, the effective monomer charge, and possibly the Debye screening length.

A number of generic coarse-grained simulation models have been proposed already decades ago to study polymer properties at this level: Lattice models, where polymers are represented by random self-avoiding walks on a lattice, and off-lattice models, where polymers are modeled as chains of interacting hard-core spheres connected by springs. Among the most prominent models of this type is the bond fluctuation model, 128 a lattice model where monomers occupy cubes on a lattice and can be connected by a finite set of bonds, and the Kremer-Grest model, 12an off-lattice model that represents polymers as strings of hard-core spheres connected by nonlinear springs. Such models can be extended in various ways, e.g., to include bending potentials, 130,131 attractive nonbonded interactions,132 or (in the case of polymer solutions) a hydrodynamic coupling to a fluid medium. 133 They have been used to verify scaling predictions1 ,131,134 and to study generic aspects of single polymer phase transitions such as chain adsorption or the coil-globule transition 135-137 properties of polymer melts and blends138 and even dynamical transitions such as the glass transition. 139-141 To some extent, they can also be used to make quantitative predictions for chemically specific polymers. For example, recent work by Everaers and co-workers142 has shown that, for a wide range of commodity polymer melts, matching a single local property in melts of Kremer-Grest chains, the so-called dimensionless Kuhn number, is sufficient to reproduce the correct entanglement modulus. 142,143 The Kuhn number is derived from microscopic quantities, i.e., the number of Kuhn segments in a volume of Kuhn length cube. The entanglement modulus is roughly proportional to a macroscopic quantity, the plateau shear modulus. Hence this example shows how simulations of a properly matched generic polymer model can be used to predict important characteristics of polymer materials. Milner has recently proposed a universal scaling theory of entanglements for melts and solutions of chains with arbitrary flexibility,14* suggesting that similar approaches might also be successful for polymer solutions.

## II.C. Interacting Polymers: The Blob Scale



The properties of polymer systems containing many polymers are often determined by conformational restructuring on scales that are much larger than the monomeric scale. On such scales, polymers behave in many respect like single soft, inter- penetrating "blobs" or chains of such blobs. In polymer physics, the term blob often refers to a theoretical framework that allows for simple intuitive derivations of crossover phenomena between different scaling regimes in polymer solutions.123,124 Here we will use it more generally to describe the soft character of overlapping polymers.

In large-scale studies of interacting polymers, two novel classes of simulation models become increasingly popular that account for this soft character: Ultracoarse-grained particle- based models with soft potentials and density-based models. In soft potential models, coarse-grained units are assumed to represent lumps of a sufficiently large number of microscopic particles that they can interpenetrate each other. The non- bonded potentials are still described in terms of pair interactions between particles with positions 7; and 7;

30

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

ACS Polymers Au

ULL [i] = Σv,(i,;) i,j

(1)

possibly augmented by higher-order multibody potentials.145 However, the potentials do not diverge at 7; = 7). This is the case, for instance, for "dissipative particle dynamics" (DPD)- models145,146 or blob models. 147 -- 154

In contrast, in density-based models, 155-164 the nonbonded potentials are expressed as a functional of local number densities e(7) ={pa(7)} of coarse-grained monomer or solvent particles of type a, typically in the form of an integral over a "free energy density'

## Unble] = [dr f(F, g(F))



(2)

where the function f(7, p(7)) depends implicitly on 7 via p(7) and may have an additional explicit 7-dependence (e.g., to account for external potentials and confinement effects). In the bulk, it is often taken to have a local quadratic form, defined in terms of Flory-Huggins-like interaction parameters

2

f(p(F))

= Exapa (7) PB(F) +4|EP(F) - Po

kBT αβ

α

(3)

Here k gives the compressibility of the polymer solution or melt, and we have assumed for simplicity that the volume fraction per bead of all entities is the same. We should mention that, in practical simulations, the value of K is often reduced quite substantially compared to the real compressibility of polymers. This is done to avoid numerical instabilities and enable simulations with larger time steps.

To complete the definition of a density-based model, one must also specify how to determine the local densities Pa and how to formulate the corresponding spatially discretized version of the equations of motion. Often, the local densities are evaluated on a grid,155 but other off-lattice variants based on weighted densities have also been proposed.161,165 When using a grid-based model in dynamical simulations, a second practical issue is how to determine the resulting forces on monomers- whether to directly take the derivative of the discretized Hamiltonian with respect to the monomer positions 166,167 or whether to calculate a discretized force field and interpolate that. 159,164,168 The former strategy guarantees that the simulation is grounded on a well-defined Hamiltonian, but it introduces lattice artifacts. The latter strategy gives more freedom to reduce the lattice artifacts and (approximately) restore momentum conservation in molecular dynamics simulations, but it does not guarantee that one samples a rigorously defined statistical ensemble in the limit of zero time step. Thus, the former approach is better suited for studying the statistical mechanics of the system, and the latter for studying processes where hydrodynamics is important.

Equation 3 defines one of the simplest density-based models, but numerous extensions are possible to make the model more flexible. One can add higher order terms, 161,162 additional density fields that characterize, e.g., local orientation, 169,170 charges," - 171,172 and/or nonlocal terms. For example, electrostatic interactions can be included in eq 2 by including the energy density of the electrostatic field generated by the charge density , 173 distribution p(7') and the corresponding interaction terms."

Both soft-potential models and models with density-based potentials are particle-based and describe the polymers as

connected chains of explicit monomers. They differ from hard- core models only in the type of nonbonded interactions. Removing the hard excluded-volume interactions, however, has a fundamental consequence: It removes topological interactions, i.e., the chains can now cross each other. This significantly changes the dynamic properties of the coarse-grained models and, in some cases, even the static structure.

Most prominently, the conformations of strictly two-dimen- sional polymers in dense melt are radically different for overlapping and nonoverlapping polymers.174-179 The config- urations of overlapping polymers are rather open and the number of interchain contacts per monomer is roughly constant. In contrast, nonoverlapping polymers segregate from one another, and the number of contacts per monomer scales as N-3/8 with increasing chain length N. This is because most open configurations are forbidden due to excluded-volume inter- actions. This effect is independent of dynamics and also persists in Monte Carlo simulations that simply sample the phase space.

In higher dimensions, the fraction of actually forbidden conformations in phase space is negligible, and the effect of hard excluded-volume interactions is more subtle. In polymer networks (gels, elastomers), and in systems of closed (ring) polymers, topological constraints partition the phase space, since a large set of energetically allowed conformations cannot be accessed kinetically from a given start configuration: For instance, initially concatenated rings cannot be separated and initially separated rings cannot be concatenated. As a result, ring polymers in a melt of nonconcatenated polymers are more compact than linear polymers, and their size (radius of gyration) scales differently as a function of N.180 Capturing such effects with soft coarse-grained models is a formidable challenge. Narros et al.153 have proposed a hierarchical multiblob approach, where the direct interactions between soft blobs (coarse-grained monomers) are supplemented by additional interactions between the centers of mass that account for the effect of topological interactions in a statistical sense. With this approach, they could reproduce the shrinking of ring polymers in melts with the correct exponent. However, other character- istics of large ring polymers in ring polymer melt, e.g., the dominance of double-folded conformations with primitive tree structure ("lattice animals"), 181,182 are not captured. Interest- ingly, a recent comparison of simulation results using Kremer- Grest ring polymers with density functional calculations (which ignore topological constraints) has suggested that topological effects have no effect on the density profiles close to surfaces in sufficiently dense melts,183 although they do seem to affect the thickness of depletion regions in semidilute solutions.

In contrast to ring polymer melts, melts of linear polymers are ergodic in phase space and blob models can mostly account for their static structure, at least on large scales. On small scales, there are deviations. For example, models with soft potentials tend to overestimate the frequency of small knots, 184,185 in particular if the size of the excluded volume of monomers is comparable to that of the Kuhn segment.184 t.184 More importantly, they fail to reproduce their dynamics at large N which is characterized by entanglements between polymers as already discussed earlier:9,18,186 According to the classic reptation picture, polymers undergo an effective one-dimensional diffusion in a tube, which is created by their entanglements with other polymers. Polymers interacting with soft potentials, however, do not reptate. 188 Schieber18 and later Likhtman 190 have proposed an ingenious way to restore entanglements at the level of single-chain dynamics:9,191,192 They proposed to mimic

31

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

the effect of entanglements by virtual "slip links", discrete objects through which the chains must slip. This model has later been extended to multichain models where the slip links are fluctuating objects that connect different chains to each other.193-196 Such slip-link degrees of freedom introduce effective attractive interactions between polymers. However, the latter can be calculated analytically and subtracted from the basic potential function, e.g., eqs 1 or 2, to eliminate their effect on the static behavior. Wu et al. and Behbahani et al. have recently demonstrated the potential of multichain slip-link approaches in ultracoarse-grained simulations of real commod- ity polymers such as polyethylene,197 polystyrene,198 and polybutadiene187 (see Figure 1). Introducing slip links can also help to restore the correct elastic and rheological properties in soft-potential based models for elastomers. 199

(a) Atomistic: ...- CH2-CH=CH-CH2 -...

## (b) Moderate CG: ... {CH2-CH=CH-CH2 ...



(c) Slip-spring: .... (CH2-CH=CH-CH2)12) ...

Figure 1. Different levels of description of cis-1,4-polybutadiene (cPB) in ref 187. (a) United atom model. (b) Structurally coarse-grained model with hard core interactions. (c) Soft potential model with slip- links. The dynamical single- chain and viscoelastic properties can be mapped onto each other and are also in good agreement with experimental data. Reproduced from ref 187. Copyright 2021 American Chemical Society.

## II.D. Mesoscopic Scale: Transition to Field Theories



The next level is the scale of mesoscale organization, i.e., structure formation in inhomogeneous polymer systems. Emerging phenomena at this scale are the nucleation of crystallites in semicrystalline polymers,19 phase separation and demixing, wetting phenomena, or self-assembly.51

Apart from the coarse-grained particle-based polymer models with hard or soft interactions discussed in sections II.B and II.C, a new tool for investigating polymer systems on such scales are field-theoretic approaches. The most common starting

points for the derivation of such approaches are density-based models such as the one defined by eq 2. By field theoretic manipulations such as delta functional transformations204-206 or Hubbard-Stratonovich transformations, 201,207,208

one can re- write the partition function of this system as an integral over fluctuating real and imaginary fields. For example, the delta functional transformation of the model (eq 2) yields the 205 following expression for the partition function:2

Za f DW | Dp exp(-FlkBT) (4)

with

Fle, W] =fårf(7,p(7)/kgT-Efª,

kBT

Pa(F) W.(F) - Σ n; In (Q,/n;) j (5)

(in the canonical ensemble) where W(7) = {Wa(7)} denotes a vector of fluctuating imaginary auxiliary fields Wa(r), j sums over different polymer types, and Q,[W] is the single-chain partition functions of polymers of type j without nonbonded interactions in the fluctuating external field W(7).

Taking these expressions as a starting point, one can make several approximations: First, one can replace the integral (eq 4) by a saddle point approximation, which amounts to approximat- ing the free energy of the system by the extremum of F in eq 5. Remarkably, the extremum for W is not located on the original imaginary integration domain, but is purely real. The approximation results in the so-called self-consistent field (SCF) theory, 205,206,209 one of the most powerful mean-field approximation for inhomogeneous polymer systems, which can often predict real interfacial structures in polymers at an almost quantitative level.206 Figuratively speaking, the SCF theory describes polymer systems as assemblies of independent chains, each in the ensemble-averaged field of the surrounding chains. The averaging approximation is good if chains interact with many other chains, which is true for chains of high molecular weight since they overlap with each other. In three-dimensional melts of linear polymers, the degree of interchain interactions can be characterized by the so-called invariant polymerization index N = b6Po N, where b is the statistical segment length, and N is the number of segments in a polymer chain. For N -> co, the SCF approximation becomes exact. Experimentally relevant values of N are of order 102-104.

A second approximation to eq 4 consists of applying a partial saddle point approximation with respect to the auxiliary fields Wa(7) only. Thus, the functional Flp, W] is extremized with respect to W, giving self-consistent equations for W[e ], which have, again, a real solution W(7). This procedure turns F into a real-valued density functional F[p]. It serves as starting point for dynamic mean field theories of polymers which have the structure of continuum theories but retain some knowledge of the macromolecular architecture of polymers. The simplest Ansatz of this kind is the purely diffusive equation of motion 210-221

Op (F, t) = V, | d'r A(F, F')V, u (F', t) (6)

with H(7, t) = 8F|8pa (7, t). In the context of the Hohen- berg-Halperin classification222 of dynamic critical phenomena (see section II.E), eq 6 corresponds to so-called "model B"

32

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

## ACS Polymers Au



a)

b)

c)

1.6

17

O

Tau density

q1ª1

1.2

One-phase

dilute

le-07

O

le-06

O

Two-phase coexistence

One-phase dense

O-O Tau SC :unselected:

0.8

O O Tau-RNA CC

le-08

0.0001

1

pb3

Figure 2. Coarse-grained simulations of liquid-liquid phase separated droplets of tau proteins.200 (a) Particle-based CG model using a Kremer-Grest type representation of chains. (b) FTS model, studied by Complex Langevin simulations. (c) Phase diagram obtained from FTS simulations as a function of Bjerrum length lp and tau-density p rescaled with the statistical segment length b (blue curve). The red curve shows the corresponding phase diagram for mixtures of Tau and RNA. Adapted with permission from ref 200. Copyright 2021 John Wiley and Sons.

dynamics. The mobility matrix function A(7,7') = {AaB(7,7')} describes the motion of monomers at position r in response to a a local thermodynamic force (-V,u(7',t)) and may be nonlocal to account for the effect of chain connectivity. Possible extensions include the coupling to equations of fluid dynamics in order to account for hydrodynamics, the inclusion of additional order parameters to account for local chain ordering,227 or the introduction of a time-delayed response functions to account for memory.228,229

Going beyond the mean-field approximation, field-theoretic simulations (FTS), aim at sampling the full partition function (eq 4). The field of FTS is relatively new and, so far, restricted to static simulations. An important problem that needs to be overcome is dealing with the imaginary integration domain of W in the integral (eq 4). Since the Wa(7) are imaginary, the "action" F in eq 5 is a complex, rapidly oscillating quantity, which leads to a sign problem. Pioneered by Ganesan and Fredrickson,230 one approach to overcoming this problem is to use the so-called "Complex Langevin" simulation method, which involves solving Langevin equations in the entire complex plane, in the case of eq 4 for both the W and 2 degrees of freedom.

If the underlying nonbonded potential functional is a quadratic functional of the densities pr) as, e.g., in eq 5, one can reduce the number of fluctuating fields by a factor of 2 by applying a Hubbard-Stratonovich transformation instead of a delta functional transformation, which significantly reduces the computational costs. Complex Langevin simulations based on this approach have been used by Fredrickson and co-workers and other groups to study, among other, fluctuation effects in diblock copolymer phase diagrams, 202,230 polymer nano- composites,231 polyelectrolyte complexation,202 and liquid- liquid phase separation of intrinsically disordered pro- teins.200,232Figure 2 shows a FTS simulation droplets formed from tau proteins, strong polyampholytes which undergo liquid-liquid phase separation due to self-coacervation.

In dense melts of polymers containing only two types of monomers A and B, a second approach becomes possi- ble, 203,217,218,233-238 which has been applied with considerable success by Matsen and co-workers to study block copolymer systems:235 In that case, the Hubbard-Stratonovich trans- formation results in a functional integral over two fluctuating fields, an imaginary one which can be associated with density fluctuations and a real one which describes the composition fluctuations. In nearly incompressible melts, the density

fluctuations have little influence on the composition fluctuations that determine the phase behavior. Therefore, one may apply a partial saddle point approximation regarding the density fluctuations only, and obtains a purely real fluctuating field theory, which can be treated, e.g., by standard Monte Carlo methods. Comparisons with Complex Langevin simula- tions236,239 have shown that the partial saddle point approx- imation is indeed accurate in dense melts. The advantage of the approach is that it allows more easily to access highly incompressible melts at experimentally relevant polymerization indices.203

In many cases, fluctuation corrections mainly shift phase transition temperatures or change the order of a transition from second order to weakly first order, but there are situations where they may fundamentally change the properties of a system. One prominent example is the "microemulsion channel" in balanced mixtures of A,B homopolymers and A:B diblock copolymers. Upon increasing xN, SCF calculations predict a demixing transition at low copolymer content, and an ordering transition to a periodic lamellar phase at high copolymer content. According to the SCF theory, both transitions meet at a so- called "Lifshitz critical point", where the lamellar thickness of the periodic phase diverges. In reality, generic theoretical consid- erations240 suggest that the Lifshitz critical point has a lower critical dimension of four, meaning that fluctuations will invariably destroy it in three (or fewer) dimensions. The fate of the Lifshitz point in lower dimensions has long remained unclear, but was recently revealed by field-theoretic simulations of Vorselaers, Spencer, and Matsen:233,234 It splits up into a critical end point and a tricritical point (see Figure 3). This example also demonstrates how simulations of polymer systems can give insights onto fundamental questions in statistical mechanics.

## II.E. Macroscopic Scale: The Engineering Scale



Finally, at the macroscopic level, the focus lies on properties of polymeric materials that are of direct interest for engineers: Mechanical stability, microstructure, stress distribution, viscoe- lasticity, constitutive relations, and aging phenomena. Emerging phenomena that are studied on such scales are, for instance, polymeric flow patterns in complex geometries242 but also inherently inhomogeneous processes such as viscoelastic phase 243 foaming, 244,245 'or crack formation.246 On macro- separation,45 scopic scales, materials are described by a set of characteristic

33

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

## ACS Polymers Au



2.6

A+B

2.4

A+B+L 1 L

UNX

A+B+BuE

2.2

disordered

2.0 0.00 0.04

0.08

0.12 0.16

Figure 3. Fluctuation effects on the Lifshitz point in the phase diagram of ternary A/B/AB homopolymer/diblock melts, as revealed by field- theoretic simulations in refs 233 and 234. Dashed line shows mean-field result, symbols connected by solid lines show the simulation results. Reprinted with permission under a Creative Commons CC BY 4.0 License from ref 235. Copyright 2021, Matsen/Beardsley.

continuous fields and corresponding transport equations. They are typically constructed somewhat heuristically based on general symmetry considerations and conservation laws, following the spirit of the famous Hohenberg-Halperin classification of dynamic critical phenomena.222 For example, so-called "model A" dynamics is used to describe relaxation processes where conservation laws are not important, "model B" dynamics is used to describe diffusive processes where only the local conservation of one "order parameter" (e.g., the polymer volume fraction) matters (an example is eq 6), "model C" dynamics describes processes where other conserved mass densities also become important, and "model H" additionally accounts for local momentum conservation and convection in order to describe stress, flow, and hydrodynamic phenomena.

It should be noted that continuum models are much less transferable than lower level models. Above the glass transition, cross-linked polymer networks are best described by elasticity theories, using displacement fields as primary field variables (e.g., refs 247, 248), and constitutive equations that establish a relation between the stress tensor and the strain tensor. In contrast, fluids of un-cross-linked polymers are described by hydrodynamic models in terms of flow fields, and constitutive equations relate the stress tensor with the strain rate tensor. Below the glass transition, polymer materials behave like solids, but plastic flow is also possible in response to high stresses. This can be addressed by distinguishing between reversible elastic deformations and irreversible plastic deformations.249-252 Even within the realm of continuum models, multiscale techniques are still necessary to bridge between micromechanical models as discussed here and mechanical models that describe objects made of polymers on truly macroscopic scales.253,254

In the following, we will focus on models for polymeric fluids. These often combine a hydrodynamic description with a simplified microscopic model for viscoelasticity, in order to account both for flow and internal relaxation processes. An important tool in the construction of such models is the so- called convected derivative, a concept originally introduced by Oldroyd:255 It describes convection with respect to a "material frame" of comoving material particles and thus in some sense generalizes the substantial derivatives in fluid dynamics to tensorial quantities. To explain the convected derivative, we first recapitulate the idea of the substantial derivative, which is a standard concept in fluid mechanics: Consider a fluid flow

characterized by a flow field ū(7, t) carrying a scalar field @(7, t). Let @(L)(7, t) be the corresponding scalar field in the comoving (Lagrangian) frame with @(7,0) = @(L)(7,0). The substantial derivative is defined such that it describes the evolution of the scalar field @(7, t) = @(L)(7 - ut, t) in the comoving frame, i.e.,

CP := OP(L) = OP + (u.V)@

(7)

When generalizing this concept to tensorial fields Q(7, t) (or Q;(7, t) in coordinate notation), following Oldroyd, one must take into account the deformations of the coordinates of Q in the comoving frame. They are determined by the deformation rate field G = Vu (or Gij = 0;u; in coordinate notation). As before, we choose Q(7, 0) = Q(L)(7,0) . For contravariant tensors Q, the relation between Q and Q(L) in the limit t -> 0 is then given by Q(7, t) = (1 + GT t)Q(L)(7 - ut, t)(1 + Gt). This motivates the definition of the upper convected derivative

Q := a,Q(L) = a,Q + (u. V)Q- GTQ- QG (8)

The corresponding consideration for covariant tensors yields the lower convected derivative

## Q := OQ + (ū . V)Q + GTQ + QG



(9)

The concept of convective derivatives provides a framework for deriving constitutive relations in viscoelastic materials in a geometrically consistent manner. For example, the so-called upper convected Maxwell model

0 + À0 = 2nD (10)

with D = (1/2)(G + GT) describes a material with a linear steady-state stress-strain relation @ steady = 2nD, where the stress tensor, o, relaxes in a simple exponential manner toward its steady-state value with relaxation time 1.

More sophisticated viscoelastic models are typically based on one of two approaches:10 Either they use phenomenological considerations to construct more complicated expressions for the relaxation of the stress tensor and/or its steady-state value, or they select a simplified molecular model for the polymers and use kinetic theory to derive approximate expressions for the stress tensor. One popular starting point of the second kind is to consider a Newtonian fluid filled with noninteracting elastic dumbbells, i.e., two beads connected by "Finitely Extensible Nonlinear Elastic" (FENE) springs, with a spring constant k(R) that diverges if the distance R of the beads exceeds a limiting value. A Fokker-Planck equation for the conformation of the dumbbells is then coupled to the Navier-Stokes equations via two convective contributions to the Fokker-Planck equation (one for the center of mass and one for the relative distance of beads) and an extra stress term in the Navier-Stokes equations. Many macroscopic models for polymer fluids can be seen as approximations to this FENE model. The most prominent one is the Oldroyd-B model, one of the first models for polymer fluids,255 which replaces the FENE spring by a regular linear Hookean spring.250 This simplifies the mathematical analysis, however, it leads to unphysical singularities under certain flow conditions where the dumbbells stretch to infinity. Another approximation is the Peterlin model (FENE-P), where the nonlinear spring constant k(R) is replaced by an averaged value k({R).257,258

In order to avoid mistakes when constructing such models, considerable care has to be taken to ensure that they are thermodynamically consistent. Several mathematical

34

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

ACS Polymers Au

Time: 20 20

Time: 80

0.4004

0.4002

## 20 -



## 15 -



N

10 -

5.

0

20

15

10

5 20

x

- 0.4

0.3998

0.3996

20

15

₦

10

5

20

15

0.3994 0

0

5

10

15

y

0.3992

10

5

x

0

Time: 130

0.41

0.4

0.39

20

0.5

0.45

0.38

15~

- 0.4

0.35

0.37

N

10 .

0.36

5

0.35

0

20

0.33

0.3

0 0.34

5

0

0.25

10

15

y

15

10

20

0

Time: 200

Time: 320

0.8

x

5

0

5

10

15

20

y

0.2

Time: 500

0.8

0.8

0.7

- 0.7

20

0.6

15

N

0.5

10

0.7

20

0.6

15

N

10

- 0.5

5

0.4

20

- 0.6

15~

N

10

0.5

5

0.4

0

20

15

10

5 20

x

0

0.3

5

10

15

C

y

0.2

0

20

15

10

5

x

5.

- 0.4

0

0.3

0

0.3

5

10

15

y

0.2

0

20

15

10

5

x

5

10

15

y

0.2

20

0

20

0

Figure 4. Spinodal phase separation in a continuous viscoelastic model (similar to Figure 1 in ref 241). The numerical simulation is based on a Lagrange-Galerkin finite element method. Courtesy of M. Lukácová-Medviďová.

frameworks have been developed which help to enforce consistency, the most rigorous being the GENERIC framework that makes a strict distinction between antisymmetric reversible and symmetric irreversible (dissipative) contributions to the dynamical equations.261 It should be noted that not all published macroscopic models are thermodynamically consistent. Schieb- er and Cordoba have recently developed a simplified set of requirements that allows one to perform basic consistency tests without having to apply the full GENERIC machinery.260 Another, even more difficult, question is to prove that the models actually have solutions for arbitrary initial conditions. Global existence results for weak solutions of the Peterlin model have recently been obtained by Masmoudi256 and, regarding a class of generalized Peterlin models, by Lukácová-Medviď'ová et al.262,263

The study of inhomogeneous polymer solutions is particular challenging due to the vastly different mobilities of polymer and solvent molecules. Quite generally, large dynamical asymmetries between components of a demixing system often result in unconventional network-like pattern formation and novel dynamic scaling exponents204 compared to standard model B or model H demixing, because the domains of the slow phase tend to behave like viscoelastic objects. This phenomenon was first discovered by Tanaka in 1993205 who termed it "viscoelastic phase separation", and it is still a subject of active research.243,266-271 Theoretical models typically build on the two-fluid model proposed by Doi and Onuki272 and Milner,273 which include a coupling between elastic stress and concen- tration. Based on this idea, Zhou et al. proposed a number of

phenomenological models for viscoelastic phase separation, paying particular attention to thermodynamic consistency.269 Spiller et al.270 have recently taken the kinetic approach and derived a two-fluid model for solutions of Hookian dumbbells which is consistent with the GENERIC formalism. Brunk and co-workers have analyzed a number of models for viscoelastic phase separation from a mathematical point of view and proved the existence of weak solutions. 241,271,274 An example of a numerical simulation of one of their models is shown in Figure 4.

## III. SCALE-BRIDGING STRATEGIES



In the previous section, we have discussed the hierarchy of models that have been designed and used to study polymeric systems on different scales. In many cases, however, using a single model is not sufficient to fully characterize a material of interest. Thus, multiscale modeling techniques must be applied, which combine different scales in one simulation, or at least establish quantitative connections between different scales. The key to multiscale modeling is coarse-graining, i.e., the art of designing high-level models with few degrees of freedom ("coarse-grained (CG) models") that capture the essential features of an underlying "fine-grained (FG)" system.

Classical coarse-graining strategies traditionally follow one of two philosophies:5 "Top-down" CG models are designed based on physical intuition without direct input from FG simulations. Examples are generic top-down models such as the bond fluctuation model128 128 and the Kremer-Grest model129 discussed in section II.B, which are used to study generic properties of polymer systems, but also chemically specific top-down models

35

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

such as the MARTINI model, 121 which use experimental information such as solubility parameters to match interaction parameters. In contrast, "bottom-up" CG models are con- structed from FG simulations in a systematic manner such that they capture certain structural or thermodynamic properties of interest. This is strategy is commonly adopted to derive classical atomistic force fields from electronic structure calculations, and it is also used to construct higher-level models. In addition to bottom-up and top-down approaches, hybrid approaches are becoming increasingly popular that integrate information from different sources-FG simulations as well as experiments275-278 and data-driven methods that apply machine-learning meth- ods. 15,102,278

Numerous coarse-graining and scale-bridging strategies have been proposed over the past decades (see refs 4-8, 10, 12, and 14-16 for review articles), and giving a comprehensive overview is beyond the scope of the present Perspective. Instead we will give a very personal view on different aspects of the coarse- graining problem with a focus on bottom-up coarse-graining, on lessons learned from the past, and challenges for the future.

Formally, defining the coarse-graining task seems quite obvious: Given a microscopic dynamical system with N degrees of freedom and corresponding equations of motion, define a reduced set of n representative collective variables and derive their dynamical equations from those of the microscopic system. This idea is old, and projection operator techniques to derive coarse-grained equations have been proposed already in the 1960s by Zwanzig and Mori.2 They were used, among others, to derive equations of fluctuating hydrodynamics for simple and complex fluids. 282,283 In recent years, the Mori- Zwanzig formalism has attracted increasing interest in the coarse-graining community, mostly thanks to the work of Español and co-workers who promoted it as a practical tool to construct, e.g., dynamic density functional theories284 or particle-based DPD models.285 In principle, projection oper- ators allow one to derive exact dynamical equations for the chosen coarse-grained variables. However, these are complex integro-differential equations that cannot be reduced to practically useful model equations, e.g. stochastic equations, without substantial further approximations. Even more seriously, Glatzel and Schilling have recently argued that the dynamic equations for the coarse-grained variables A¡(t) cannot necessarily be related to a potential of mean force17,286 U[ A]. Their claim is consistent with a discussion by Zwanzig in ref 287, who pointed out that the memory kernel in the linear Mori- Zwanzig equations absorbs some of the nonlinearities of a nonlinear conservative potential in the FG equations. Unfortu- nately, this implies that the resulting CGmodels are not necessarily compatible with the GENERIC framework201 and its clear distinction between external driving forces, conservative interactions, and dissipative forces. As discussed earlier, the GENERIC structure helps to enforce thermodynamic con- sistency and ensure, by construction, that violations of the second law of thermodynamics are not possible in a CG model. Giving up this structure thus represents a serious drawback. Luckily, recent work by Vroyland and Monmarché suggests a possible way out of this dilemma. Using the Mori -- Zwanzig formalism and considering a single CG particle, they showed that it is possible to derive a GLE that complies with the GENERIC structure, if one allows for position dependent memory kernels. 288

One may be tempted to set aside these problems and design CG models that primarily target static equilibrium properties.

One can then use the partition function of the microscopic system as the starting point and integrate out the N microscopic degrees of freedom while constraining the n CG variables, which directly gives a "potential of mean force" or "free energy landscape" U[A ]. In general, however, simple analytic expressions for U[A]] are not available, such that a simulation of the exact CG model is as expensive, from a computational point of few, as the simulation of the FG model. Thus, further approximations must again be made such as, e.g., rewriting U[A;] as a sum of effective pair or low order multibody potentials.

Finally, already the identification of meaningful coarse- grained variables represents a challenge in itself-in particular if the coarse-grained model is expected to capture several very different aspects of the underlying FG model. This leads to the well-known problem of representability: A CG model that reproduces the structure of the FG model does not necessarily have the correct thermal properties and vice versa. Moreover, a CG model that was constructed for one state point (e.g., one density), not necessarily captures the properties of the FG model at another state point (another density). The latter so-called transferability issue will obviously cause problems when using CG models for studying strongly inhomogeneous systems.

In sum, coarse-graining is bound to be a somewhat "dirty" business. This is a direct consequence of the famous "no free lunch" theorem": Unfortunately, it is not possible to simplify a complex problem just by rewriting it in terms of fewer variables. Coarse-graining is effectively an optimization problem which requires many compromises and a high level of physical and chemical intuition. The coarse-graining philosophy rests on the assumption that the large-scale structure of materials can be understood without explicit knowledge of microscopic details. In the case of polymers, one hopes that this assumption is justified due to their repetitive molecular structure, the high level of conformational disorder, and the dominant role of entropy.

We will now discuss selected aspects of coarse-graining in polymeric systems or, more generally, soft matter systems.

## III.A. Static Coarse-Graining



III.A.1. Structure-Based Coarse-Graining. Structure- based coarse-graining techniques are typically used to design particle-based CG models with the goal to reproduce structural properties of the FG system such as spatial correlation functions. The CG variables are the positions R of CG particles, and the optimization task consists in finding the best approximation for the free energy landscape U[R]] or the configuration dependent force field F,[R] in the phase space of the CG variables. Regarding equilibrium static coarse-graining, the field is already quite advanced. The CG bonded interactions can be calculated in a straightforward manner by sampling, e.g., bond length and bond angle distributions in small reference simulations. To determine nonbonded CG interactions, researchers can use the open-source package VOTCA289 (www.votca.org) and select between a range of established methods5, such as inverse Monte Carlo (IMC), iterative Boltzmann inversion (IBI),291-295 force matching (FM),296-300 or relative entropy (RE) minimization between the CG and the FG distribution.301 Alternatively, they can employ the framework of the generalized Yvon-Born-Green (g-YBG), 302-304 or use artificial neural networks. 102,305,306 Noid and co-workers have pointed out that the quality of nonbonded CG force fields can be greatly improved if one distinguishes between CG monomers that have different local connectivities within a molecule, 307,308 e.g., between middle and end segments.

36

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

One paradigmatic problem in structural coarse-graining is to construct pair potentials from radial distribution functions (RDFs) of particles as determined, e.g., from FG simulations. This is known as the inverse Henderson problem. As proved in 1974 by Henderson for finite systems with fixed particle number310 and very recently by Frommer et al.311,312 for the thermodynamic limit, the problem has a unique solution for a rich class of interaction potentials which includes, among other the so-called Lennard-Jones type potentials.313 Nevertheless, the problem is ill-posed in the sense that a small noise in the RDF can lead to large changes in the potentials. In other words, quite dissimilar potentials can produce almost identical RDFs309,314 (see also Figure 5). This opens possibilities to optimize pair potentials not only with respect to structural properties, but also to other properties as well. Building on this idea, Hanke and co- workers have recently developed novel integral equation-based methods that allow one to solve the inverse Henderson problem with additional constraints, 315,316 such that the resulting CG model reproduces both the structural correlations and the

a) 3,5

3

2,5

2

U(r) or g(r) [a.u.]

1,5

- Uref true potential U50 (50 IBI steps) U300 (300 IBI steps) - - RDFref target RDF50 (50 IBI steps)

-- RDF300 (300 IBI steps)

1

0,5

0

-0,5

-0.2

0,4 0,6

0,8

r [a.u.]

b)

3

2,5

2

- Uref true

- - RDFref target

- UIBI (IBI)

- - RDFIBI (IBI)

- UIMC (IMC) - - RDFIMC (IMC)

1,5

U(r) or g(r) [a.u.]

0,5

0

-0,5

-1

0,4

0,6

0,8

r [a.u.]

Figure 5. Uncertainties in the reconstruction of pair potentials from pair correlation function, see also.309 In this example, the target RDF is taken from simulations of a binary Lennard-Jones mixture; hence, the true potential (black solid line) is well-known. Solid lines show potentials as indicated, and dashed lines with the same color for the RDFs obtained with the same potential. (a) IBI results after 50 and 300 iterations (green and blue). (b) Final results obtained with an IBI variant (red) and with IMC (green). The true potential is best reconstructed with the IMC method. All potentials, however, yield RDFs that are almost indistinguishable from the target RDF. Data provided by David Rosenberger.

thermodynamic properties of the microscopic system.316 When applying such methods, one should keep in mind that the RDFs obtained from FG simulations may suffer from finite-size effects. Cortes-Huerto and co-workers have recently investigated this in the context of Kirkwood-Buff integrals317,318 and proposed expressions for finite-size corrections in liquid solutions.51/ In the presence of elastic interactions, finite size effects persist even in large systems and extrapolation procedures must be applied.319,320

An interesting alternative way of dealing with the represent- ability problem has been proposed by Lebold and Noid.321,322 Rather than trying to find one CG model that captures both the energetics and the structure of the FG model, they suggest to explicitly keep track of energetic and entropic contributions to the potential of mean force321,322 in the CG simulation. Thus, the effective potential is split up as

## U[R]] = Uw[R]] - TSw[R]



(11)

where Uw is constructed such that it gives, on average, the energy of the fine-grained system with collective variables constrained to RÅ. The potential U is obtained by standard structural coarse-graining methods, and the potential Uw is determined using a minimization method similar to least- squares fitting. When analyzing CG simulation trajectories, the potential Uw can then be used to calculate observables that depend on energy. As a side effect, this approach also allows one to estimate the expected change in the potential of mean force at a different temperature with remarkable accuracy.522 Among others, it could be used to overcome sampling problems in the microscopic reference system, e.g., close to a glass transition.323

Going beyond pure pair potentials, higher-order multibody potentials 324-328 or density-dependent potentials329-338 offer additional flexibility which can be exploited to develop CG models with improved transferability properties.339 339 In particular, density-dependent potentials provide a comparatively straight- forward way of accounting for the local environment of interacting CG particles that may undergo liquid-vapor phase separation, n,340 and they are quite popular in empirical models with soft potentials such as (many-body) DPD145 or models with density-based interactions.165 Such empirical soft potential models are often set up as a sum of two contributions: Local density-dependent repulsive interactions between particles that account for the effect of excluded volume interactions, and density-independent attractive interactions that account for cohesion. The functional form of the two terms is usually postulated, but they can also be derived in a bottom-up fashion from FG simulations, e.g., by a combination of force matching and relative entropy minimization. 336,338 Since one has some freedom how to distribute the forces between different contributions, the results are not unique;336 they depend on the coarse-graining procedure. This gives freedom which can be exploited to further optimize the potentials with respect to representability and transferability.

We should note that density-dependent potentials also have interesting applications beyond liquid-vapor systems, e.g., in ultracoarse-grained descriptions of compressible fluids or in coarse-grained descriptions of responsive materials where the shape of CG particles depends on their local environment.341

In other situations where local orientations of molecules or monomers are important, it might be desirable to include multibody potentials342 that also depend on the local conformation, such as three-body Stillinger-Weber type potentials that depend on the local angles between the

37

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

interaction sites. 324,343,344 Scherer, Andrienko, and co-workers have developed systematic ways to derive such potential, either by force matching327 or by using kernel-based machine learning with covariant meshing in order to account for inherent symmetries.345 So far, this has only been applied for small molecules, but it also offers interesting perspectives for simulations of, e.g., semicrystalline polymers.

An alternative way of parametrizing strongly configuration dependent effective interaction potentials has recently been developed by Bereau and Rudzinski.346,347 Their idea is to use different CG force fields for different regions in (local) configurational space, and interpolate ("hop") between them depending on the current state of the system. This multisurface concept, borrowed from models for electronic transitions, allows for a much better local optimization of force fields without having to resort to complicated force field parametrizations. As a nice side effect, potential barriers can also be represented much more accurately, which greatly improves the dynamic properties of the system. A related "multiconfigurational" concept designed to capture conformational chain transitions and their effect on potentials of mean force has been proposed by Sharp et al.348

III.A.2. Thermodynamics-Based Coarse-Graining. The coarse-graining approaches discussed in the previous section yield CG models that capture structural properties of the FG reference system such as pair correlation functions or statistical averages of mechanical force fields. From a multiscale point of view, it might often be more interesting to capture thermodynamic properties such as the equation of state (the density), the compressibility or more generally, high-wavelength structure factors, solubility parameters, interfacial tensions and surface tensions. Thermodynamics-based CG strategies are popular in top-down coarse-graining, as they use thermody- namic quantities as input which are more easily accessible in experiments. Typically, a certain functional form of potentials is assumed, and the parameters are matched such that the CG model reproduces the desired thermodynamic properties. For example, van der Haven et al.349 have recently derived a very accurate approximate closed-form expression for the coexistence phase diagrams of binary polymeric mixtures in DPD models with pair interactions, which allows to directly relate the soft DPD interaction parameters with experimental data on demixing phase behavior.

Thermodynamics-based coarse-graining is also the most natural approach when designing field-based continuum models or extremely CG models with soft potentials such as DPD or density-based potentials. As we have discussed above, density- based models and field-based continuum models are closely related to each other. There also exists a direct connection between DPD and continuum mechanics: For simple fluids, Español and Revenga have introduced a variant of DPD, 350 termed "smoothed dissipative particle dynamics" (sDPD), which is entirely constructed from thermodynamic properties and can be seen as a Lagrangian solver for the fluctuating Navier-Stokes equations.

When constructing ultracoarse-grained models, one must again distinguish between bonded and nonbonded potentials. Bonded potentials can be determined in a structure-based manner as described in section III.A.1. On large scales, when studying polymers of large molecular weight, it is often sufficient to use simple chain models such as the discrete or continuous Gaussian chain model,18 which requires matching only one parameter (the Kuhn length for given number of Kuhn segments)351 to the average conformational properties of the

chains in the reference system. Determining nonbonded interactions is more difficult, as standard density-based potentials or interaction terms in field-based models (eqs 2 and 5) are typically framed in a thermodynamic language in terms of compressibilities, Flory-Huggins x parameters (eq 3) etc.

Specifically, mapping x parameters still represents an outstanding challenge. Field-theoretic models typically assume that it describes the effective nonbonded interactions between CG polymer segments and is independent of local composition, chain length, and chain architecture. This picture is clearly greatly simplified and it has long been unclear whether the concept of a purely monomer-based x parameters is at all reasonable. Luckily, recent work by Morse, Matsen and co- workers235,352,353 on diblock copolymer melts suggests that this is probably the case, at least for dense polymer melts, due to a universality in the phase behavior of polymers with large molecular weight. They proposed to determine the x parameter in diblock copolymer melts by fitting the collective structure factor in the disordered state of symmetric diblock copolymer (BCP) melts to accurate theoretical predictions of a renormalized theory that accounts for the effect of fluctuations and finite chain lengths.354 Using this top-down mapping method, they were able to quantitatively reproduce the location of the order-disorder transition (ODT) in BCP melts of a number of particle-based models 352,354 and also experimental systems353 after accounting for the effect of polydispersity. Building on this insight, Willis et al.355 proposed as alternative approach to directly use the ODT for mapping x after correcting for effects of polydispersity and compositional asymmetry. Reanalyzing published experimental data, they mapped x(T) onto the functional form

x(I) =A + B (12)

where A subsumes enthalpic and B entropic contributions to the effective segment interactions, and extracted values of A and B for 19 different chemical pairs.

The x-calibration scheme of Morse and co-workers relies on the existence of accurate theoretical predictions for the structure and phase behavior of diblock copolymer melts. When looking at more complex systems, such predictions are usually not available, and less accurate mapping procedures must be adopted. Theories of the x-parameter have a long history, see, e.g., refs 356-364 (the list is far from complete). Practical mapping schemes for determining effective x-parameters have been proposed already 30 years ago by Müller and co-

workers365,366 and applied successfully to lattice models for polymer mixtures. In cases where the factors contributing to the x-parameter are mainly enthalpic, Müller and Binder proposed, as a simple prescription, to determine an "effective coordination number" from interchain correlation functions, .36 which replaces the coordination number in the original Flory-Huggins theory.367,368 Müller also devised a scheme to obtain additional entropic contributions from independent studies of the equation of state in "athermal" systems, where enthalpic interactions have been switched off.366 More recently, a number of heuristic schemes for matching Flory-Huggins type interaction param- eters have been proposed by De Nicola and co-workers, 369,370 that rely on either matching energies with CG off-lattice models309 or adjusting conformational properties of homopol- ymers in solution.370 Ledum et al. have developed a machine- learning protocol for optimizing such parameters with respect to

38

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

## ACS Polymers Au



arbitrary target quantities, e.g., density profiles.371 Sherck et al.372 and Weyman et al.373 have recently developed systematic bottom-up coarse-graining strategies for deriving field-based models with nonbonded monomer interactions that are not restricted to the Flory-Huggins form (eq 3). Their idea is to proceed in two steps. In the first step, a CG particle-based with soft pair potentials of given functional form is determined from reference simulations of a microscopic model, e.g., by relative entropy minimization3/2 or by matching the RDF. The second step is a Hubbard-Stratonovich transformation that turns the particle model into an auxiliary field model, which can then be studied by field-theoretical simulations. The second step involves an inversion of the pair potential in Fourier space, which restricts the class of potentials for which the approach can be applied.373 In particular, the inversion is not possible for hard core potentials, therefore the first step is essential and cannot be omitted. The latter still remains true if one replaces the Hubbard-Stratonovich transformation by a delta functional transformation in order to obtain a field theory of the type of eqs 4 and 5. Such an approach would give additional flexibility because higher order multibody interactions can be in- cluded.145,161,162 The underlying density-based potential does not have to be an integral over a local free energy density f(7,e), it could also describe nonlocal interactions as, e.g., in

1

U

2

3

3

r r r

r V

( r

r )

(13)

however, the integral over VaB(7) still needs to exist and be finite. We should note that, strictly speaking, the bottom-up approaches of Sherck et al. and Weyman et al. use ideas taken from structural coarse-graining. Nevertheless, the resulting CG models do not capture local structural properties such as packing effects, hence they are closer to thermodynamically CG models than to structurally CG models.

Compared to structural coarse-graining, one disadvantage of thermodynamics-based coarse-graining is that one loses the direct connection between mechanical forces in the CG and the FG system. Since forces drive the dynamics, it becomes more difficult to restore the correct dynamical properties without further adjustments. Indeed, recent studies on ionic liquids374 have suggested that structure-based CG models tend to have a more consistent dynamical behavior than thermodynamically CG models, e.g., regarding the relative mobility of anions and cations. We will specifically discuss issues of dynamic coarse- graining in the next section. Thermodynamics-based coarse- graining also becomes questionable in systems far from equilibrium, e.g., in active fluids. One should note, however, that many structure-based coarse-graining techniques are also no longer applicable for such systems, as most of them-with the exception of force matching-assume local thermodynamic equilibrium: They assume local configurations to be Boltzmann distributed in subvolumes of size comparable to the correlation length.

## III.B. Dynamic Coarse-Graining



The most common approach to studying dynamical properties in CG simulations is to use the free energy landscape obtained from a static equilibrium coarse-graining procedure as an effective interaction potential in molecular dynamics (MD) simulations. This approach can be quite successful if one accounts for a few side effects of structural coarse-graining: First, as known from the Mori-Zwanzig formalism287 integrating out degrees of freedom invariably introduces friction terms and

stochastic noise terms in the CG dynamical equations. In a standard MD simulation, these friction terms are disregarded, which accelerates the dynamics. Second, CG free energy landscapes are typically smoother than atomistic ones, which further reduces the direct friction between CG particles. As a result, coarse-graining reduces the separation between originally highly disparate time scales such as, e.g., the inertial and the diffusive time scales (the telescope effect),375 and accelerates slower dynamical processes.

From the point of view of time bridging, both the speedup and the telescoping are beneficial, as they allow one to access later time scales in CG simulations376 and study processes on different time scales simultaneously in one simulation. One of the earliest9% and still widely and successfully used approaches to dynamic coarse-graining has been to simply take advantage of this effect, determine the speedup factor of the process of interest, and use this to map the CG dynamics on real dynamics, 377-382 taking into account that the speedup factor might be different for different processes and/or compo- nents. 380 However, care must be taken that the speedup does not change the order of "faster" and "slower" processes and which might change dynamical pathways, particularly in dynamically asymmetric systems. This defines the problem of dynamic consistency.12

As already discussed in the previous section, one key to reducing the dynamic consistency problem is accurate structural coarse-graining, as it helps to recover consistent dynamics even in standard MD simulations, i.e., consistent barrier crossing dynamics and consistent relative speedup.346,374 In fact, using kinetic information as additional input for the parametrization of coarse-grained force fields may improve their quality, 383,384 because it gives more weight to transitional conformations, which are typically not well sampled in standard coarse-graining approaches. For instance, Xia, Keten and co-workers have recently proposed an "energy renormalization" method for adjusting the activation barriers in CG models of polymer glasses, which allows to recover the dynamical and rheological properties obtained from all-atom reference simulations over a wide temperature range.385-387

In addition, one can manually reintroduce terms in the dynamical equations that mimic the effect of the interactions between the CG variables and the remaining "irrelevant" degrees of freedom, i.e., friction and correponding stochastic noise 388 and, possibly, memory.

III.B.1. Dynamic Rescaling. Gaining a more quantitative understanding of the dynamic speedup between FG and CG models is an interesting problem of statistical mechanics. One promising approach is excess entropy scaling. The idea goes back to the "principle of corresponding states" as formulated by Helfand and Rice in 1960,389 which states that, for fluids of particles interacting with a potential of the form V(r) = Eu*(r/6), the dynamical and transport properties for different o and E can be mapped onto each other. For that particular choice of potential, the correspondence can be shown by simple dimensional analysis and seems close to trivial, but it does establish an interesting correlation between dynamic and thermodynamic quantities. Building on this and a method to map simple fluids onto hard sphere fluids, 390 Rosenfeld proposed a heuristic approach to identifying corresponding . 391,392 which states in simple fluids based on their excess entropy,

turned out to be remarkably successful in both the dense and dilute limits. Recently, Rondina et al.393 have shown that excess entropy scaling can also be applied in dense polymer melts. They

39

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

ACS Polymers Au

Perspective

pubs.acs.org/polymerau

used a simple bead spring model as a starting point which was coarse-grained to different degrees and showed that the ratio of dynamical quantities like the bond relaxation time T or the viscosity n in the CG and FG system followed an exponential law XCG/XFG = A exp(aASexc) (14)

in a wide temperature range (with X = T or n). Here ASexc is the temperature-dependent excess entropy difference between the CG and the FG system which was determined by thermody- namic integration. However, the correspondence was found to be less universal than one might hope, since both a and A depend on the CG model.

Lyubimov, Guenza, and co-workers 1º394-396 have considered CG models that map polymer melts onto a fluid of interacting soft blob, and designed a first-principles approach that allowed them to estimate the speedup factor with remarkable accuracy. They assumed that the speedup factor has two contributions: The first is based on a simple rescaling according to the principle of corresponding states. , 389 The second accounts for the different environments of the interacting units, i.e., the different effective friction constants of monomers that are part of a tagged chain and of tagged CG particle in a melt environment. Both are calculated within mode coupling theory397 and then mapped onto each other. Using this ansatz, Guenza and Lyubimov were able to derive analytical expressions for the dynamic speedup factor of diffusion constants in chemically realistic melts such as polybutadiene. 396 Unfortunately, the calculations require a rather involved analytic machinery, and extensions to complex inhomogeneous systems and mixtures are not yet available.

The dynamic rescaling approach can also be applied to nonequilibrium systems, e.g., sheared polymer fluids or amorphous polymer materials under extreme stress. Ge and co-workers have recently studied polystyrene glasses under shear, uniaxial compressive stress,398 and tensile stress which was strong enough to induce crazing.399 They compared the results of CG, united-atom (UA), and all-atom (AA) simulations using a simple rescaling prescription that targetted the stress tensor and found that a single rescaling factor was sufficient to (roughly) collapse the entire stress-strain curves of the different models. This was even true when looking separately at the conservative (elastic) and dissipative contributions to the total stress. In the case of crazing,399 they showed that the craze fibril structure was similar in the three models, and AA craze configurations could be reconstructed from CG simulations. This demonstrates that CG simulations can be used to accelerate simulations and access later times in simulations of non- equilibrium processes.

III.B.2. Introducing Friction. In particle-based CG models, natural frameworks for introducing friction are the Langevin thermostat, which allows to assign separate friction constants for every CG particle, or the DPD thermostat, which conserves momentum and allows to adjust independently the friction parameters for every pair of interacting CG beads.

A natural generic way to determine CG friction parameters from FG simulations is provided by the Green-Kubo formalism, which relates the friction force experienced by a particle moving at fixed velocity to the integral over the time correlation function of the fluctuating forces acting on the particle (the FACF). In the language of linear response theory, this expression relates a steady-state generalized "current" (in this case the mean force on the particle) building up in response to a constant "thermody- namic force" (in this case the fixed velocity) to the time- integrated current-current (in this case force-force) correla-

tions. Phrased in this way, one can immediately see why a naïve application of the approach to FG simulation trajectories is dangerous: The velocity of the CG particles is not fixed, instead it fluctuates and averages to zero, and as a result, the integral over the FACE vanishes as well.388 If the time scales of the dynamics of CG variables and remaining irrelevant variables are well- separated, one can overcome this problem by monitoring the running Green-Kubo integral as a function of an upper time cutoff. It will then first reach a more or less well-defined plateau before it starts decaying, and the plateau value can be used to extract values for the friction parameter.400 However, the choice of the time cutoff value remains somewhat heuristic.

One way to overcome this so-called "plateau problem" is to constrain the dynamics of the FG simulations such that the momentum of the CG particles is kept fixed. A corresponding bottom-up scheme for determining DPD friction parameters from FG simulations was first proposed by Akkerman and Briels388 and later derived more formally by Hijón et al.285 based on the Mori-Zwanzig formalism and an additional Markovian assumption. The idea is to modify the dynamics of the FG simulations such that the desired collective CG variables are constrained to fixed values and do not participate in the dynamics. This effectively decouples the FG dynamics from the CG dynamics and solves the plateau problem. Hijón et al.285 demonstrated the power of the approach using the example of star polymer melts, and several other authors have later applied it to derive CG DPD models for chemically realistic oligomers or polymers such as n-alkanes,401 polybutadiene, 402 a . 402 and dimethyl- propane.403

III.B.3. Introducing Memory. The strategy of absorbing the full dynamics of the irrelevant variables in a single set of DPD friction parameters is justified if the time scales in the CG model are well separated from those processes in the FG system that have been integrated out.388 However, if the degree of coarse- graining is comparatively low, or if the CG model does not capture all slow processes in the FG model, the time scale separation of characteristic processes at the FG and the CG level is incomplete. In such cases, the Mori-Zwanzig projection technique287 yields CG dynamical equations that are non- Markovian, i.e., include memory terms. Two types of approaches have been adopted in the past to account for this effect.

The first is to introduce virtual, but physically motivated variables, which mimic the effect of slow processes that have been eliminated in the CG model,404,405 while not affecting the structural and thermodynamic properties of the CG system. One example is the slip links discussed in section II.C, which are introduced to restore the effect of entanglements, i.e., the slow dynamics of topological constraints that are removed in extremely coarse-grained models. Wu et al. have recently developed a systematic method to derive slip-link parameters from experiments or FG simulation data.19Another example is the RaPiD model for polymers developed by Briels and co- workers, which uses the center of mass of molecules as CG variables, but introduces a set of additional virtual variables that characterize the conformational state of the molecules. 406,407

The second approach is to cast the dynamical equations in the CG model in the form of generalized Langevin equations (GLEs), i.e., to explicitly include memory in the CG dynamical equations.14 Setting up such equations is a highly nontrivial task. In particle-based CG models, one would ideally like to use a multidimensional GLE of the type

40

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

ACS Polymers Au

pubs.acs.org/polymerau

Perspective

a)

b) Local Dyn.

1

0,9

DA.Max 0.8

Chain Dyn.

0

70

^ Debye

AT A

XN

0,7

0,6

:unselected: Simulation

0,5

1005

-0.5

0

0,5

At [toN]

40

0.5

1

2.5

10

1000

Time (units: ~ Rouse times)

Figure 6. (a) Time evolution of order parameter in a diblock copolymer melt after a sudden quench according to different DDFT models (line) and CG particle-based simulations (symbols). The DDFT functional AT that has been contructed from the particle model. Adapted from ref 220. Copyright 2020 American Chemical Society. (b) Snapshots during the ordering of a melt of two-scale multiblock copolymers (A5„B„,A,B,A,B, structure) after a sudden deep (top) and shallow (bottom) quench. Adapted with permission under a Creative commons CC BY 4.0 License from ref 221. Copyright 2020, Schmid/Li.

MỹV(t) = F(+) - ds EK,(t, s) V(s) + OF(t)

j

(15)

where M; and Vi are the mass and velocity of CG particles, Ff (t) and OF;(t) the conservative and fluctuating stochastic forces acting on them, and Ki(t, s) is a multidimensional memory kernel that depends on the configuration at time t and s, and which is related to the stochastic force by a fluctuation- dissipation relation

equil. k (OF,(t) OF,(s)} = m; _ Kit(t, s) {V(s) V,(s))

kBTKi(t, s)

(16)

Note that we have used a tensor notation here, and the last equality = uses the relation (V.(s) V(s)} = 10;kBT/m2, which is valid at thermodynamic equilibrium. The form (eq 15) has been derived by Kinjo and Hyodo408 based on Mori-Zwanzig projections and additional approximations. 17,286 The fluctua- tion-dissipation relation can also be derived from the Mori- Zwanzig projection operator formalism, but one can show that it is a general feature of GLEs which satisfy an orthogonality condition for the relation between random force and velocity.409 Several methods have been developed and analyzed that allow to determine memory kernels from FG simulations and thus construct GLE-based CG models in a bottom-up fash- ion 14,288,410-424The main practical problem with the CG equation, eq 15, is that simulations of such high-dimensional coupled integro- differential equations are computationally very time-consuming, mostly due to the high costs associated with generating the multidimensionally correlated noise that satisfies the fluctua- tion-dissipation relation. Therefore, simplifications must be made. The simplest and most efficient one is to ignore all cross- memory terms and replace Ki(t, s) by a single scalar function, Kij(t, s) = 18 K(t - s). This approach has been used, among others, by Wang and co-workers420,425 to model polymers in dilute solution and by Klippenstein and van der Vegt to model polymer melts.422 In their approach, Klippenstein van der Vegt explicitly address the issue of multibody correlations and propose a method to replace them by a single effective self- memory kernel. To this end, they introduce a new scheme for consistently including the cross-correlations between the stochastic forces and the conservative interactions with the

effective medium, which turns out to be quite accurate in their studies of star polymer melts422 and Asakura-Oosawa fluids.424

Going beyond pure self-memory kernels, Li and co-workers have suggested an approach, termed "non-Markovian DPD" (NM-DPD), which decomposes the memory kernel into a sum of frequency dependent DPD friction functions. 426-428 This relieves the noise generation problem, as the stochastic forces can then be decomposed in the same pairwise manner. Unfortunately, the approach puts severe constraints on the self-memory part of the memory-kernel Kij) since it assumes Kij = - 2+¡Ky. This can cause problems, e.g., when considering hydrodynamic interactions between CG particles in implicit solvent,416 or diffusion of molecules in penetrant networks.403 To overcome the problem, Jung et al. have developed a more general scheme for reconstructing and treating pair memory kernels that decouples self- and pair-friction while still ensuring linear scaling for short-ranged pair-interactions.416

When comparing the two approaches to account for memory in CG systems-physically motivated virtual variables and GLE- based CG models-we should note that the practical solution of GLE equations also often involves the use of auxiliary variables.14 However, these auxiliary variables are just introduced as a numerical trick to solve the GLE and have no physical meaning.280,429-433 The idea is to replace the GLE by a set of regular Langevin equations in an extended phase space. This is possible if the memory kernel can be approximated by a finite sum of possibly complex, but decaying exponentials (a Prony series).434 Alternatively, the parameters of the Langevin equations can be determined directly from correlation functions obtained in FG simulations420,421 in a numerically well- controlled manner. 421

III.B.4. Transition Particle-Continuum. So far, we have discussed dynamical coarse-graining issues in particle-based models. Closely related problems arise in dynamical coarse- graining from particle to continuum equations, when the CG equations are dynamic equations for continuous fields. If the fields describe complex fluids, e.g., polymer systems, one again needs to a account for a multitude of time scales 435-438 which often precludes the use of, e.g., simple Cahn-Hilliard type equations.439 Wang et al.228 have considered dynamic density functional (DDFT) equations of the type (eq 6), but with the mobility function replaced by a time-delayed memory function A(7 - 7'; t - t'), which they calculated analytically in random phase approximation. They studied the effect of memory on the ordering/disordering kinetics in homopolymer and block copolymer melts and found very good agreement between particle-based simulations and continuum simulations.22 One

41

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

ACS Polymers Au

pubs.acs.org/polymerau

Perspective

Soft coarse-grained

Intermediate coarse-grained

CG bonded potentials

Atomistic reference

Atomistic

25 nm

Reference RDF

Morphology

Electronic properties

IE [ev]

7.0

(1)6

y [mm]

Single chain sampling

6.5

6.0

5.5

Small atomistic bulk simulation

5.0 Energy 4.5 landscape x [nm]

2 4 6 8 10 12 14 16 0 2 4 6 8 10 12 14 16 x [nm

Figure 7. Multiscale strategy for predicting charge transport in polymeric semiconductors. from ref 478. Copyright 2015 John Wiley and Sons.

, 478 See text for explanation. Reproduced with permission

key to success in such an approach is to identify the appropriate CG collective variables (densities). Very recently, Müller analyzed this problem440 by examining three situations where seemingly identical initial density perturbations were created in different ways, first by applying a modulated force on all segments of a melt, second by applying a force on end segments only, and third by applying a force on a selected middle segment. In particle-based simulations, the dynamic response to these perturbations was found to be very different in the three cases. This could be reproduced in the continuum simulations if the densities of segments which had experienced the initial force and those of passive segments were treated as separate collective variables.

From the point of view of dynamic coarse-graining, polymers have the convenient feature that relaxation processes on different time scales can often roughly be associated with different length scales. Therefore, Markovian DDFT models such as eq 6 may be able to capture the multiscale dynamics if the nonlocal mobility matrix function is adjusted properly A(7 -7'). Mantha et al.220 developed a bottom-up method to construct A(7 - 7'; t - t') from reference FG particle simulations and found that simulations based on the resulting DDFT model are in very good agreement with corresponding particle-based simulations (see, e.g., Figure 6). Matching mobility matrices is also a convenient way to map different CG particle-based polymer models onto each other.441

One should note, however, that these approaches are restricted to systems close to equilibrium. Far from equilibrium, a CG continuum description operating with densities only is certainly not sufficient and one needs to introduce additional variables that characterize the chain conformations.442 Fur- thermore, polymer stretching generates mechanical stresses, therefore, the use of a purely diffusive dynamical model such as eq 6 (model B dynamics) is no longer justified. An appropriate CG model in such cases must also include momentum and hydrodynamics. As we have discussed in section II.E, viscoelastic models are quite commonly constructed from molecular polymer models such as the elastic dumbbell model. Up to now, this is mostly based on analytical considerations using

substantial mean-field approximations, and to the best of the author's knowledge, systematic bottom-up strategies to construct full viscoelastic models from FG simulations are still missing. So far, coarse-graining strategies that connect particle models with continuous viscoelastic models for polymeric fluids are mostly based on parameter mapping.27 .271 This also holds for elastoplastic models for polymeric glasses.443

Alternatively, it is sometimes possible to combine multiscale approaches with theoretical insights, e.g., from the tube model of viscoelasticity, in order to answer specific questions. One example of such a theoretically informed scale bridging scheme is the branch-on-branch algorithm by McLeish and co- workers. 444,445 'It builds on a theory for the rheology of branched polymers, the so-called pom-pom model by Bishko et al.,446 which estimates the relaxation modulus of chains for given polymer architectures, requiring only a few additional input parameters. The branch-on-branch algorithm establishes a connection between microscopic simulations of the synthesis of highly branched polymers and their rheological properties. The microscopic simulations are used to generate a representative sample of branched polymers, which are then fed into the theoretical machinery. The method was applied successfully by Read et al. commercial Low density polyethylene (LDPE), and recently by Zentel and co-workers to predict the rheological properties of LDPE and polybutyl acrylate (PBA) from the reaction conditions in a miniplant. 447-451

III.B.5. Accessing Late Times. So far, we have mainly discussed strategies to infer correct and consistent dynamical properties from CG models. However, even though CG simulations can cover much longer time spans than atomistic simulations, this is usually not sufficient to access experimentally relevant time scales of seconds, minutes, minutes, or even months. In order to do so, one must also coarse-grain in time.

In situations when it is possible to identify single activated events that slow down the time evolution of a system, one can resort to rare event sampling techniques. Typical problems that are considered with such approaches are, e.g., refolding events of molecules or nucleation processes in materials. A large portfolio of methods has been proposed to study them, 452 such as

42

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective## ACS Polymers Au



pubs.acs.org/polymerau

weighted ensemble techniques, 453,454 transition path sam- pling, 455-457 forward flux sampling, 458-460 the string meth- od, 461,462

or a combinations thereof.463 Using such methods, one can extract rate constants that can be fed into a kinetic model in order to simulate a system on larger time scales.

More generally, one of the most powerful frameworks for coarse graining in time is Markov state modeling, which has become very popular in the field of biomolecular simula-

tions.464-467 In Markov state models (MSMs), the configura- tional space is partitioned into many regions, called macrostates, and the dynamics is modeled in terms of a master equation by memory-less transitions between these states. The number of macrostates is typically chosen quite large, much larger than, e.g., the number of known metastable configurations of a system. Replacing the original molecular dynamics equation by such a relatively fine-grained Markovian process thus represents a severe approximation. In reality, the transitions between macrostates usually have some memory of the past. Never- theless, it can be shown that for optimized mappings, the long- term dynamics is still reproduced very accurately by the MSM, as long as it is governed by a few dominant slow time scales.466

Currently, Markov state modeling is a well-established technique with solid theoretical foundations.466 Techniques are available how to optimize the partitioning into macro- states,468 how to determine transition rates and the associated uncertainty," , 469 and even how to use MSMs to connect theoretical models to experimental trajectory data.470 Recent machine learning based approaches offer additional oppor- tunities for further optimization. 471,472 Many of these techniques assume equilibrium; i.e., they require transition rates to fulfill detailed balance. Knoch and Speck have recently considered nonequilibrium MSMs (NE-MSM)s for driven systems473-476 and shown how to connect MSMs at different CG levels (i.e., with different microstate numbers) in a thermodynamically consistent manner. Knoch et al. also applied the MSM approach to the nonequilibrium problem of force-driven molecule unfolding and showed that MSMs can be used to bridge between loading rates in simulations to experimentally accessible loading rates.477

## III.C. Multiresolution



The ultimate vision of multiscale modeling is to study the properties of a system simultaneously on different scales. Often, it is sufficient to establish one-way communication channels between simulations at different CG level. As an example of such a scheme, Figure 7 shows a strategy to predict the electronic transport properties of polymeric organic materials, which has been developed by Andrienko, Daoulas, and co-work- ers. , 170,478,479 It relies on a theoretical framework that relates the charge transport in organic semiconducting polymers to their local atomistic conformations, 480-483 based on the Marcus theory of electron transfer rates.484 In the multiscale approach of Andrienko, Daoulas, and co-workers, coarse-grained and ultracoarse-grained force fields for conjugated polymers are constructed from atomistic reference simulations and (regarding the nonbonded interactions in the ultracoarse grained models) phenomenological considerations. Ultracoarse-grained simula- tions using these force-fields are then carried out to sample large scale morphologies, which serve as starting point for creating atomistic configurations by a successive backmapping strategy (see below). From the atomistic structures, a local ionization energy landscape is constructed, which allows to infer electronic properties such as the charge mobility.

This work flow demonstrates the power of multiscale approaches; however, it does not yet allow to account for possible feedback mechanisms between processes on different scales. One way to include them is provided by the "heterogeneous multiscale" (HMM) framework proposed by E and Engquist in 2003.485 The idea is to couple a macroscopic continuum simulation-in their case a fluid dynamics simulations-with microscopic FG simulations, which serve to estimate missing data for the macroscale model on the fly.486-489 The approach has recently been applied by Lukácová- Medvid'ová and co-workers to study non-Newtonian flows of shear-thinning polymers melts in complex geometries.490-492 The HMM idea can also be extended to other types of continuum models. For example, Honda and Kawakatsu493 and Müller and Daoulas494 have proposed related mixed-resolution models that concurrently couple time-dependent Ginzburg Landau (TGL) models of (co)polymer blends to more detailed models of the same system: The long-time evolution of the composition profiles is simulated by TGL simulations, but SCF calculations493 or particle-based simulations494 are carried out intermittently, using the current TGL conformation as a basis, to readjust the parameters of the TGL model.

In some situations, it may be desirable to study large portions of a system with a coarse-grained model, but be able to zoom into selected regions in space with higher resolution. This concept goes back to the famous quantum mechanical/ molecular mechanics (QM/MM) method495 by Warshel and Levitt, which combines electronic structure calculations in selected regions of space with classical atomistic molecular dynamics in the rest of the system, separated by a hybrid transition region. In a similar spirit, Prapotnik, delle Site, and Kremer in 2005496 and de Fabritiis, Delgado-Buscalioni, and Coveney in 2006497 have proposed mixed resolution dynamical simulation schemes for complex fluids that allow zooming into selected regions of space and studying them at higher resolution-the "AdResS" scheme49% and the "hybrid MD" scheme.497 Both, however, differ from QM/MM approaches or related approaches involving a CG outer region49 in one important aspect: They allow for a particle exchange between the CG and FG regions. The AdResS scheme49% achieves this by implementing a gradual switch between FG and CG force-fields in a transition region-or, in a later "Hamiltonian-AdResS" variant, 499 499 a switch between interaction potentials. The hybrid- MD scheme497 couples a particle model to a continuum model via flux boundary conditions and allows to generate and remove particles in the transition region. The approaches have subsequently been refined and extended in various direc- tions. 500-502 combined with each other, .503,504 and related schemes have been proposed. For example, Qi et al. have developed a scheme that couples field-based and particle-based polymer models 505-507 via a spatially varying semigrandcanon- ical potential that enforces identity switches.508 As an interesting new idea for AdResS, Heidari and co-workers509-511 recently proposed to use an ideal gas as outer medium. While the latter hardly qualifies as a high-level model of a complex soft material, the setup allows one to carry out simulations with true open boundaries, to determine absolute free energies for the coupled FG system, and to enforce nonequilibrium situations with, e.g., steady-state currents.510

A crucial component of many multiresolution schemes is backmapping: To connect different levels of resolution to each other, one must not only go up the scales by coarse-graining but also be able to go down, i.e., generate representative microscopic

43

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

b)

Perspective

## ACS Polymers Au



conditional in put

a)

generated atom

G

Cumene

Octane

C - fake

B

Training

G

A

conditional in put

reference atom

:selected:

Syndiotactic polystyrene

Testing

A

B

C- real

:selected: :selected:

:selected: preceding atoms

:unselected: CG beads

:selected: generated atom

:selected:

reference atom

Figure 8. Backmapping strategy for polymer melts based on generative adversarial networks (GANs). (a) Sketch of the approach: A generator network G sequentially samples atom positions depending on the CG structure and the existing atoms. The discriminator C evaluates true and fake configurations based on the discrepancy between the positions of reference atoms and generated atoms. The training objective of G is to fool C, and the training objective of C is not to be fooled. Reprinted with permission under a Creative Commons CC BY 4.0 License from ref 512. Copyright 2020 Stieffenhofer/Wand/Bereau. (b) A GAN trained on cumene and octane can be used for backmapping of syndiotactic polystyrene. Reprinted with permission under a Creative Commons CC BY 4.0 License from ref 513. Copyright 2021, Stieffenhofer/Bereau/Wand.

molecular conformations from CG configurations. This is often done in a two-step procedure: First, some heuristic method is used to construct a first guess for the positions of the FG particles, and then, the FG configuration is further optimized by simulated annealing or another energy minimization meth- od 97,377,514-516 Liu et al. have proposed an alternative method based on configurational bias Monte Carlo.517 The back- mapping problem is particularly challenging in the case of proteins, due to their complex chemical structure, and a number of sophisticated methods have been developed for this community. An overview can be found in ref 518, Table 3. Currently, machine learning tools borrowed from computer graphics become increasingly attractive. The reason is that the backmapping problem has some similarity with typical problems in computer graphics, such as filling a given rough frame with a representative set of textures. Stieffenhofer et al.512,513 and Li et al.519 have recently developed backmapping methods based on deep generative adversarial networks (GANs), a framework where two neural networks-a "generator" and a "discrim- inator"-compete with each other in order to learn the main statistical properties of a training set in an unsupervised manner. Stieffenhofer et al. tested their scheme on syndiotactic polystyrene and showed that it can create good backmaps already before energy minimization, and that it is transferable: A GAN trained on melts can be used for backmapping of polymer crystals and even chemically similar (small) molecules512,513 (see Figure 8).

An interesting application of multiresolution tools is the generation of equilibrated polymer melt configurations for large molecular weight-which is still a difficult problem in polymer simulations. 520 In traditional approaches, one first prepares a reasonably random initial configuration, e.g., by assembling a number of polymers with typical melt configurations, and then further relaxes it by implementing unphysical dynamics and/or Monte Carlo moves that allow chain crossing or even change chain connectivity.521-528 In multiscale approaches, 529-536 one uses CG simulations to equilibrate the melt and then reconstructs a FG configuration by increasing the level of resolution in a stepwise fashion. Tubiana et al. have recently performed a systematic comparison of a traditional and a

multiscale equilibration scheme, focusing on topological indicators such as knot distributions, 537 and found excellent agreement.5

## III.D. Machine-Learning Based Strategies



Regarding virtually all aspects of scale bridging techniques discussed above, machine-learning (ML) based methods are becoming increasingly important.102 Kernel-based techniques or artificial neural networks (ANNs) are used for identifying suitable CG variables, 472,539 € for determining accurate atomistic potentials that bridge between ab initio calculations and standard classical force fields278,540 as well as for deriving improved coarse-grained potentials, 15,306,328,339,345,541,542 for determining memory kernels from FG simulations,+20 for constructing MSMs, 471,472 or for backmapping.512,513,519 In some cases, ANNs can be trained to predict the outcome of CG simulations, such as, e.g., the conformation of heteropolymers for a given monomer sequence, 545 the equation of state of homopolymer melts for given pair potential,500 or even complex quantities such as drug-membrane insertion free energies.544 This opens interesting perspectives for new coarse-graining strategies or new strategies of materials design.

Traditionally, an important application of ML in polymer science has been to predict material properties of interest of polymer based materials or composites, such as, e.g., the tribological properties, wear resistance, thermal conductiv- ity, 16,545-548 or even self-assembly.549 Specifically, ANNs have been used for some time to predict the glass transition temperature To, using as input either the chemical structure only550-553 or additional information from small-scale quantum mechanical calculations. , 554,555 Depending on the materials, the predictive power can be quite high.556-564 Such approaches can be applied, e.g., for identifying promising candidates for "high temperature polymers"565 with high To. More generally, a central vision in the emerging field of polymer infor- matics 543,566-569 is to provide ML tools for the discovery of new interesting polymer materials. Ramprasad and co-workers have recently launched a polymer informatics platform (www. polymergenome.org) which offers tools for predicting a variety of polymer properties that include the density, Tg, the melting

44

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

temperature, the dielectric constant, the tensile strength, and many others.570,571

One should note that, in general, extracting new physical insights from ML-based scale bridging strategies is not a trivial task. They can help to unveil hidden structure-property relations or correlations between different material proper- ties, 558,572 but they do not necessarily explain the underlying mechanisms. When used for coarse-graining and force field generation, they can be viewed as being a sophisticated interpolation scheme between available (training) data, but they do not necessarily help to understand general principles of coarse-graining or general features of CG models. On the other hand, feeding in theoretical knowledge of physical principles enhances the efficiency of ML-based procedures and reduces the amount of necessary training data.102 The resulting ML-based models usually have much higher predictive power than the original purely knowledge-based models. Hence knowledge- based and ML-based approaches to scale bridging and multiscale modeling mutually fertilize each other and should be seen as complementary.

## IV. CHALLENGES FOR THE FUTURE



Comparing the available scale-bridging techniques in the last section to the examples of scale-bridging phenomena in polymers in the introduction, it becomes clear that we still need to go a long way before these two ends meet. Being able to gain a comprehensive quantitative understanding of real-world phenomena that includes the interplay of structures processes on all relevant scales, from the smallest to the largest, remains a grand challenge of polymer science. Several hard problems still need to be solved.

Strong Inhomogeneities. Real polymeric materials are usually multiphase materials, they are filled with internal interfaces, and their composition varies dramatically in space. Therefore, the transferability issues that still afflict most CG models represent serious problems that need to be overcome, e.g., by further improving coarse-graining strategies or by linking different CG models to each other in a multiresolution sense.

Defects. Defects are omnipresent in soft materials. They can be defined as very dilute and strongly localized perturbations that may come in several flavors:573 As doping defects in the form of local impurities, as connectivity defects that distort the local molecule structure, or as topological defects that do not involve any local chemical modifications, but still locally perturb the structure in a manner that they cannot be removed without global rearrangements of the whole system (examples are dislocations). Because they are highly dilute, they are usually not present in small scale simulations unless forced to be there; nevertheless, they tend to have a large and long-range impact on the material properties. In order to study this, small scale simulations should thus capture the effect of a defect that they actually do not contain, and that imparts its presence only, e.g., via nonperiodic boundary conditions.

Nonequilibrium and Processing. As discussed above, many traditional CG concepts are developed for equilibrium systems or at least build on a local equilibrium assumption. On the other hand, already the example of viscoelastic phase separation shows that in polymers, local equilibrium cannot be taken for granted even in seemingly simple problems such as spinodal phase separation. Most polymeric materials never reach equilibrium and their properties crucially depend on the way they have been created.35 Therefore, quantitative multiscale descriptions must be able to account for processing pathways. The practical

importance of nonequilibrium processes in polymer systems has been acknowledged for a long time, and nonequilibrium phenomena as occur, e.g., in polymer rheology, have been a research focus since the beginnings of polymer science. Nevertheless, systematic scale bridging strategies for non- equilibrium polymers are still in their infancy.

Accessing Late Times. The time bridging strategies discussed in section III.B.5 have mostly been applied to single molecules or simple small systems and not to materials. In order to understand the properties of polymeric materials at late times, depending on environmental conditions, and to investigate phenomena such as aging, abrasion and wear, failure, and fatigue, one must account for all factors listed above (inhomogeneities, defects, processing history) and study their (co)evolution over a very long time period. So far, theoretical models574-576 are mostly based on empirical theories and with little connection to microscopic simulations.

Multiscale modeling of polymers thus remains a difficult problem, but it also offers exciting new prospects for the future. For instance, one fascinating challenge will be to develop systematic multiscale strategies for truly nonequilibrium living polymeric systems as are common in biology, which depend on strongly fluctuating local compositions and are constantly driven out of equilibrium.

## AUTHOR INFORMATION Corresponding Author



Friederike Schmid - Institut für Physik, Johannes Gutenberg- Universität Mainz, 55128 Mainz, Germany; @ orcid.org/ 0000-0002-5536-6718; Email: friederike.schmid@uni- mainz.de

Complete contact information is available at: https://pubs.acs.org/10.1021/acspolymersau.2c00049

## Notes The author declares no competing financial interest.



## :selected: ACKNOWLEDGMENTS



This work is funded by the German Science Foundation within the Collaborative Research Center TRR 146 "multiscale simulation methods for soft matter systems" via Grant 233630050. The author has had the privilege to serve as the spokesperson of this center for many years. She has benefitted from many stimulating discussions and enjoyable interactions with all members of this Konsortium, in particular Tristan Bereau, Kostas Daoulas, Gregor Diezemann, Burkhard Dünweg, Martin Hanke, Kurt Kremer, Maria Lukácová-Medviďová, Arash Nikoubashman, Joe Rudzinski, Thomas Speck, Lukas Stelzl, Nico van der Vegt, Peter Virnau, and Michael Wand. She thanks M. Lukácová-Medvid'ová for providing Figure 4, D. Rosenberger for sharing the data of Figure 5, and P. Blümler for creating the TOC graphic.

## ■ REFERENCES



(1) Gartner, T. E., III; Jayaraman, A. Modeling and Simulations of Polymers: A Roadmap. Macromolecules 2019, 52, 755-786.

(2) Baschnagel, J .; Binder, K .; Doruker, P .; Gusev, A .; Hahn, O .; Kremer, K .; Mattice, W .; Müller-Plathe, F .; Murat, M .; Paul, W .; Santos, S .; Suter, U .; Tries, V.Bridging the gap between atomistic and coarse- grained models of polymers: Status and perspectives. In Advances in Polymer Science: Viscoelasticity, atomistic models, statistical chemistry; Abe, A., Ed .; Springer, 2000; Vol. 152; pp 41-156.

45

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

## ACS Polymers Au



(3) Müller-Plathe, F. Coarse-graining in polymer simulation: From the atomistic to the mesoscopic scale and back. ChemPhysChem 2002, 3, 754-769.

(4) Peter, C .; Kremer, K. Multiscale simulation of soft matter systems. Faraday Disc. 2010, 144, 9.

(5) Noid, W. Perspective: Coarse-grained models for biomolecular systems. J. Chem. Phys. 2013, 139, 090901.

(6) Li, Y .; Abberton, B. C .; Kröger, M .; Liu, W. K. Challenges in Multiscale Modeling of Polymer Dynamics. Polymers 2013, 5, 751- 832.

(7) Brini, E .; Algaer, E. A .; Ganguly, P .; Li, C .; Rodriguez-Ropero, F .; van der Vegt, N. F. A. Systematic coarse-graining methods for soft matter simulations - A review. Soft Matter 2013, 9, 2108.

(8) Saunders, M. G .; Voth, G. A. Coarse-Graining Methods for Computational Biology. Annu. Rev. Biophys. 2013, 42, 73-93.

(9) Schieber, J. D .; Andreev, M. Entangled Polymer Dynamics in Equilibrium and Flow Modeled Through Slip Links. Annu. Rev. Chem. Biomol. Eng. 2014, 5, 367-381.

(10) Bird, R. B .; Giacomin, A. J. Polymer Fluid Dynamics: Continuum and Molecular Approaches. Annu. Rev. Chem. Biomol. Eng. 2016, 7, 479-507.

(11) Gooneie, A .; Schuschnigg, S .; Holzer, C. A Review of Multiscale Computational Methods in Polymeric Materials. Polymers 2017, 9, 16. (12) Rudzinski, J. F. Recent Progress towards Chemically-Specific Coarse-Grained Simulation Models with Consistent Dynamical Properties. Computation 2019, 7, 42.

(13) Ye, T .; Pan, D .; Huang, C .; Liu, M. Smoothed particle hydrodynamics (SPH) for complex fluid flows: Recent developments in methodology and applications. Phys. Fluids 2019, 31, 011301.

(14) Klippenstein, V .; Tripathy, M .; Jung, G .; Schmid, F .; van der Vegt, N. Introducing Memory in Coarse-Grained Molecular Simu- lations. J. Phys. Chem. B 2021, 125, 4931-4954.

(15) Dhamankar, S .; Webb, M. A. Chemically specific coarse-graining of polymers: Methods and prospects. J. Polym. Sci. 2021, 59, 2613- 2643.

(16) Nguyen, D .; Tao, L .; Li, Y. Integration of Machine Learning and Coarse-Grained Molecular Simulations for Polymer Materials: Physical Understandings and Molecular Design. Frontiers in Chemistry 2022, 9, 820417.

(17) Schilling, T. Coarse-Grained Modelling Out of Equilibrium. Phys. Rep. 2022, 972, 1-45.

(18) Doi, M .; Edwards, S.The theory of polymer dynamics; Oxford University Press: New York, 1986.

(19) Piorkowska, E., Rutledge, G. C., Eds. Handbook of Polymer Crystallization; Wiley: Hoboken, 2013.

(20) Crist, B .; Schultz, J. M. Polymer spherulites: A critical review. Prog. Polym. Sci. 2016, 56, 1-63.

(21) Beran, G. J. O. Modeling Polymorphic Molecular Crystals with Electronic Structure Theory. Chem. Rev. 2016, 116, 5567-5613.

(22) Guerra, G .; Vitagliano, V. M .; Derosa, C .; Petraccone, V .; Corradini, P. Polymorphism in melt crystallized syndiotactic polystyrene samples. Macromolecules 1990, 23, 1539-1544.

(23) Liu, C .; Kremer, K .; Bereau, T. Polymorphism of Syndiotactic Polystyrene Crystals from Multiscale Simulations. Adv. Theory Simul. 2018, 1, 1800024.

(24) Liu, C .; Brandenburg, J. G .; Valsson, O .; Kremer, K .; Bereau, T. Free-energy landscape of polymer-crystal polymorphism. Soft Matter 2020, 16, 9683-9692.

(25) Schulz, M .; Schäfer, M .; Saalwächter, K .; Thurn-Albrecht, T. Competition between crystal growth and intracrystalline chain diffusion determines the lamellar thickness in semicrystalline polymers. Nature Comm. 2022, 13, 119.

(26) Sangroniz, L .; Cavallo, D .; Müller, A. J. Self-Nucleation Effects on Polymer Crystallization. Macromolecules 2020, 53, 4581-4604.

(27) Muthukumar, M. Communication: Theory of melt-memory in polymer crystallization. J. Chem. Phys. 2016, 145, 031105.

(28) Luo, C .; Sommer, J .- U. Frozen Topology: Entanglements Control Nucleation and Crystallization in Polymers. Phys. Rev. Lett. 2014, 112, 195702.

(29) Luo, C .; Kröger, M .; Sommer, J. U. Entanglements and Crystallization of Concentrated Polymer Solutions: Molecular Dynamics Simulations. Macromolecules 2016, 49, 9017-9025.

(30) Luo, C .; Kröger, M .; Sommer, J .- U. Molecular dynamics simulations of polymer crystallization under confinement: Entangle- ment effect. Polymer 2017, 109, 71-84.

(31) Xiao, H .; Luo, C .; Yan, D .; Sommer, J .- U. Molecular Dynamics Simulation of Crystallization Cyclic Polymer Melts As Compared to Their Linear Counterparts. Macromolecules 2017, 50, 9796-9806.

(32) Zhai, Z .; Fusco, C .; Morthomas, J .; Perez, M .; Lame, O. Disentangling and Lamellar Thickening of Linear Polymers during Crystallization: Simulation of Bimodal and Unimodal Molecular Weight Distribution Systems. ACS Nano 2019, 13, 11310-11319. (33) Payal, R. S .; Sommer, J .- U. Crystallization of Polymers under the Influence of an External Force Field. Polymers 2021, 13, 2078.

(34) Liu, X .; Yu, W. Role of Chain Dynamics in the Melt Memory Effect of Crystallization. Macromolecules 2020, 53, 7887-7898.

(35) Chandran, S .; Baschnagel, J .; Cangialosi, D .; Fukao, K .; Glynos, E .; Janssen, L. M. C .; Müller, M .; Muthukumar, M .; Steiner, U .; Xu, J .; Napolitano, S .; Reiter, G. Processing Pathways Decide Polymer Properties at the Molecular Level. Macromolecules 2019, 52, 7146- 7156.

(36) Hall, K. W .; Percec, S .; Shinoda, W .; Klein, M. L. Property Decoupling across the Embryonic Nucleus-Melt Interface during Polymer Crystal Nucleation. J. Phys. Chem. B 2020, 124, 4793-4804. (37) Cui, K .; Ma, Z .; Tian, N .; Su, F .; Liu, D .; Li, L. Multiscale and Multistep Ordering of Flow-Induced Nucleation of Polymers. Chem. Rev. 2018, 118, 1840-1886.

(38) Luo, W .; Wang, J .; Guo, Y .; Hu, W. Role of stress relaxation in stress-induced polymer crystallization. Polymer 2021, 235, 124306.

(39) Kearns, K. L .; Scherzer, J .; Chyasnavichyus, M .; Monaenkova, D .; Moore, J .; Sammler, R. L .; Fielitz, T .; Nicholson, D. A .; Andreev, M .; Rutledge, G. C. Measuring Flow-Induced Crystallization Kinetics of Polyethylene after Processing. Macromolecules 2021, 54, 2101-2112. (40) Sheng, J .; Chen, W .; Cui, K .; Li, L. Polymer crystallization under external flow. Rep. Prog. Phys. 2022, 85, 036601.

(41) Hall, K. W .; Percec, S .; Shinoda, W .; Klein, M. L. Chain-End Modification: A Starting Point for Controlling Polymer Crystal Nucleation. Macromolecules 2021, 54, 1599-1610.

(42) Flachmüller, A .; Mecking, S .; Peter, C. Coarse-grained model of the aggregation and structure control of polyethylene nanocrystals. J. Phys .: Condens. Matter 2021, 32, 264001.

(43) Jabbari-Farouji, S .; Rottler, J .; Lame, O .; Makke, A .; Perez, M .; Barrat, J .- L. Plastic Deformation Mechanisms of Semicrystalline and Amorphous Polymers. ACS Macro Lett. 2015, 4, 147-150.

(44) Jabbari-Farouji, S .; Lame, O .; Perez, M .; Rottler, J .; Barrat, J .- L. Role of the Intercrystalline Tie Chains Network in the Mechanical Response of Semicrystalline Polymers. Phys. Rev. Lett. 2017, 118, 217802.

(45) Schultz, J. M. Self-Generated Fields and Polymer Crystallization. Macromolecules 2012, 45, 6299-6323.

(46) Boudenne, A., Ibos, L., Candau, Y., Thomas, S., Eds. Handbook of multiphase polymer systems; Wiley: Hoboken, 2011.

(47) Shokoohi, S .; Arefazar, A. A review on ternary immiscible polymer blends: morphology and effective parameters. Polym. Adv. Techn. 2009, 20, 433-447.

(48) Xue, L .; Zhang, J .; Han, Y. Phase separation induced ordered patterns in thin polymer blend films. Prog. Polym. Sci. 2012, 37, 564- 594.

(49) Castelletto, V .; Hamley, I. W. Morphology of block copolymer melts. Curr. Opn. in Sol. State & Mater. Sci. 2004, 8, 426-438.

(50) Orilall, M. C .; Wiesner, U. Block copolymer based composition and morphology control in nanostructured hybrid materials for energy conversion and storage: solar cells, batteries, and fuel cells. Chem. Soc. Rev. 2011, 40, 520-535.

(51) Mai, Y .; Eisenberg, A. Self-assembly of block copolymers. Chem. Soc. Rev. 2012, 41, 5969-5985.

(52) Kang, S .; Kim, G .- H .; Park, S .- Y. Conjugated Block Copolymers for Functional Nanostructures. Acc. Chem. Res. 2022, 55, 2224-2234.

46

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

## ACS Polymers Au



(53) Koohbor, B .; Pagliocca, N .; Youssef, G. A multiscale experimental approach to characterize micro-to-macro transition length scale in polymer foams. Mech. Mater. 2021, 161, 104006. (54) Balazs, A. C .; Emrick, T .; Russell, T. P. Nanoparticle polymer composites: Where two small worlds meet. Science 2006, 314, 1107- 1110.

(55) Zeng, Q. H .; Yu, A. B .; Lu, G. Q. Multiscale modeling and simulation of polymer nanocomposites. Prog. Polym. Sci. 2008, 33, 191-269.

(56) Rueda, M. M .; Auscher, M .- C .; Fulchiron, R .; Perie, T .; Martin, G .; Sonntag, P .; Cassagnau, P. Rheology and applications of highly filled polymers: A review of current understanding. Prog. Polym. Sci. 2017, 66, 22-53.

(57) Karatrantos, A .; Composto, R. J .; Winey, K. I .; Kröger, M .; Clarke, N. Modeling of Entangled Polymer Diffusion in Melts and Nanocomposites: A Review. Polymers 2019, 11, 876.

(58) Giunta, G .; Chiricotto, M .; Jackson, I .; Karimi-Varzaneh, H. A .; Carbone, P. Multiscale modelling of heterogeneous fillers in polymer composites: The case of polyisoprene and carbon black. J. Phys .: Cond. Matt. 2021, 33, 194003.

(59) Sun, R .; Melton, M .; Safaie, N .; Ferrier, R. C., Jr .; Cheng, S .; Liu, Y .; Zuo, X .; Wang, Y. Molecular View on Mechanical Reinforcement in Polymer Nanocomposites. Phys. Rev. Lett. 2021, 126, 117801. (60) Cheng, S .; Bocharova, V .; Belianinov, A .; Xiong, S .; Kisliuk, A .; Somnath, S .; Holt, A. P .; Ovchinnikova, O. S .; Jesse, S .; Martin, H .; Etampawala, T .; Dadmun, M .; Sokolov, A. P. Unraveling the Mechanism of Nanoscale Mechanical Reinforcement in Glassy Polymer Nanocomposites. Nano Lett. 2016, 16, 3630-3637.

(61) Zhai, S .; Zhang, P .; Xian, Y .; Zeng, J .; Shi, B. Effective thermal conductivity of polymer composites: Theoretical models and simulation models. Int. J. Heat Mass Transfer 2018, 117, 358-374. (62) Kapitza, P. L. The study of heat transfer in helium II. J. Phys. U.S.S.R 1941, 4, 181.

(63) Shin, H .; Yang, S .; Chang, S .; Yu, S .; Cho, M. Multiscale homogenization modeling for thermal transport properties of polymer nanocomposites with Kapitza thermal resistance. Polymer 2013, 54, 1543-1554.

(64) He, B .; Mortazavi, B .; Zhuang, X .; Rabczuk, T. Modeling Kapitza resistance of two-phase composite material. Composite structures 2016, 152, 939-946.

(65) Eisoldt, L .; Smith, A .; Scheibel, T. Decoding the secrets of spider silk. Mater. Today 2011, 14, 80-86.

(66) Lopez Barreiro, D .; Yeo, J .; Tarakanova, A .; Martin-Martinez, F.

J .; Buehler, M. J. Multiscale Modeling of Silk and Silk-Based Biomaterials-A Review. Macromol. Biosci. 2019, 19, 1800253.

(67) Jin, H .; Kaplan, D. Mechanism of silk processing in insects and spiders. Nature 2003, 424, 1057-1061.

(68) Kielty, C. M .; Grant, M. E. The collagen family: Structure, assembly, and organization in the extracellular matrix. In Connective tissue and its heritable disorders; Royce, P. M., Steinmann, B., Eds .; Wiley, 2002; p 159.

(69) Buehler, M. J. Nature designs tough collagen: Explaining the nanostructure of collagen fibrils. Proc. Natl. Acad. Sci. U.S.A. 2006, 103, 12285.

(70) Shoulders, M. D .; Raines, R. T. Collagen Structure and Stability. Annu. Rev. Biochem. 2009, 78, 929-958.

(71) Bella, J. Collagen structure: new tricks from a very old dog. Biochem. J. 2016, 473, 1001-1025.

(72) Kar, K .; Amin, P .; Bryan, M. A .; Persikov, A. V .; Mohs, A .; Wang, Y .- H .; Brodsky, B. Self-association of collagen triple helix peptides into higher order structures. J. Biol. Chem. 2006, 281, 33283.

(73) Orgel, J. P. R. O .; Irving, T. C .; Miller, A .; Wess, T. J. Microfibrillar structure of type I collagen in situ. Proc. Natl. Acad. Sci. U.S.A. 2006, 103, 9001.

(74) Leikina, E .; Mertts, M. V .; Kuznetsova, N .; Leikin, S. Type I collagen is thermally unstable at body temperature. Proc. Natl. Acad. Sci. U.S.A. 2002, 99, 1314.

(75) Brown, G. N .; Sattler, R. L .; Guo, X. E. Experimental studies of bone mechanoadaptation: bridging in vitro and in vivo studies with multiscale systems. Interface focus 2016, 6, 20150071.

(76) Garcia-Aznar, J. M .; Nasello, G .; Hervas-Raluy, S .; Perez, M. A .; Gomez-Benito, M. J. Multiscale modeling of bone tissue mechanobi- ology. Bone 2021, 151, 116032.

(77) Allain, J .- M .; Lynch, B .; Schanne-Klein, M .- C. Multiscale characterisation of skin mechanics through in situ imaging. In Skin Biophysics: From Experimental Characterization to Advanced Modelling; Limbert, G., Ed .; Studies in Mechanobiology Tissue Engineering and Biomaterials; 2019; Vol. 22; pp 235-263.

(78) Shelley, M. J. The Dynamics of Microtubule/Motor-Protein Assemblies in Biology and Physics. Ann. Rev. Fluid Mech. 2016, 48, 487-506.

(79) Powers, J. D .; Malingen, S. A .; Regnier, M .; Daniel, T. L. The Sliding Filament Theory Since Andrew Huxley: Multiscale and Multidisciplinary Muscle Research. Annu. Rev. Biophys. 2021, 50, 373-400.

(80) Hyman, A. A .; Weber, C. A .; Juelicher, F. Liquid-Liquid Phase Separation in Biology. Annu. Rev. Cell Dev. Biol. 2014, 30, 39-58.

(81) Shin, Y .; Brangwynne, C. P. Liquid phase condensation in cell physiology and disease. Science 2017, 357, 6357.

(82) Boeynaems, S .; Alberti, S .; Fawzi, N. L .; Mittag, T .; Polymenidou, M .; Rousseau, F .; Schymkowitz, J .; Shorter, J .; Wolozin, B .; van den Bosch, L .; Tompa, P .; Fuxreiter, M. Protein Phase Separation: A New Phase in Cell Biology. Trends in Cell Biology 2018, 28, 420-435.

(83) Berry, J .; Brangwynne, C. P .; Haataja, M. Physical principles of intracellular organization via active and passive phase transitions. Rep. Prog. Phys. 2018, 81, 046601.

(84) Posey, A. E .; Holehouse, A. S .; Pappu, R. V.Phase Separation of Intrinsically disordered proteins; In Methods in Enzymology; Rhoades, E., Ed .; Elsevier, 2018; Vol. 611; pp 1-30.

(85) Alberti, S .; Dormann, D. Liquid-Liquid Phase Separation in Disease. Annu. Rev. Genetics 2019, 53, 171.

(86) Choi, J .- M .; Holehouse, A. S .; Pappu, R. V. Physical Principles Underlying the Complex Biology of Intracellular Phase Transitions. Annu. Rev. Biophys 2020, 49, 107-133.

(87) Lyon, A. S .; Peeples, W. B .; Rosen, M. K. A framework for understanding the functions of biomolecular condensates across scales. Nature Rev. Mol. Cell Biol. 2021, 22, 215-235.

(88) Baschnagel, J .; Binder, K .; Paul, W .; Laso, M .; Suter, U. W .; Batoulis, I .; Jilge, W .; Burger, T. On the construction of coarse-grained models for linear flexible polymer chains - distribution functions for groups of consecutive monomers. J. Chem. Phys. 1991, 95, 6014-6025. (89) Rapold, R. F .; Mattice, W. L. Introduction of short and long range energies to simulate real chains on the 2nd lattice. Macromolecules 1996, 29, 2457-2466.

(90) Tries, V .; Paul, W .; Baschnagel, J .; Binder, K. Modeling polyethylene with the bond fluctuation model. J. Chem. Phys. 1997, 106, 738-748.

(91) Cho, J .; Mattice, W. Estimation of long-range interaction in coarse-grained rotational isomeric state polyethylene chains on a high coordination lattice. Macromolecules 1997, 30, 637-644.

(92) Doruker, P .; Mattice, W. Reverse mapping of coarse-grained polyethylene chains from the second nearest neighbor diamond lattice to an atomistic model in continuous space. Macromolecules 1997, 30, 5520-5526.

(93) Doruker, P .; Mattice, W. Dynamics of bulk polyethylene on a high coordination lattice. Macromol. Symp. 1998, 133, 47-70.

(94) Paul, W .; Binder, K .; Kremer, K .; Heermann, D. W. Structure property correlation of polymers, A Monte Carlo Approach. Macro- molecules 1991, 24, 6332-6334.

(95) Paul, W .; Pistoor, N. A Mapping of realistic onto abstract polymer models and an application to 2 bisphenol polycarbonates. Macromolecules 1994, 27, 1249-1255.

(96) Tschöp, W .; Kremer, K .; Batoulis, J .; Bürger, T .; Hahn, O. Simulation of polymer melts. I. Coarse-graining procedure for polycarbonates. Acta Polym. 1998, 49, 61-74.

47

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(97) Tschöp, W .; Kremer, K .; Hahn, O .; Batoulis, J .; Bürger, T. Simulation of polymer melts. II. From coarse-grained models back to atomistic description. Acta Polym. 1998, 49, 75-79.

(98) Eilhard, J .; Zirkel, A .; Tschop, W .; Hahn, O .; Kremer, K .; Scharpf, O .; Richter, D .; Buchenau, U. Spatial correlations in polycarbonates: Neutron scattering and simulation. J. Chem. Phys. 1999, 110, 1819- 1830.

(99) Doruker, P .; Rapold, R .; Mattice, W. Rotational isomeric state models for polyoxyethylene and polythiaethylene on a high coordination lattice. J. Chem. Phys. 1996, 104, 8742-8749.

(100) Haliloglu, T .; Mattice, W. Mapping of rotational isomeric state chains with asymmetric torsional potential energy functions on a high coordination lattice: Application to polypropylene. J. Chem. Phys. 1998, 108, 6989-6995.

(101) Padding, J. T .; Briels, W. J. Systematic coarse-graining of the dynamics of entangled polymer melts: the road from chemistry to rheology. J. Phys .: Cond. Matt. 2011, 23, 233101.

(102) Noé, F .; Tkatchenko, A .; Müller, K .- R .; Clementi, C. Machine Learning for Molecular Simulations. Annu. Rev. Phys. Chem. 2020, 71, 361-390.

(103) Barton, A. F. M.Handbook of Polymer-Liquid Interaction Parameters and Solubility Parameters; CRC Press: Boca Raton, 1990. (104) Hatakeyama, H .; Hatakeyama, T. Interaction between water and hydrophilic polymers. Thermochim. Acta 1998, 308, 3-22. 14th IUPAC Conference on Chemical Thermodynamics, OSAKA, JAPAN, AUG 25-30, 1996.

(105) Heinz, H .; Ramezani-Dakhel, H. Simulations of inorganic- bioorganic interfaces to discover new materials: insights, comparisons to experiment, challenges, and opportunities. Chem. Soc. Rev. 2016, 45, 412-448.

(106) Braunecker, W. A .; Matyjaszewski, K. Controlled/living radical polymerization: Features, developments, and perspectives. Prog. Polym. Sci. 2007, 32, 93-146.

(107) Vega-Hernández, M. A .; Cano-Díaz, G. S .; Vivaldo-Lima, E .; Rosas-Aburto, A .; Hernández-Luna, M. G .; Martinez, A .; Palacios- Alquisira, J .; Mohammadi, Y .; Penlidis, A. A Review on the Synthesis, Characterization, and Modeling of Polymer Grafting. Processes 2021, 9, 375.

(108) Rappé, A. K .; Goddard, W. A., III Charge Equilibration for Molecular Dynamics Simulations. J. Phys. Chem. 1991, 95, 3358-3363. (109) Wilmer, C. E .; Kim, K. C .; Snurr, R. Q. An Extended Charge Equilibration Method. J. Phys. Chem. Lett. 2012, 3, 2506-2511.

(110) Wu, J. Density functional theory for chemical engineering: From capillarity to soft materials. AIChE J. 2006, 52, 1169-1193. (111) Dovesi, R .; Erba, A .; Orlando, R .; Zicovich-Wilson, C. M .; Civalleri, B .; Maschio, L .; Rerat, M .; Casassa, S .; Baima, J .; Salustro, S .; Kirtman, B. Quantum-mechanical condensed matter simulations with CRYSTAL. Wiley Interdisc. Rev. - Comp. Mol. Sci. 2018, 8, e1360.

(112) Sozlc, K., Ed. Polymer compatibility and incompatibility: Principles and Practices; Harwood Academic Publishers, MMI Press: Chur, Switzerland, New York, 1982.

(113) Boroudjerdi, H .; Kim, Y .; Naji, A .; Netz, R .; Schlagberger, X .; Serr, A. Statics and dynamics of strongly charged soft matter. Phys. Rep. 2005, 416, 129-199.

(114) Mukherji, D .; Marques, C. M. M .; Kremer, K. Polymer collapse in miscible good solvents is a generic phenomenon driven by preferential adsorption. Nature Comm. 2014, 5, 4882.

(115) Magda, J. J .; Fredrickson, G. H .; Larson, R. G .; Helfand, E. Dimensions of a polymer-chain in a mixed-solvent. Macromolecules 1988, 21, 726-732.

(116) Bischofberger, I .; Calzolari, D. C. E .; Trappe, V. Co- nonsolvency of PNiPAM at the transition between solvation mechanisms. Soft Matter 2014, 10, 8288-8295.

(117) Rodriguez-Ropero, F .; Hajari, T .; van der Vegt, N. F. A. Mechanism of Polymer Collapse in Miscible Good Solvents. J. Phys. Chem. B 2015, 119, 15780-15788.

(118) Dudowicz, J .; Freed, K. F .; Douglas, J. F. Communication: Cosolvency and cononsolvency explained in terms of a Flory-Huggins type theory. J. Chem. Phys. 2015, 143, 131101.

(119) Bharadwaj, S .; Niebuur, B .- J .; Nothdurft, K .; Richtering, W .; van der Vegt, N. F. A .; Papadakis, C. M. Cononsolvency of thermores- ponsive polymers: Where we are now and where we are going. Soft Matter 2022, 18, 2884-2909.

(120) Li, X .; Wang, N .; Ma, Y .; Ji, X .; Huang, Y .; Huang, X .; Wang, T .; Zhou, L .; Hao, H. Revealing the Molecular Mechanism of Cosolvency Based on Thermodynamic Phase Diagram, Molecular Simulation, and Spectrum Analysis: The Tolbutamide Case. J. Phys. Chem. Lett. 2022, 13, 1628-1635.

(121) Marrink, S. J .; Risselada, H. J .; Yefimov, S .; Tieleman, D. P .; de Vries, A. H. The MARTINI force field: coarse grained model for biomolecular simulations. J. Phys. Chem. B 2007, 111, 7812-7824. (122) De Gennes, P. G.Scaling Concepts in Polymer Physics; Cornell University Press: Ithaca and London, 1979.

(123) Rubinstein, M .; Colby, R. H.Polymer Physics; Oxford University Press: Oxford, 2003.

(124) Halperin, A. On polymer brushes and blobology: An introduction. In Soft Order in Physical Systems; Rabin, Y., Bruinsma, R., Eds .; Springer, 1994; pp 33-56.

(125) Das, R. K .; Pappu, R. V. Conformations of intrinsically disordered proteins are influenced by linear sequence distributions of oppositely charged residues. Proc. Natl. Acad. Sci. U.S.A. 2013, 110, 13392-13397.

(126) Pomposo, J. A .; Perez-Baena, I .; Lo Verso, F .; Moreno, A. J .; Arbe, A .; Colmenero, J. How Far Are Single-Chain Polymer Nanoparticles in Solution from the Globular State? ACS Macro Lett. 2014, 3, 767-772.

(127) Soranno, A .; Koenig, I .; Borgia, M. B .; Hofmann, H .; Zosel, F .; Nettels, D .; Schuler, B. Single-molecule spectroscopy reveals polymer effects of disordered proteins in crowded environments. Proc. Natl. Acad. Sci. U.S.A. 2014, 111, 4874-4879.

(128) Carmesin, I .; Kremer, K. The Bond Fluctuation Method - A new effective algorithm for the dynamics of polymers in all spatial dimensions. Macromolecules 1988, 21, 2819-2823.

(129) Grest, G. S .; Kremer, K. Molecular-dynamics simulation for polymer in the presence of a heat bath. Phys. Rev. A 1986, 33, 3628- 3631.

(130) Faller, R .; Kolb, A .; Müller-Plathe, F. Local chain ordering in amorphous polymer melts: influence of chain stiffness. Phys. Chem. Chem. Phys. 1999, 1, 2071-2076.

(131) Hsu, H .- P. Monte Carlo simulations of lattice models for single polymer systems. J. Chem. Phys. 2014, 141, 164903.

(132) Deutsch, H. P .; Binder, K. Interdiffusion and self-diffusion in polymer mixtures - A Monte Carlo Study. J. Chem. Phys. 1991, 94, 2294-2304.

(133) Ahlrichs, P .; Dünweg, B. Simulation of a single polymer chain in solution by combining lattice Boltzmann and molecular dynamics. J. Chem. Phys. 1999, 111, 8225-8239.

(134) Paul, W .; Binder, K .; Heermann, D. W .; Kremer, K. Crossover scaling in semidilute polymer solutions - A Monte Carlo test. J. de Physique II 1991, 1, 37-60.

(135) van den Oever, J .; Leermakers, F .; Fleer, G .; Ivanov, V .; Shusharina, N .; Khokhlov, A .; Khalatur, P. Coil-globule transition for regular, random, and specially designed copolymers: Monte Carlo simulation and self-consistent field theory. Phys. Rev. E 2002, 65, 041708.

(136) Binder, K .; Baschnagel, J .; Müller, M .; Paul, W .; Rampf, F. Simulation of phase transitions of single polymer chains: Recent advances. Macromol. Symp. 2006, 237, 128-138.

(137) Luettmer-Strathmann, J .; Rampf, F .; Paul, W .; Binder, K. Transitions of tethered polymer chains: A simulation study with the bond fluctuation lattice model. J. Chem. Phys. 2008, 128, 064903.

(138) Müller, M. Miscibility behavior and single chain properties in polymer blends: a bond fluctuation model study. Macromol. Theory Sim. 1999, 8, 343-374.

(139) Ray, P .; Baschnagel, J .; Binder, K. Dynamics near the glass- transition in 2-dimensional polymer melts - A Monte Carlo simulation study. J. Phys .: Cond. Matt. 1993, 5, 5731-5742.

48

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

pubs.acs.org/polymerau

Perspective

## ACS Polymers Au



(140) Binder, K .; Baschnagel, J .; Paul, W. Glass transition of polymer melts: test of theoretical concepts by computer simulation. Prog. Polym. Sci. 2003, 28, 115-172.

(141) Radosz, W .; Pawlik, G .; Mitus, A. C. Characterization of Monte Carlo Dynamic/Kinetic Properties of Local Structure in Bond Fluctuation Model of Polymer System. Materials 2021, 14, 4962. (142) Everaers, R .; Karimi-Varzaneh, H. A .; Fleck, F .; Hojdis, N .; Svaneborg, C. Kremer-Grest Models for Commodity Polymer Melts: Linking Theory, Experiment, and Simulation at the Kuhn Scale. Macromolecules 2020, 53, 1901-1916.

(143) Everaers, R .; Sukumaran, S .; Grest, G .; Svaneborg, C .; Sivasubramanian, A .; Kremer, K. Rheology and microscopic topology of entangled polymeric liquids. Science 2004, 303, 823-826.

(144) Milner, S. T. Unified Entanglement Scaling for Flexible, Semiflexible, and Stiff Polymer Melts and Solutions. Macromolecules 2020, 53, 1314-1325.

(145) Pagonabarraga, I .; Frenkel, D. Dissipative particle dynamics for interacting systems. J. Chem. Phys. 2001, 115, 5015.

(146) Groot, R. D .; Warren, P. B. Dissipative particle dynamics: Bridging the gap between atomistic and mesoscopic simulation. J. Chem. Phys. 1997, 107, 4423-4435.

(147) Laso, M .; Öttinger, H. C .; Suter, U. W. Bond-length and bond- angle distributions in coarse-grained polymer chains. J. Chem. Phys. 1991, 95, 2178-2182.

(148) Murat, M .; Kremer, K. From many monomers to many polymers: Soft ellipsoid model for polymer melts and mixtures. J. Chem. Phys. 1998, 108, 4340-4348.

(149) Likos, C. Effective interactions in soft condensed matter physics. Phys. Rep. 2001, 348, 267-439.

(150) Bolhuis, P. G .; Louis, A. A .; Hansen, J. P .; Meijer, E. J. Accurate effective pair potentials for polymer solutions. J. Chem. Phys. 2001, 114, 4296-4311.

(151) Eurich, F .; Maass, P. Soft ellipsoid model for Gaussian polymer chains. J. Chem. Phys. 2001, 114, 7655-7668.

(152) Vettorel, T .; Besold, G .; Kremer, K. Fluctuating soft-sphere approach to coarse-graining of polymer models. Soft Matter 2010, 6, 2282-2292.

(153) Narros, A .; Likos, C. N .; Moreno, A. J .; Capone, B. Multi-blob coarse-graining for ring polymer solutions. Soft Matter 2014, 10, 9601. (154) D'Adamo, G .; Menichetti, R .; Pelissetto, A .; Pierleoni, C. Coarse-graining polymer solutions: A critical appraisal of single- and multi-site models. Eur. Phys. J. - Spec. Topics 2015, 224, 2239-2267. (155) Laradji, M .; Guo, H .; Zuckermann, M. J. Off-lattice Monte- Carlo simulation of polymer brushes in good solvents. Phys. Rev. E 1994, 49, 3199-3206.

(156) Besold, G .; Guo, H .; Zuckermann, M. Off-lattice Monte Carlo simulation of the discrete Edwards model. J. Polym. Sci., Part B 2000, 38, 1053-1068.

(157) Ganesan, V .; Pryamitsyn, V. Dynamical mean-field theory for inhomogeneous polymeric systems. J. Chem. Phys. 2003, 118, 4345- 4348.

(158) Detcheverry, F. A .; Kang, H .; Daoulas, K. C .; Müller, M .; Nealey, P. F .; dePablo, J. J. Monte Carlo Simulations of a Coarse Grain Model for Block Copolymers and Nanocomposites. Macromolecules 2008, 41, 4989-5001.

(159) Milano, G .; Kawakatsu, T. Hybrid particle-field molecular dynamics simulations for dense polymer systems. J. Chem. Phys. 2009, 130, 214106.

(160) Wang, Q .; Yin, Y. Fast off-lattice Monte Carlo simulations with "soft" repulsive potentials. J. Chem. Phys. 2009, 130, 104903.

(161) Müller, M. Studying Amphiphilic Self-assembly with Soft Coarse-Grained Models. J. Stat. Phys. 2011, 145, 967-1016.

(162) Zhang, J .; Mukherji, D .; Daoulas, K. C. Studying PMMA films on silica surfaces with generic microscopic and mesoscale models. Eur. Phys. J. - Spec. Topics 2016, 225, 1423-1440.

(163) Zhang, J .; Kremer, K .; Michels, J. J .; Daoulas, K. C. Exploring Disordered Morphologies of Blends and Block Copolymers for Light- Emitting Diodes with Mesoscopic Simulations. Macromolecules 2020, 53, 523-538.

(164) Bore, S. L .; Cascella, M. Hamiltonian and alias-free hybrid particle-field molecular dynamics. J. Chem. Phys. 2020, 153, 094106. (165) Hömberg, M .; Müller, M. Main phase transition in lipid bilayers: Phase coexistence and line tension in a soft, solvent-free, coarse-grained model. J. Chem. Phys. 2010, 132, 155104.

(166) Zhang, S .; Qi, S .; Klushin, L. I .; Skvortsov, A. M .; Yan, D .; Schmid, F. Anomalous critical slowdown at a first order phase transition in single polymer chains. J. Chem. Phys. 2017, 147, 064902.

(167) Zhang, S .; Qi, S .; Klushin, L. I .; Skvortsov, A. M .; Yan, D .; Schmid, F. Phase transitions in single macromolecules: Loop-stretch transition versus loop adsorption transition in end-grafted polymer chains. J. Chem. Phys. 2018, 148, 044903.

(168) Sevink, G. J. A .; Schmid, F .; Kawakatsu, T .; Milano, G. Combining cell-based hydrodynamics with hybrid particle-field simulations: efficient and realistic simulation of structuring dynamics. Soft Matter 2017, 13, 1594-1623.

(169) Daoulas, K. C .; Ruehle, V .; Kremer, K. Simulations of nematic homopolymer melts using particle-based models with interactions expressed through collective variables. J. Phys .: Cond. Matt. 2012, 24, 284121.

(170) Greco, C .; Melnyk, A .; Kremer, K .; Andrienko, D .; Daoulas, K. C. Generic Model for Lamellar Self-Assembly in Conjugated Polymers: Linking Mesoscopic Morphology and Charge Transport in P3HT. Macromolecules 2019, 52, 968-981.

(171) Lytle, T. K .; Radhakrishna, M .; Sing, C. E. High Charge Density Coacervate Assembly via Hybrid Monte Carlo Single Chain in Mean Field Theory. Macromolecules 2016, 49, 9693-9705.

(172) Kolli, H. B .; de Nicola, A .; Bore, S. L .; Schäfer, K .; Diezemann, G .; Gauss, J .; Kawakatsu, T .; Lu, Z .- Y .; Zhu, Y .- L .; Milano, G .; Cascella, M. Hybrid Particle-Field Molecular Dynamics Simulations of Charged Amphiphiles in an Aqueous Environment. J. Chem. Theory Comput. 2018, 14, 4928-4937.

(173) Shi, A .; Noolandi, J. Theory of inhomogeneous weakly charged polyelectrolytes. Macromol. Theory Sim. 1999, 8, 214-229.

(174) Duplantier, B .; Saleur, H. Exact surface and wedge exponents for polymers in 2 dimensions. Phys. Rev. Lett. 1986, 57, 3179-3182.

(175) Duplantier, B .; Saleur, H. Exadt tricritical exponents for polymers at the theta-point in 2 dimensions. Phys. Rev. Lett. 1987, 59, 539-542.

(176) Semenov, A .; Johner, A. Theoretical notes on dense polymers in two dimensions. Eur. Phys. J. E 2003, 12, 469-480.

(177) Cavallo, A .; Müller, M .; Binder, K. Unmixing of polymer blends confined in ultrathin films: Crossover between two-dimensional and three-dimensional behavior. J. Phys. Chem. B 2005, 109, 6544-6552. (178) Cavallo, A .; Müller, M .; Wittmer, J .; Johner, A .; Binder, K. Single chain structure in thin polymer films: Corrections to Floryas and Silberbergas hypotheses. J. Phys .: Cond. Matt. 2005, 17, S1697-S1709. (179) Meyer, H .; Wittmer, J. P .; Kreer, T .; Johner, A .; Baschnagel, J. Static properties of polymer melts in two dimensions. J. Chem. Phys. 2010, 132, 184904.

(180) Halverson, J. D .; Lee, W. B .; Grest, G. S .; Grosberg, A. Y .; Kremer, K. Molecular dynamics simulation study of nonconcatenated ring polymers in a melt. I. Statics. J. Chem. Phys. 2011, 134, 204904. (181) Rosa, A .; Everaers, R. Ring Polymers in the Melt State: The Physics of Crumpling. Phys. Rev. Lett. 2014, 112, 118302.

(182) Everaers, R .; Grosberg, A. Y .; Rubinstein, M .; Rosa, A. Flory theory of randomly branched polymers. Soft Matter 2017, 13, 1223- 1234.

(183) Chubak, I .; Likos, C. N .; Egorov, S. A. Multiscale Approaches for Confining Ring Polymer Solutions. J. Phys. Chem. B 2021, 125, 4910.

(184) Zhang, J .; Meyer, H .; Virnau, P .; Daoulas, K. C. Can Soft Models Describe Polymer Knots? Macromolecules 2020, 53, 10475- 10486. (185) Wu, Z .; Alberti, S. A. N .; Schneider, J .; Müller-Plathe, F. Knotting behaviour of polymer chains in the melt state for soft-core models with and without slip-springs. J. Phys .: Cond. Matt. 2021, 33, 244001.

49

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(186) Masubuchi, Y. Simulating the Flow of Entangled Polymers. Annu. Rev. Chem. Biomol. Eng. 2014, 5, 11-33, DOI: 10.1146/annurev- chembioeng-060713-040401.

(187) Behbahani, A. F .; Schneider, L .; Rissanou, A .; Chazirakis, A .; Bacova, P .; Jana, P. K .; Li, W .; Doxastakis, M .; Polinska, P .; Burkhart, C .; Müller, M .; Harmandaris, V. A. Dynamics and Rheology of Polymer Melts via Hierarchical Atomistic, Coarse-Grained, and Slip-Spring Simulations. Macromolecules 2021, 54, 2740-2762.

(188) Padding, J .; Briels, W. Uncrossability constraints in mesoscopic polymer melt simulations: Non-Rouse behavior of C120H242. J. Chem. Phys. 2001, 115, 2846-2859.

(189) Schieber, J. Fluctuations in entanglements of polymer liquids. J. Chem. Phys. 2003, 118, 5162-5166.

(190) Likhtman, A. Single-chain slip-link model of entangled polymers: Simultaneous description of neutron spin-echo, rheology, and diffusion. Macromolecules 2005, 38, 6128-6139.

(191) Müller, M .; Daoulas, K. C. Single-chain dynamics in a homogeneous melt and a lamellar microphase: A comparison between Smart Monte Carlo dynamics, slithering-snake dynamics, and slip-link dynamics. J. Chem. Phys. 2008, 129, 164906.

(192) Steenbakkers, R. J. A .; Andreev, M .; Schieber, J. D. Thermodynamically consistent incorporation of entanglement spatial fluctuations in the slip-link model. Phys. Rev. E 2021, 103, 022501. (193) Uneyama, T .; Masubuchi, Y. Multi-chain slip-spring model for entangled polymer dynamics. J. Chem. Phys. 2012, 137, 154902. (194) Chappa, V. C .; Morse, D. C .; Zippelius, A .; Müller, M. Translationally Invariant Slip-Spring Model for Entangled Polymer Dynamics. Phys. Rev. Lett. 2012, 109, 148302.

(195) Ramirez-Hernandez, A .; Peters, B. L .; Andreev, M .; Schieber, J. D .; de Pablo, J. J. A multi-chain polymer slip-spring model with fluctuating number of entanglements for linear and nonlinear rheology. J. Chem. Phys. 2015, 143, 243147.

(196) Ramirez-Hernandez, A .; Peters, B. L .; Schneider, L .; Andreev, M .; Schieber, J. D .; Müller, M .; de Pablo, J. J. A multi-chain polymer slip-spring model with fluctuating number of entanglements: Density fluctuations, confinement, and phase separation. J. Chem. Phys. 2017, 146, 014903.

(197) Wu, Z .; Kalogirou, A .; de Nicola, A .; Milano, G .; Müller-Plathe, F. Atomistic hybrid particle-field molecular dynamics combined with slip-springs: Restoring entangled dynamics to simulations of polymer melts. J. Chem. Theory Comput. 2021, 42, 6-18.

(198) Wu, Z .; Milano, G .; Müller-Plathe, F. Combination of Hybrid Particle-Field Molecular Dynamics and Slip-Springs for the Efficient Simulation of Coarse-Grained Polymer Models: Static and Dynamic Properties of Polystyrene Melts. J. Chem. Theory Comput. 2021, 17, 474-487.

(199) Schneider, J .; Fleck, F .; Karimi-Varzaneh, H. A .; Müller-Plathe, F. Simulation of Elastomers by Slip-Spring Dissipative Particle Dynamics. Macromolecules 2021, 54, 5155-5166.

(200) Najafi, S .; Lin, Y .; Longhini, A. P .; Zhang, X .; Delaney, K. T .; Kosik, K. S .; Fredrickson, G. H .; Shea, J .- E .; Han, S. Liquid-liquid phase separation of Tau by self and complex coacervation. Protein Sci. 2021, 30, 1393-1407.

(201) Fredrickson, G. H.The Equilibrium Theory of Inhomogeneous Polymers; Oxford University Press: Oxford, 2013.

(202) Delaney, K. T .; Fredrickson, G. H. Recent Developments in Fully Fluctuating Field-Theoretic Simulations of polymer melts and solutions. J. Phys. Chem. B 2016, 120, 7615.

(203) Matsen, M. Field theoretic approach for block copolymer melts: SCFT and FTS. J. Chem. Phys. 2020, 152, 110901.

(204) Hong, K. M .; Noolandi, J. Theory of inhomogeneous multicomponent polymer systems. Macromolecules 1981, 14, 727-736. (205) Schmid, F. Self-consistent-field theories for complex fluids. J. Phys .: Cond. Matt. 1998, 10, 8105-8138.

(206) Schmid, F. Theory and Simulation of Multiphase Polymer Systems. InHandbook of Multiphase Polymer Systems; Wiley-Blackwell, 2011; Chapter 3, pp 31-80.

(207) Edwards, S. F. The theory of polymer solutions at intermediate concentration. Proc. Phys. Soc. 1966, 88, 265-280.

(208) Helfand, E. Theory of inhomogeneous polymers - Fundamen- tals of Gaussian random-walk model. J. Chem. Phys. 1975, 62, 999- 1005.

(209) Matsen, M. The standard Gaussian model for block copolymer melts. J. Phys .: Cond. Matt. 2002, 14, R21-R47.

(210) Kawasaki, T .; Sekimoto, K. Dynamic theory of polymer melt morphology. Physica A 1987, 143, 349-413.

(211) Kawasaki, K .; Sekimoto, K. Morphology dynamics of block copolymer systems. Physica A 1988, 148, 361-413.

(212) Fraaije, J. G. E. M. Dynamic Density Functional Theory for Microphase Separation Kinetics of Block Copolymer Melts. J. Chem. Phys. 1993, 99, 9202-9212.

(213) Fraaije, J. G. E. M .; van Vlimmeren, B. A. C .; Maurits, N. M .; Postma, M .; Evers, O. A .; Hoffmann, C .; Altevogt, P .; Goldbeck-Wood, G. The dynamic mean-field density functional method and its application to the mesoscopic dynamics of quenched block copolymer melts. J. Chem. Phys. 1997, 106, 4260-4269.

(214) Maurits, N. M .; Fraaije, J. G. E. M. Mesoscopic dynamics of copolymer melts: From density dynamics to external potential dynamics using nonlocal kinetic coupling. J. Chem. Phys. 1997, 107, 5879-5889.

(215) Kawakatsu, T .; Doi, M .; Hasegawa, R. Dynamic density functional approach to phase separation dynamics of polymer systems. Intn. J. Mod. Phys. C 1999, 10, 1531-1540.

(216) Morita, H .; Kawakatsu, T .; Doi, M. Dynamic density functional study on the structure of thin polymer blend films with a free surface. Macromolecules 2001, 34, 8777-8783.

(217) Reister, E .; Müller, M .; Binder, K. Spinodal decomposition in a binary polymer mixture: Dynamic self-consistent-field theory and Monte Carlo simulations. Phys. Rev. E 2001, 64, 041804.

(218) Müller, M .; Schmid, F. In Advanced computer simulation approaches for soft matter sciences II; Holm, C., Kremer, K., Eds .; Advances in Polymer Science; Springer, 2005; Vol. 185; pp 1-58.

(219) Qi, S .; Schmid, F. Dynamic Density Functional Theories for Inhomogeneous Polymer Systems Compared to Brownian Dynamics Simulations. Macromolecules 2017, 50, 9831-9845.

(220) Mantha, S .; Qi, S .; Schmid, F. Bottom-up Construction of Dynamic Density Functional Theories for Inhomogeneous Polymer Systems from Microscopic Simulations. Macromolecules 2020, 53, 3409-3423.

(221) Schmid, F .; Li, B. Dynamic Self-Consistent Field Approach for Studying Kinetic Processes in Multiblock Copolymer Melts. Polymers 2020, 12, 2205.

(222) Hohenberg, P. C .; Halperin, B. I. Theory of dynamic critical phenomena. Rev. Mod. Phys. 1977, 49, 435-479.

(223) Honda, T .; Kawakatsu, T. Hydrodynamic effects on the disorder-to-order transitions of diblock copolymer melts. J. Chem. Phys. 2008, 129, 114904.

(224) Maurits, N. M .; Zvelindovsky, A. V .; Sevink, G. J. A .; van Vlimmeren, B. A. C .; Fraaije, J. G. E. M. Hydrodynamic effects in three- dimensional microphase separation of block copolymers: Dynamic mean-field density functional approach. J. Chem. Phys. 1998, 108, 9150-9154.

(225) Zhang, L .; Sevink, A .; Schmid, F. Hybrid Lattice Boltzmann/ Dynamic Self-Consistent Field Simulations of Microphase Separation and Vesicle Formation in Block Copolymer Systems. Macromolecules 2011, 44, 9434-9447.

(226) Heuser, J .; Sevink, G. J. A .; Schmid, F. Self-Assembly of Polymeric Particles in Poiseuille Flow: A Hybrid Lattice Boltzmann/ External Potential Dynamics Simulation Study. Macromolecules 2017, 50, 4474-4490.

(227) Hamm, M .; Goldbeck-Wood, G .; Zvelindovsky, A .; Sevink, G .; Fraaije, J. Structure formation in liquid crystalline polymers. J. Chem. Phys. 2002, 116, 3152-3161.

(228) Wang, G .; Ren, Y .; Müller, M. Collective short-time dynamics in multicomponent polymer melts. Macromolecules 2019, 52, 7704-7720. (229) Rottler, J .; Müller, M. Efficient pathways of block copolymer directed self-assembly: Insights from efficient continuum modeling. ACS Nano 2020, 14, 13986-13994.

50

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(230) Ganesan, V .; Fredrickson, G. Field-theoretic polymer simulations. EPL 2001, 55, 814-820.

(231) Lindsay, B. J .; Composto, R. J .; Riggleman, R. A. Equilibrium Field Theoretic Study of Nanoparticle Interactions in Diblock Copolymer Melts. J. Phys. Chem. B 2019, 123, 9466-9480.

(232) McCarty, J .; Delaney, K. T .; Danielsen, S. P. O .; Fredrickson, G. H .; Shea, J .- E. Complete Phase Diagram for Liquid-Liquid Phase Separation of Intrinsically Disordered Proteins. J. Phys. Chem. Lett. 2019, 10, 1644-1652.

(233) Vorselaars, B .; Spencer, R. K. W .; Matsen, M. W. Instability of the Microemulsion Channel in Block Copolymer-Homopolymer Blends. Phys. Rev. Lett. 2020, 125, 117801.

(234) Spencer, R. K. W .; Matsen, M. W. Coexistence of Polymeric Microemulsion with Homopolymer-Rich Phases. Macromolecules 2021, 54, 1329-1337.

(235) Matsen, M. W .; Beardsley, T. M. Field-Theoretic Simulations for Block Copolymer Melts Using the Partial Saddle-Point Approx- imation. Polymers 2021, 13, 2437.

(236) Düchs, D .; Ganesan, V .; Fredrickson, G. H .; Schmid, F. Fluctuation Effects in Ternary AB+A+B Polymeric Emulsions. Macromolecules 2003, 36, 9237-9248.

(237) Düchs, D .; Schmid, F. Formation and structure of the microemulsion phase in two-dimensional ternary AB+A+B polymeric emulsions. J. Chem. Phys. 2004, 121, 2798-2805.

(238) Beardsley, T. M .; Matsen, M. W. Fluctuation correction for the order-disorder transition of diblock copolymer melts. J. Chem. Phys. 2021, 154, 124902.

(239) Alexander-Katz, A .; Fredrickson, G. Diblock Copolymer Thin Films: A Field-Theoretic Simulation Study. Macromolecules 2007, 40, 4075-4087. (240) Zappalá, D. Indications of isotropic Lifshitz points in four dimensions. Phys. Rev. D 2018, 98, 085005.

(241) Brunk, A .; Lukáčová-Medviďová, M. Global existence of weak solutions to viscoelastic phase separation: part II. Degenerate case. Nonlinearity 2022, 35, 3459-3486.

(242) Han, C. D.Rheology and Processing of Polymeric Materials, Vol. 2: Polymer Processing; Oxford University Press: Oxford, 2006.

(243) Tanaka, H. Viscoelastic phase separation. J. Phys .: Cond. Matt. 2000, 12, R207-R264.

(244) Geyer, S .; Piesche, M. Macro and Micro-Scale Modeling of Polyurethane Foaming Processes. AIP Conf. Proc. 2014, 1593, 560- 564.

(245) Obi, B.Polymeric Foams: Structure-Property-Performance: A Design Guide; Elsevier, 2017.

(246) Heinrich, G., Kipscholl, R., Stocek, R., Eds. Fatigue Crack Growth in Rubber Materials; Advances in Polymer Science; Springer: Hoboken, 2021.

(247) Anderson, D .; Carlson, D .; Fried, E. A continuum-mechanical theory for nematic elastomers. J. Elasticity 1999, 56, 33-58.

(248) Hong, W .; Zhao, X .; Suo, Z. Large deformation and electrochemistry of polyelectrolyte gels. J. Mech. Phys. Solids 2010, 58, 558-577. (249) Borja, R. I.Plasticity: Modelling & Computation; Springer: Berlin, Heidelberg, New York, 2013.

(250) Narijauskaitė, B .; Palevičius, A .; Gaidys, R .; Janušas, G .; Šakalys, R. Polycarbonate as an elasto-plastic material model for simulation of the microstructure hot imprint process. Sensors 2013, 13, 11229- 11242.

(251) Miehe, C .; Aldakheel, F .; Raina, A. Phase field modeling of ductile fracture at finite strains: A variational gradient-extended plasticity-damage theory. Intnl. J. Plasticity 2016, 84, 1-32.

(252) Aranda-Ruiz, J .; Ravi-Chandar, K .; Loya, J. A. On the double transition in the failure mode of polycarbonate. Mech. Mater. 2020, 140, 103242.

(253) Wang, Y .; Huang, Z. Analytical Micromechanics Models for Elastoplastic Behavior of Long Fibrous Composites: A Critical Review and Comparative Study. Materials 2018, 11, 1919.

(254) David Müzel, S .; Bonhin, E. P .; Guimarães, N. M .; Guidi, E. S. Application of the finite element method in the analysis of composite materials: A review. Polymers 2020, 12, 818.

(255) Beris, A. N. Continuum mechanics modeling of complex fluid systems following Oldroyd's seminal 1950 work. J. Non-Newtonian Fluid Mech. 2021, 298, 104677.

(256) Masmoudi, N. Global existence of weak solutions to macroscopic models of polymeric flows. J. Math. Pures et Appliquees 2011, 96, 502-520.

(257) Peterlin, A. Hydrodynamics of linear macromolecules. J. Pure and Appl. Chem. 1966, 12, 563-586.

(258) Peterlin, A. Hydrodynamics of macromolecules in a velocity field with longitudinal gradient. J. Polym. Sci. B - Polym. Lett. 1966, 4, 287.

(259) De Groot, S. R .; Mazur, P.Non-Equilibrium Thermodynamics; Dover Publications: New York, 1984.

(260) Schieber, J. D .; Córdoba, A. Nonequilibrium thermodynamics for soft matter made easy(er). Phys. Fluids 2021, 33, 083103.

(261) Öttinger, H. C.Beyond Equilibrium Thermodynamics; Wiley, 2005.

(262) Lukáčová-Medviďová, M .; Mizerová, H .; Nečasová, v .; Renardy, M. Global Existence Result for the Generalized Peterlin Viscoelastic Models. Siam J. Math. Anal. 2017, 49, 2950-2964.

(263) Gwiazda, P .; Lukáčová-Medviďová, M .; Mizerová, H .; Świerczewska Gwiazda, A. Existence of global weak solutions to the kinetic Peterlin model. Nonlinear Analysis: Real World Applications 2018, 44, 465-478.

(264) Tateno, M .; Tanaka, H. Power-law coarsening in network- forming phase separation governed by mechanical relaxation. Nat Commun. 2021, 12, 912.

(265) Tanaka, H. Unusual Phase Separation in a Polymer Solution Caused by Asymmetric Molecular Dynamics. Phys. Rev. Lett. 1993, 71, 3158-3161.

(266) Tanaka, H. Universality of Viscoelastic Phase Separation in Dynamically Asymmetric Fluid Mixtures. Phys. Rev. Lett. 1996, 76, 787. (267) Taniguchi, T .; Onuki, A. Network Domain Structure in Viscoelastic Phase Separation. Phys. Rev. Lett. 1996, 77, 4910-4913. (268) Tanaka, H. Viscoelastic model of phase separation. Phys. Rev. E 1997, 56, 4451-4462.

(269) Zhou, D .; Zhang, P .; E, W. Modified models of polymer phase separation. Phys. Rev. E 2006, 73, 061801.

(270) Spiller, D .; Brunk, A .; Habrich, O .; Egger, H .; Lukáčová- Medviď'ová, M .; Dünweg, B. J. Phys .: Cond. Matt 2021, 33, 364001. (271) Brunk, A .; Dünweg, B .; Egger, H .; Habrich, O .; Lukáčová- Medviď'ová, M .; Spiller, D. J. Phys .: Cond. Matt 2021, 33, 234002. (272) Doi, M .; Onuki, A. Dynamic coupling between stress and composition in polymer solutions and blends. J. de Physique II 1992, 2, 1631-1656.

(273) Milner, S. T. Dynamical theory of concentration fluctuations in polymer solutions under shear. Phys. Rev. E 1993, 48, 3674-3691. (274) Brunk, A .; Lukáčová-Medviďová, M. Global existence of weak solutions to viscoelastic phase separation part: I. Regular case. Nonlinearity 2022, 35, 3417-3458.

(275) Bonomi, M .; Camilloni, C .; Cavalli, A .; Vendruscolo, M. Metainference: ABayesian inference method for heterogeneous systems. Science Advances 2016, 2, 1501177.

(276) Rudzinski, J. F .; Kremer, K .; Bereau, T. Communication: Consistent interpretation of molecular simulation kinetics using Markov state models biased with external information. J. Chem. Phys. 2016, 144, 051102.

(277) Frohlking, T .; Bernetti, M .; Calonaci, N .; Bussi, G. Toward empirical force fields that match experimental observables. J. Chem. Phys. 2020, 152, 230902.

(278) Miksch, A. M .; morawietz, T .; Kästner, J .; Urban, A .; Artrith, N. Strategies for the construction of machine-learning potentials for accurate and efficient atomic-scale simulations. Mach. Learn .: Sci. Technol. 2021, 2, 031001.

(279) Mori, H. Transport, collective motion, and Brownian motion. Prog. Theor. Phys. 1965, 33, 423.

51

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(280) Mori, H. A Continued-Fraction Representation of the Time- Correlation Functions. Prog. Theor. Phys. 1965, 34, 399-416. (281) Zwanzig, R. Memory effects in irreversible thermodynamics. Phys. Rev. 1961, 124, 983.

(282) Forster, D.Hydrodynamic fluctuations, broken symmetry, and correlation functions; CRC Press: Boca Raton, 1975.

(283) Boon, J. P., Yip, S.Molecular hydrodynamics; Dover Publications: New York, 1980.

(284) Español, P .; Löwen, H. Derivation of dynamical density functional theory using the projection operator technique. J. Chem. Phys. 2009, 131, 244101.

(285) Hijón, C .; Español, P .; Vanden-Eijnden, E .; Delgado- Buscalioni, R. Mori-Zwanzig formalism as a practical computational tool. Faraday Discuss. 2010, 144, 301-322.

(286) Glatzel, F .; Schilling, T. The Interplay between Memory and Potentials of Mean Force: A Discussion on the Structure of Equations of Motion for Coarse-Grained Observables. EPL 2021, 136, 36001. (287) Zwanzig, R.Nonequilibrium Statistical Mechanics; Oxford University Press: New York, 2001.

(288) Vroylandt, H .; Monmarché, P. Position-dependent memory kernel in generalized Langevin equations: Theory and numerical estimation. J. Chem. Phys. 2022, 156, 244105.

(289) Rühle, V .; Junghans, C .; Lukyanov, A .; Kremer, K .; Andrienko,

D. J. Chem. Theory Comput. 2009, 5, 3211-3223.

(290) Lyubartsev, A. P .; Laaksonen, A. Calculation of effective interaction potentials from radial distribution functions: A reverse Monte Carlo approach. Phys. Rev. E 1995, 52, 3730-3737.

(291) Soper, A. K. Empirical potential Monte Carlo simulation of fluid structure. Chem. Phys. 1996, 202, 295-306.

(292) Reith, D .; Pütz, M .; Müller-Plathe, F. Deriving effective mesoscale potentials from atomistic simulations. J. Comput. Chem. 2003, 24, 1624-1636.

(293) Ganguly, P .; Mukherji, D .; Junghans, C .; van der Vegt, N. F. A. Kirkwood-Buff Coarse-Grained Force Fields for Aqueous Solutions. J. Chem. Theory Comput. 2012, 8, 1802-1807.

(294) de Oliveira, T. E .; Netz, P. A .; Kremer, K .; Junghans, C .; Mukherji, D. C-IBI: Targeting cumulative coordination within an iterative protocol to derive coarse-grained models of (multi- component) complex fluids. J. Chem. Phys. 2016, 144, 174106.

(295) Hanke, M. Well-Posedness of the Iterative Boltzmann Inversion. J. Stat. Phys. 2018, 170, 536-553.

(296) Ercolessi, F .; Adams, J. B. Interatomic Potentials from First- Principles Calculations: The Force-Matching Method. EPL 1994, 26, 583-588.

(297) Izvekov, S .; Voth, G. A. A Multiscale Coarse-Graining Method for Biomolecular Systems. J. Phys. Chem. B 2005, 109, 2469-2473. (298) Izvekov, S .; Voth, G. A. Multiscale coarse graining ofliquid-state systems. J. Chem. Phys. 2005, 123, 134105.

(299) Noid, W. C .; Chu, J .- W .; Ayton, G. S .; Krishna, V .; Izvekov, S .; Voth, G. A .; Andersen, H. C. The multiscale coarse-graining method. I. A rigorous bridge between atomistic and coarse-grained models. J. Chem. Phys. 2008, 128, 244114.

(300) Noid, W. C .; Liu, P .; Wang, Y .; Chu, J .- W .; Ayton, G. S .; Izvekov, S .; Andersen, H. C .; Voth, G. A. The multiscale coarse-graining method. II. Numerical implementation for coarse-grained molecular models. J. Chem. Phys. 2008, 128, 244115.

(301) Shell, M. S. The relative entropy is fundamental to multiscale and inverse thermodynamic problems. J. Chem. Phys. 2008, 129, 144108. (302) Mullinax, J. W .; Noid, W. G. Generalized Yvon-Born-Green Theory for Molecular Systems. Phys. Rev. Lett. 2009, 103, 198104. (303) Mullinax, J. W .; Noid, W. G. A Generalized-Yvon-Born-Green Theory for Determining Coarse-Grained Interaction Potentials. J. Phys. Chem. C 2010, 114, 5661-5674.

(304) Wörner, S. J .; Bereau, T .; Kremer, K .; Rudzinski, J. F. Direct route to reproducing pair distribution functions with coarse-grained models via transformed atomistic cross correlations. J. Chem. Phys. 2019, 151, 244110.

(305) Wang, J .; Olsson, S .; Wehmeyer, C .; Pŕez, A .; Charron, N. E .; de Fabritiis, G .; Noé, F .; Clementi, C. Machine Learning of Coarse- Grained Molecular Dynamics Force Fields. ACS Cent. Sci. 2019, 5, 755-767.

(306) Berressem, F .; Nikoubashman, A. BoltzmaNN: Predicting effective pair potentials and equations of state using neural networks. J. Chem. Phys. 2021, 154, 124123.

(307) Mullinax, J. W .; Noid, W. G. Extended ensemble approach for deriving transferable coarse-grained potentials. J. Chem. Phys. 2009, 131, 104110.

(308) Dunn, N. J. H .; Noid, W. G. Bottom-up coarse-grained models with predictive accuracy and transferability for both structural and thermodynamic properties of heptane-toluene mixtures. J. Chem. Phys. 2016, 144, 204124.

(309) Rosenberger, D .; Hanke, M .; van der Vegt, N. F. A. Comparison of iterative inverse coarse-graining methods. Eur. Phys. J. - Spec. Topics 2016, 225, 1323-1345.

(310) Henderson, R. A uniqueness theorem for fluid pair correlation functions. Phys. Lett. A 1974, 99, 197.

(311) Frommer, F .; Hanke, M .; Jansen, S. A note on the uniqueness result for the inverse Henderson problem. J. Math. Physics 2019, 60, 093303.

(312) Frommer, F .; Hanke, M. A variational framework for the inverse Henderson problem of statistical mechanics. Letters in Mathematical Physics 2022, 112, 71.

(313) Ruelle, D.Statistical Mechanics: Rigorous Results; W. A. Benjamin Publisher: New York, 1969.

(314) Villa, A .; Peter, C .; van der Vegt, N. F. A. Transferability of Nonbonded Interaction Potentials for Coarse-Grained Simulations: Benzene in Water. J. Chem. Theory Comput. 2010, 6, 2434-2444. (315) Delbary, F .; Hanke, M .; Ivanizki, D. A generalized Newton iteration for computing the solution of the inverse Henderson problem. Inverse Problems in Science and Engineering 2020, 28, 1166-1190.

(316) Bernhardt, M. P .; Hanke, M .; van der Vegt, N. Iterative integral equation methods for structural coarse-graining. J. Chem. Phys. 2021, 154, 084118.

(317) Cortes-Huerto, R .; Kremer, K .; Potestio, R. Communication: Kirkwood-Buff integrals in the thermodynamic limit from small-sized molecular dynamics simulations. J. Chem. Phys. 2016, 145, 141103. (318) Sevilla, M .; Cortes-Huerto, R. Connecting density fluctuations and Kirkwood-Buff integrals for finite-size systems. J. Chem. Phys. 2022, 156, 044502.

(319) Phuong, N. H .; Germano, G .; Schmid, F. Elastic constants from direct correlation functions in nematic liquid crystals: A computer simulation study. J. Chem. Phys. 2001, 115, 7227-7234.

(320) Phuong, N. H .; Schmid, F. Local structure in nematic and isotropic liquid crystals. J. Chem. Phys. 2003, 119, 1214-1222.

(321) Lebold, K. M .; Noid, W. G. Dual approach for effective potentials that accurately model structure and energetics. J. Chem. Phys. 2019, 150, 234107.

(322) Lebold, K. M .; Noid, W. G. Dual-potential approach for coarse- grained implicit solvent models with accurate, internally consistent energetics and predictive transferability. J. Chem. Phys. 2019, 151, 164113.

(323) Szukalo, R. J .; Noid, W. G. Investigating the energetic and entropic components of effective potentials across a glass transition. J. Phys .: Cond. Matt. 2021, 33, 154004.

(324) Molinero, V .; Moore, E. B. Water modeled as an intermediate element between Carbon and Silicon. J. Phys. Chem. B 2009, 113, 4008-4016.

(325) Larini, L .; Lu, L .; Voth, G. A. The multiscale coarse-graining method. VI. Implementation of three-body coarse-grained potentials. J. Chem. Phys. 2010, 132, 164107.

(326) Das, A .; Andersen, H. C. The multiscale coarse-graining method. IX. A general method for construction of three body coarse- grained force fields. J. Chem. Phys. 2012, 136, 194114.

(327) Scherer, C .; Andrienko, D. Understanding three-body contributions to coarse-grained force-fields. Phys. Chem. Chem. Phys. 2018, 20, 22387.

52

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(328) Glielmo, A .; Zeni, C .; De Vita, A. Efficient nonparametric n- body force fields from machine learning. Phys. Rev. B 2018, 97, 184307. (329) Allen, E. C .; Rutledge, G. C. A novel algorithm for creating coarse-grained, density dependent implicit solvent models. J. Chem. Phys. 2008, 128, 154115.

(330) Moore, J. D .; Barnes, B. C .; Izvekov, S .; Lísal, M .; Sellers, M. S .; Taylor, D. E .; Brennan, J. K. A coarse-grain force field for RDX: Density dependent and energy conserving. J. Chem. Phys. 2016, 144, 104501. (331) Sanyal, T .; Shell, M. S. Coarse-grained models using local- density potentials optimized with the relative entropy: Application to implicit solvation. J. Chem. Phys. 2016, 145, 034109.

(332) Sanyal, T .; Shell, M. S. Transferable Coarse-Grained Models of Liquid-Liquid Equilibrium Using Local Density Potentials Optimized with the Relative Entropy. J. Phys. Chem. A 2018, 122, 5678-5693. (333) Dama, J. F .; Jin, J .; Voth, G. A. The Theory of Ultra-Coarse- Graining. 3. Coarse-Grained Sites with Rapid Local Equilibrium of Internal States. J. Rheol. 2017, 13, 1010-1022.

(334) Delyser, M. R .; Noid, W. G. Extended pressure-matching to inhomogeneous systems via local-density potentials. J. Chem. Phys. 2017, 147, 134111.

(335) Montes-Saralegui, M .; Kahl, G .; Nikoubashman, A. On the applicability of density dependent effective interactions in cluster- forming systems. J. Chem. Phys. 2017, 146, 054904.

(336) Delyser, M. R .; Noid, W. G. Analysis of local density potentials. J. Chem. Phys. 2017, 147, 134111.

(337) Rosenberger, D .; Sanyal, T .; Shell, M. S .; van der Vegt, N. F. A. Transferability of Local Density-Assisted Implicit Solvation Models for Homogeneous Fluid Mixtures. J. Chem. Theory Comput. 2019, 15, 2881-2895.

(338) Berressem, F .; Scherer, C .; Andrienko, D .; Nikoubashman, A. Ultra-coarse-graining of homopolymers in inhomogeneous systems. J. Phys .: Cond. Matt. 2021, 33, 254002.

(339) John, S .; Csányi, G. Many-Body Coarse-Grained Interactions Using Gaussian Approximation Potentials. J. Phys. Chem. B 2017, 121, 10934-10949.

(340) Jin, J .; Voth, G. A. Ultra-Coarse-Grained Models Allow for an Accurate and Transferable Treatment of Interfacial Systems. J. Chem. Theory Comput. 2018, 14, 2180-2197.

(341) Baul, U .; Dzubiella, J. Structure and dynamics of responsive colloids with dynamical polydipersity. J. Phys .: Condens. Matter 2021, 33, 174002.

(342) Cisneros, G. A .; Wikfeldt, K. T .; Ojamäe, L .; Lu, J .; Xu, Y .; Torabifard, H .; Bartók, A. P .; Csányi, G .; Molinero, V .; Paesani, F. Modeling Molecular Interactions in Water: From Pairwise to Many- Body Potential Energy Functions. Chem. Rev. 2016, 116, 7501-7528. (343) Stillinger, F. H .; Weber, T. A. Computer simulation of local order in condensed phases of silicon. Phys. Rev. B 1985, 31, 5262. (344) Stillinger, F. H .; Weber, T. A. Erratum: Computer simulation of local order in condensed phases of silicon. Phys. Rev. B 1986, 33, 1451. (345) Scherer, C .; Scheid, R .; Andrienko, D .; Bereau, T. Kernel-Based Machine Learning for Efficient Simulations of Molecular Liquids. J. Chem. Theory Comput. 2020, 16, 3194-3204.

(346) Bereau, T .; Rudzinski, J. F. Accurate Structure-Based Coarse Graining Leads to Consistent Barrier-Crossing Dynamics. Phys. Rev. Lett. 2018, 121, 256002.

(347) Rudzinski, J. F .; Bereau, T. Coarse-grained conformational surface hopping: Methodology and transferability. J. Chem. Phys. 2020, 153, 214110. (348) Sharp, M. E .; Vazquez, F. X .; Wagner, J. W .; Dannenhoffer- Lafage, T .; Voth, G. A. Multiconfigurational Coarse-Grained Molecular Dynamics. J. Chem. Theory Comput. 2019, 15, 3306-3315. (349) van der Haven, D. L. H .; Köhler, S .; Schreiner, E .; in 't Veld, P. J. Closed-Form Coexistence Equation for Phase Separation of Polymeric Mixtures in Dissipative Particle Dynamics. J. Phys. Chem. B 2021, 125, 7485-7498.

(350) Español, P .; Revenga, M. Smoothed dissipative particle dynamics. Phys. Rev. E 2003, 67, 026705.

(351) Flory, P. J.Statistical Mechanics of Chain Molecules; Wiley, 1969.

(352) Glaser, J .; Medapuram, P .; Beardsley, T. M .; Matsen, M. W .; Morse, D. C. Universality of Block Copolymer Melts. Phys. Rev. Lett. 2014, 113, 068302.

(353) Beardsley, T. M .; Matsen, M. W. Universality between experiment and simulation of a diblock copolymer melt. Phys. Rev. Lett. 2016, 117, 217801.

(354) Glaser, J .; Qin, J .; Medapuram, P .; Morse, D. C. Collective and Single-Chain Correlations in Disordered Melts of Symmetric Diblock Copolymers: Quantitative Comparison of Simulations and Theory. Macromolecules 2014, 47, 851-869.

(355) Willis, J. D .; Beardsley, T. M .; Matsen, M. W. Simple and Accurate Calibration of the Flory-Huggins Interaction Parameter. Macromolecules 2020, 53, 9973-9982.

(356) Curro, J. G .; Schweizer, K. S. Theory for the chi parameter of polymer blends - effect of attractive interactions. J. Chem. Phys. 1988, 88, 7242-7243.

(357) Schweizer, K., Curro, J. In Advances in Chemical Physics; Prigogine, I., Rice, S., Eds .; Wiley; 1997; Vol. 98; pp 1-142.

(358) Dudowicz, J .; Freed, K. F. Relation of effective interaction parameters for binary blends and diblock copolymers - lattice cluster theory predictions and comparisons with experiment. Macromolecules 1993, 26, 213-220.

(359) Freed, K. F .; Dudowicz, J. A lattice-model molecular theory for the properties of polymer blends. Trends Polym. Sci. 1995, 3, 248-255. (360) Foreman, K .; Freed, K. Adv. Chem. Phys. 2007, 103, 335-390. (361) Singh, C .; Schweizer, K. S. Correlation-effects and entropy- driven phase-separation in athermal polymer blends. J. Chem. Phys. 1995, 103, 5814-5832.

(362) Singh, C .; Schweizer, K. Coupled enthalpic-packing effects on the miscibility of conformationally asymmetric polymer blends. Macromolecules 1997, 30, 1490-1508.

(363) Fredrickson, G. H .; Liu, A. J .; Bates, F. S. Entropic corrections to the Flory-Huggins theory of polymer blends - Architectural and conformational effects. Macromolecules 1994, 27, 2503-2511.

(364) Wang, Z .- G. Concentration fluctuation in binary polymer blends: chi parameter, spinodal and Ginzburg criterion. J. Chem. Phys. 2002, 117, 481-500.

(365) Müller, M .; Binder, K. Computer-simulation of asymmetric polymer mixtures. Macromolecules 1995, 28, 1825-1834.

(366) Müller, M. Effects of structural disparities in polymer blends - A Monte Carlo investigation. Macromolecules 1995, 28, 6556-6564. (367) Flory, P. Thermodynamics of high polymer solutions. J. Chem. Phys. 1941, 9, 660-661.

(368) Huggins, M. L. Solutions of long chain compounds. J. Chem. Phys. 1941, 9, 440-661.

(369) de Nicola, A .; Zhao, Y .; Kawakatsu, T .; Roccatano, D .; Milano, G. Hybrid Particle-Field Coarse-Grained Models for Biological Phospholipids. J. Chem. Theory Comput. 2011, 7, 2947-2962. (370) de Nicola, A .; Kawakatsu, T .; Milano, G. A Hybrid Particle- Field Coarse-Grained Molecular Model for Pluronics Water Mixtures. Macromol. Chem. Phys. 2013, 214, 1940-1950.

(371) Ledum, M .; Bore, S. L .; Cascella, M. Automated determination of hybrid particle-field parameters by machine learning. Mol. Phys. 2020, 118, e1785571.

(372) Sherck, N .; Shen, K .; Nguyen, M .; Yoo, B .; Kohler, S .; Speros, J. C .; Delaney, K. T .; Shell, M. S .; Fredrickson, G. H. Molecularly Informed Field Theories from Bottom-up Coarse-Graining. ACS Macro Lett. 2021, 10, 576-583.

(373) Weyman, A .; Mavrantzas, V. G .; Öttinger, H. C. Field-theoretic simulations beyond 8-interactions: Overcoming the inverse potential problem in auxiliary field models. J. Phys. Chem. 2021, 155, 024106. (374) Rudzinski, J. R .; Kloth, S .; Wörner, S .; Pal, T .; Kremer, K .; Bereau, T .; Vogel, M. Dynamical properties across different coarse- grained models for ionic liquids. J. Phys .: Cond. Matt. 2021, 33, 224001. (375) Padding, J. T .; Louis, A. A. Hydrodynamic interactions and Brownian forces in colloidal systems: Coarse-graining over time and length scales. Phys. Rev. E 2006, 74, 031402.

(376) Kloth, S .; Bernhardt, M. P .; van der Vegt, N. F. A .; Vogel, M. Coarse-grained model of a nanoscale-segregated ionic liquid for

53

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

simulations of low-temperature structure and dynamics. J. Phys .: Condens. Matter 2021, 32, 204002.

(377) Harmandaris, V. A .; Adhikari, N. P .; van der Vegt, N. F. A .; Kremer, K. Hierarchical Modeling of Polystyrene: From Atomistic to Coarse-grained Simulations. Macromolecules 2006, 39, 6708-6719. (378) Harmandaris, V. A .; Kremer, K. Dynamics of Polystyrene Melts through Hierarchical Multiscale Simulations. Macromolecules 2009, 42, 791-802.

(379) Fritz, D .; Herbers, C. R .; Kremer, K .; van der Vegt, N. F. A. Hierarchical modeling of polymer permeation. Soft Matter 2009, 5, 4556-4563.

(380) Fritz, D .; Koschke, K .; Harmandaris, V. A .; van der Vegt, N. F. A .; Kremer, K. Multiscale modeling of soft matter: scaling of dynamics. Phys. Chem. Chem. Phys. 2011, 13, 10412-10420.

(381) Salerno, K. M .; Agrawal, A .; Perahia, D .; Grest, G. S. Resolving Dynamic Properties of Polymers through Coarse-Grained Computa- tional Studies. Phys. Rev. Lett. 2016, 116, 058302.

(382) Peters, B. L .; Salerno, K. M .; Agrawal, A .; Perahia, D .; Grest, G. S. Coarse-Grained Modeling of Polyethylene Melts: Effect on Dynamics. J. Chem. Theory Comput. 2017, 13, 2890-2896.

(383) Rudzinski, J. F .; Bereau, T. Concurrent parametrization against static and kinetic information leads to more robust coarse-grained force fields. Eur. Phys. J. - Spec. Topics 2016, 225, 1373-1389.

(384) Giri, R. K .; Swaminathan, N. Role of mapping schemes on dynamical and mechanical properties of coarse-grained models of cis- 1,4-polyisoprene. Comput. Mater. Sci. 2022, 208, 111309.

(385) Xia, W .; Song, J .; JEong, C .; Hsu, D. D .; Phelan, F. R. J .; Douglas, J. F .; Keten, S. Energy-renormalization fo achieving temperature-transferable coarse-graining of polymer dynamics. Macro- molecules 2017, 50, 8787-8796.

(386) Song, J .; Hsu, D. D .; Shull, K. R .; Phelan, F. R., Jr .; Douglas, J. F .; Xia, W .; Keten, S. Energy Renormalization Method for the Coarse- Graining of Polymer Viscoelasticity. Macromolecules 2018, 51, 3818- 3827.

(387) Xia, W .; Hansoge, N. K .; Xu, W .- S .; Phelan, F. R., Jr .; Keten, S .; Douglas, J. F. Energy renormalization for coarse-graining polymers having different segmental structures. Science Advances 2019, 5, eaav4683.

(388) Akkermans, R. L. C .; Briels, W. J. Coarse-grained dynamics of one chain in a polymer melt. J. Chem. Phys. 2000, 113, 6409-6422. (389) Helfand, E .; Rice, S. A. Principle of corresponding states for transport properties. J. Chem. Phys. 1960, 32, 1642-1644.

(390) Hansen, J .- P .; McDonald, I. R.Theory of simple liquids; Academic Press: London, 1990.

(391) Rosenfeld, Y. Relation between the transport coefficients and the internal entropy of simple systems. Phys. Rev. A 1977, 15, 2545. (392) Rosenfeld, Y. A quasi-universal scaling law for atomic transport in simple fluids. J. Phys .: Cond. Matt. 1999, 11, 5415.

(393) Rondina, G. G .; Boehm, M. C .; Müller-Plathe, F. Predicting the Mobility Increase of Coarse-Grained Polymer Models from Excess Entropy Differences. J. Chem. Theory Comput. 2020, 16, 1431-1447.

(394) Lyubimov, I .; McCarty, J .; Clark, A .; Guenza, M. G. Analytical rescaling of polymer dynamics from mesoscale simulations. J. Chem. Phys. 2010, 132, 224903.

(395) Lyubimov, I .; Guenza, M. G. First-principle approach to rescale the dynamics of simulated coarse-grained molecular liquids. Phys. Rev. E 2011, 84, 031801.

(396) Lyubimov, I .; Guenza, M. G. Theoretical reconstruction of realistic dynamics of highly coarse-grained cis-1,4-polybutadiene melts. J. Chem. Phys. 2013, 138, 12A546.

(397) Schweizer, K. S. Microscopic theory of the dynamics of polymeric liquids: General formulation of a mode-mode-coupling approach. J. Chem. Phys. 1989, 91, 5802.

(398) Ge, T .; Wang, J .; Robbins, M. O. Effects of Coarse-Graining on Molecular Properties of Glassy Polymers. Macromolecules 2021, 54, 2277-2287.

(399) Wang, J .; In't Veld, P. J .; Robbins, M. O .; Ge, T. Effects of Coarse-Graining on Molecular Simulation of Craze Formation in Polymer Glass. Macromolecules 2022, 55, 1267-1278.

(400) Li, Z .; Bian, X .; Caswell, B .; Karniadakis, G. E. Construction of dissipative particle dynamics models for complex fluids via the Mori- Zwanzig formulation. Soft Matter 2014, 10, 8659-8672.

(401) Trement, S .; Schnell, B .; Petitjean, L .; Couty, M .; Rousseau, B. Conservative and dissipative force field for simulation of coarse-grained alkane molecules: A bottom-up approach. J. Chem. Phys. 2014, 140, 134113.

(402) Lemarchand, C. A .; Couty, M .; Rousseau, B. Coarse-grained simulations of cis- and trans-polybutadiene: A bottom-up approach. J. Chem. Phys. 2017, 146, 074904.

(403) Deichmann, G .; van der Vegt, N. F. A. Bottom-up approach to represent dynamic properties in coarse-grained molecular simulations. J. Chem. Phys. 2018, 149, 244114.

(404) van den Noort, A .; den Otter, W. K .; Briels, W. J. Coarse graining of slow variables in dynamic simulations of soft matter. EPL 2007, 80, 28003.

(405) Briels, W. J. Transient forces in flowing soft matter. Soft Matter 2009, 5, 4401-4411.

(406) Liu, L .; den Otter, W. K .; Briels, W. J. Coarse grain forces in star polymer melts. Soft Matter 2014, 10, 7874-7886.

(407) Ahuja, V. R .; van der Gucht, J .; Briels, W. J. Hydrodynamically Coupled Brownian Dynamics: A coarse-grain particle-based Brownian dynamics technique with hydrodynamic interactions for modeling self- developing flow of polymer solutions. J. Chem. Phys. 2018, 148, 034902. (408) Kinjo, T .; Hyodo, S. Equation of motion for coarse-grained simulation based on microscopic description. Phys. Rev. E 2007, 75, 051109.

(409) Jung, G .; Schmid, F. Fluctuation-dissipation relations far from equilibrium: a case study. Soft Matter 2021, 17, 6413-6425.

(410) Straub, J. E .; Borkovec, M .; Berne, B. J. Calculation of dynamic friction on intramolecular degrees of freedom. J. Phys. Chem. 1987, 91, 4995-4998.

(411) Straub, J. E .; Berne, B. J .; Roux, B. Spatial dependence of time- dependent friction for pair diffusion in a simple fluid. J. Chem. Phys. 1990, 93, 6804-6812.

(412) Shin, H. K .; Kim, C .; Talkner, P .; Lee, E. K. Brownian motion from molecular dynamics. Chem. Phys. 2010, 375, 316-326.

(413) Carof, A .; Vuilleumier, R .; Rotenberg, B. Two algorithms to compute projected correlation functions in molecular dynamics simulations. J. Chem. Phys. 2014, 140, 124103.

(414) Lei, H .; Baker, N. A .; Li, X. Data-driven parameterization of the generalized Langevin equation. Proc. Natl. Acad. Sci. U.S.A. 2016, 113, 14183-14188.

(415) Jung, G .; Hanke, M .; Schmid, F. Iterative Reconstruction of Memory Kernels. J. Chem. Theory Comput. 2017, 13, 2481-2488.

(416) Jung, G .; Hanke, M .; Schmid, F. Generalized Langevin dynamics: construction and numerical integration of non-Markovian particle-based models. Soft Matter 2018, 14, 9368-9382.

(417) Kowalik, B .; Daldrop, J. O .; Kappler, J .; Schulz, J. C. F .; Schlaich, A .; Netz, R. R. Memory-kernel extraction for different molecular solutes in solvents of varying viscosity in confinement. Phys. Rev. E 2019, 100, 012126.

(418) Meyer, H .; Pelagejcev, P .; Schilling, T. Non-Markovian out-of- equilibrium dynamics: A general numerical procedure to construct time-dependent memory kernels for coarse-grained observables. EPL 2019, 128, 40001.

(419) Meyer, H .; Wolf, S .; Stock, G .; Schilling, T. A Numerical Procedure to Evaluate Memory Effects in Non-Equilibrium Coarse- Grained Models. Adv. Theory Sim. 2021, 4, 2000197.

(420) Wang, S .; Ma, Z .; Pan, W. Data-driven coarse-grained modeling of polymers in solution with structural and dynamic properties conserved. Soft Matter 2020, 16, 8330-8344.

(421) Bockius, N .; Shea, J .; Jung, G .; Schmid, F .; Hanke, M. Model reduction techniques for the computation of extended Markov parameterizations for generalized Langevin equations. J. Phys .: Cond. Matt. 2021, 33, 214003.

(422) Klippenstein, V .; van der Vegt, N. F. A. Cross-correlation corrected friction in (generalized) Langevin models. J. Chem. Phys. 2021, 154, 191102.

54

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(423) Hanke, M. Mathematical analysis of some iterative methods for the reconstruction of memory kernels. ETNA - Electron. Trans. Numer. Analysis 2020, 54, 483-498.

(424) Klippenstein, V .; van der Vegt, N. F. A. Cross-correlation corrected friction in generalized Langevin models: Application to the continuous Asakura-Oosawa model. J. Chem. Phys. 2022, 157, 044103. (425) Wang, S .; Li, Z .; Pan, W. Implicit-solvent coarse-grained modeling for polymer solutions via Mori-Zwanzig formalism. Soft Matter 2019, 15, 7567-7582.

(426) Li, Z .; Bian, X .; Li, X .; Karniadakis, G. E. Incorporation of memory effects in coarse-grained modeling via the Mori-Zwanzig formalism. J. Chem. Phys. 2015, 143, 243128.

(427) Li, Z .; Bian, X .; Yang, X .; Karniadakis, G. E. A comparative study of coarse-graining methods for polymeric fluids: Mori-Zwanzig vs. iterative Boltzmann inversion vs. stochastic parametric optimization. J. Chem. Phys. 2016, 145, 044102.

(428) Li, Z .; Lee, H. S .; Darve, E .; Karniadakis, G. E. Computing the non-Markovian coarse-grained interactions derived from the Mor- iâAŞZwanzig formalism in molecular systems: Application to polymer melts. J. Chem. Phys. 2017, 146, 014104.

(429) Ferrario, M .; Grigolini, P. A generalization of the kuboâĂŤfreed relaxation theory. Chem. Phys. Lett. 1979, 62, 100-106.

(430) Marchesoni, F .; Grigolini, P. On the extension of the Kramers theory of chemical relaxation to the case of nonwhite noise. J. Chem. Phys. 1983, 78, 6287-6298.

(431) Ceriotti, M .; Bussi, G .; Parrinello, M. Langevin Equation with Colored Noise for Constant-Temperature Molecular Dynamics Simulations. Phys. Rev. Lett. 2009, 102, 020601.

(432) Ceriotti, M .; Bussi, G .; Parrinello, M. Colored-Noise Thermo- stats à la Carte. J. Chem. Theory Comput. 2010, 6, 1170-1180.

(433) Davtyan, A .; Dama, J. F .; Voth, G. A .; Andersen, H. C. Dynamic force matching: A method for constructing dynamical coarse-grained models with realistic time dependence. J. Chem. Phys. 2015, 142, 154104.

(434) Baczewski, A. D .; Bond, S. D. Numerical integration of the extended variable generalized Langevin equation with a positive Prony representable memory kernel. J. Chem. Phys. 2013, 139, 044107. (435) Guenza, M. Many chain correlated dynamics in polymer fluids. J. Chem. Phys. 1999, 110, 7574-7588.

(436) Padding, J. T .; Briels, W. J. Time and length scales of polymer melts studied by coarse-grained molecular dynamics simulations. J. Chem. Phys. 2002, 117, 925-943.

(437) Panja, D. Anomalous polymer dynamics is non-Markovian: memory effects and the generalized Langevin equation formulation. Journal of Statistical Mechanics: Theory and Experiment 2010, 2010, P06011.

(438) Hsu, H .- P .; Kremer, K. Static and dynamic properties of large polymer melts in equilibrium. J. Chem. Phys. 2016, 144, 154907. (439) Semenov, A. Relaxation of long-wavelength density fluctuations in a concentrated polymer solution. JETP 1986, 63, 717-720. (440) Müller, M. Memory in the relaxation of a polymer density modulation. J. Chem. Phys. 2022, 156, 124902.

(441) Li, B .; Daoulas, K .; Schmid, F. Dynamic coarse-graining of polymer systems using mobility functions. J. Phys .: Cond. Matt. 2021, 33, 194004.

(442) Müller, M .; Sollich, P .; Sun, D .- W. Nonequilibrium Molecular Conformations in Polymer Self-Consistent Field Theory. Macro- molecules 2020, 53, 10457-10474.

(443) Solar, M .; Meyer, H .; Gauthier, C .; Fond, C .; Benzerara, O .; Schirrer, R .; Baschnagel, J. Mechanical behavior of linear amorphous polymers: Comparison between molecular dynamics and finite-element simulations. Phys. Rev. E 2012, 85, 021808.

(444) Das, C .; Inkson, N. J .; Read, D. J .; Kelmanson, M. A .; McLeish, T. C. B. Computational linear rheology of general branch-on-branch polymers. J. Rheol. 2006, 50, 207.

(445) Read, D. J .; Auhl, D .; Das, C .; den Doelder, J .; Kapnistos, M .; Vittorias, I .; McLeish, T. C. B. Linking Models of Polymerization and Dynamics to Predict Branched Polymer Structure and Flow. Science 2011, 333, 1871-1874.

(446) Bishko, G .; McLeish, T. C. B .; Harlen, O. G .; Larson, R. G. Theoretical Molecular Rheology of Branched Polymers in Simple and Complex Flows: The Pom-Pom Model. Phys. Rev. Lett. 1997, 79, 2352-2355.

(447) Zentel, K. M .; Degenkolb, J .; Busch, M. Using a Multiscale Modeling Approach to Correlate Reaction Conditions with Polymer Microstructure and Rheology. Macromol. Theory Sim. 2021, 30, 2000047.

(448) Zentel, K. M .; Busch, M. Predicting Polymer Properties via a Coupled Kinetic, Stochastic and Rheological Modeling Approach from Reaction Conditions. Macr. Reaction Eng. 2022, 16, 2100027.

(449) Zentel, K. M .; Bungu, P. S. E .; Pasch, H .; Busch, M. Linking molecular structure to plant conditions: Advanced analysis of a systematic set of mini-plant scale low density polyethylenes. Polym. Chem. 2021, 12, 3026.

(450) Zentel, K. M .; Bungu, P. S. E .; Degenkolb, J .; Pasch, H .; Busch, M. Connecting the complex microstructure of LDPE to its rheology and processing properties via a combined fractionation and modelling approach. RSC Adv. 2021, 11, 33114.

(451) Grotian genannt Klages, H .; Ermis, N .; Luinstra, G. A .; Zentel, K. M. Coupling Kinetic Modelling with SAOS and LOS Rheology of Poly(n-butyl acrylate). Macromol. Rap. Comm. 2022, 43, 2100620. (452) Yang, Y. I .; Shao, Q .; Zhang, J .; Yang, L .; Gao, Y. Q. Enhanced sampling in molecular dynamics. J. Chem. Phys. 2019, 151, 070902.

(453) Huber, G .; Kim, S. Weighted-ensemble Brownian dynamics simulations for protein association reactions. Biophys. J. 1996, 70, 97- 110.

(454) Zhang, B. W .; Jasnow, D .; Zuckerman, D. M. The "weighted ensemble" path sampling method is statistically exact for a broad class of stochastic processes and binning procedures. J. Chem. Phys. 2010, 132, 054107.

(455) Dellago, C .; Bolhuis, P .; Csajka, F .; Chandler, D. Transition path sampling and the calculation of rate constants. J. Chem. Phys. 1998, 108, 1964-1977.

(456) Bolhuis, P .; Chandler, D .; Dellago, C .; Geissler, P. Transition path sampling: Throwing ropes over rough mountain passes, in the dark. Annu. Rev. Phys. Chem. 2002, 53, 291-318.

(457) Bolhuis, P. G .; Swenson, D. W. H. Transition Path Sampling as Markov Chain Monte Carlo of Trajectories: Recent Algorithms, Software, Applications, and Future Outlook. Adv. Theory Sim 2021, 4, 2000237.

(458) Allen, R .; Warren, P .; ten Wolde, P. Sampling rare switching events in biochemical networks. Phys. Rev. Lett. 2005, 94, 018104. (459) Allen, R. J .; Valeriani, C .; ten Wolde, P. R. Forward flux sampling for rare event simulations. J. Phys .: Condens. Matter 2009, 21, 463102.

(460) Berryman, J. T .; Schilling, T. Sampling rare events in nonequilibrium and nonstationary systems. J. Chem. Phys. 2010, 133, 244101.

(461) Weinan, E .; Ren, W .; Vanden-Eijnden, E. String Method for the Study of Rare Events. Phys. Rev. B 2002, 66, 052301.

(462) Weinan, E .; Ren, W .; Vanden-Eijnden, E. Finite Temperature String Method for the Study of Rare Events. J. Phys. Chem. B 2005, 109, 6688-6693.

(463) Adelman, J. L .; Grabe, M. Simulating rare events using a weighted ensemble string-based method. J. Chem. Phys. 2013, 138, 044105.

(464) Pande, V. S .; Beauchamp, K .; Bowman, G. R. Everything you wanted to know about Markov State Models but were afraid to ask. Methods 2010, 52, 99-105.

(465) Bowyman, G. R., Panday, V. S., Noé, F., Eds. An Introduction to Markov State Models and Their Application to Long Timescale Molecular Simulations; Advances in Experimental Medicine and Biology; Springer, 2014.

(466) Schütte, C .; Sarich, M. A critical appraisal of Markov state models. Eur. Phys. J. - Spec. Topics 2015, 224, 2445-2462.

(467) Husic, B. E .; Pande, V. S. Markov State Models: From an Art to a Science. J. Am. Chem. Soc. 2018, 140, 2386-2396.

55

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(468) Perez-Hernandez, G .; Paul, F .; Giorgino, T .; de Fabritiis, G .; Noe, F. Identification of slow molecular order parameters for Markov model construction. J. Chem. Phys. 2013, 139, 015102.

(469) Trendelkamp-Schroer, B .; Wu, H .; Paul, F .; Noe, F. Estimation and uncertainty of reversible Markov models. J. Chem. Phys. 2015, 143, 174101.

(470) Keller, B. G .; Prinz, J .- H .; Noe, F. Markov models and dynamical fingerprints: Unraveling the complexity of molecular kinetics. Chem. Phys. 2012, 396, 92-107.

(471) Mardt, A .; Noe, F. Progress in deep Markov state modeling: Coarse graining and experimental data restraints. J. Chem. Phys. 2021, 155, 214106.

(472) Appeldorn, J. H .; Lemcke, S .; Speck, T .; Nikoubashman, A. Employing Artificial Neural Networks to Identify Reaction Coordinates and Pathways for Self-Assembly. J. Phys. Chem. B 2022, 126, 5007- 5016.

(473) Knoch, F .; Speck, T. Cycle representatives for the coarse- graining of systems driven into a non-equilibrium steady state. New J. of Physics 2015, 17, 115004.

(474) Knoch, F .; Speck, T. Nonequilibrium Markov state modeling of the globule-stretch transition. Phys. Rev. E 2017, 95, 012503.

(475) Knoch, F .; Speck, T. Non-equilibrium Markov state modeling of periodically driven biomolecules. J. Chem. Phys. 2019, 150, 054103. (476) Knoch, F .; Speck, T. Unfolding dynamics of small peptides biased by constant mechanical forces. Mol. Syst. Design & Eng. 2018, 3, 204-213.

(477) Knoch, F .; Schafer, K .; Diezemann, G .; Speck, T. Dynamic coarse-graining fills the gap between atomistic simulations and experimental investigations of mechanical unfolding. J. Chem. Phys. 2018, 148, 044109.

(478) Gemuenden, P .; Poelking, C .; Kremer, K .; Daoulas, K .; Andrienko, D. Effect of Mesoscale Ordering on the Density of States of Polymeric. Semiconductors. Macromol. Rap. Comm. 2015, 36, 1047- 1053. (479) Kordt, P .; van der Holst, J. J. M .; Al Helwi, M .; Kowalsky, W .; May, F .; Badinski, A .; Lennartz, C .; Andrienko, D. Modeling of Organic Light Emitting Diodes: From Molecular to Device Properties. Adv. Funct. Mat 2015, 25, 1955-1971.

(480) Athanasopoulos, S .; Kirkpatrick, J .; Martinez, D .; Frost, J. M .; Foden, C. M .; Walker, A. B .; Nelson, J. Predictive study of charge transport in disordered semiconducting polymers. Nano Lett. 2007, 7, 1785-1788. (481) Kirkpatrick, J .; Marcon, V .; Nelson, J .; Kremer, K .; Andrienko, D. Charge mobility of discotic mesophases: A multiscale quantum and classical study. Phys. Rev. Lett. 2007, 98, 227402.

(482) Nelson, J .; Kwiatkowski, J. J .; Kirkpatrick, J .; Frost, J. M. Modeling Charge Transport in Organic Photovoltaic Materials. Acc. Chem. Res. 2009, 42, 1768-1778.

(483) Ruehle, V .; Lukyanov, A .; May, F .; Schrader, M .; Vehoff, T .; Kirkpatrick, J .; Baumeier, B .; Andrienko, D. Microscopic Simulations of Charge Transport in Disordered Organic Semiconductors. J. Chem. Theory Comput. 2011, 7, 3335-3345. (484) Marcus, R. A. Electron-transfer reactions in chemistry - Theory and experiment. Rev. Mod. Phys. 1993, 65, 599-610.

(485) E, W .; Engquist, B. The Heterogeneous Multiscale Methods. Methods. Comm. Math. Sci. 2003, 1, 87-231.

(486) Ren, W .; E, W. Heterogeneous multiscale method for the modeling of complex fluids and micro-fluidics. J. Comput. Phys. 2005, 204, 1-26. (487) E, W .; Engquist, B .; Li, X .; Ren, W .; Vanden-Eijnden, E. Heterogeneous Multiscale Methods: A Review. Phys. 2007, 2, 367- 340.

(488) Borg, M. K .; Lockerby, D. A .; Reese, J. A. A multiscale method for micro/nano flows of high aspect ratio. J. Comput. Phys. 2013, 233, 400-413.

(489) Yan, H .- J .; Wan, Z .- H .; Qin, F .- H .; Sun, D .- J. Multiscale Simulations of Polymer Flow Between Two Parallel Plates. J. Fluids Eng. - Trans. ASME 2021, 143, 041208.

(490) Stalter, S .; Yelash, L .; Emamy, N .; Statt, A .; Hanke, M .; Lukáčová-Medviďová, M. Molecular dynamics simulations in hybrid particle-continuum schemes: Pitfalls and caveats. Comp. Phys. Comm. 2018, 224, 198-208.

(491) Datta, R .; Yelash, L .; Schmid, F .; Kummer, F .; Oberlack, M .; Lukáčová-Medviďová, M .; Virnau, P. Shear-Thinning in Oligomer Melts - Molecular Origins and Applications. Polymers 2021, 13, 2806. (492) Tedeschi, F .; Giusteri, G. G .; Yelash, L .; Lukáčová-Medviďová, M. A multi-scale method for complex flows of non-Newtonian fluids. Math. in Engineering 2022, 4, 1-22.

(493) Honda, T .; Kawakatsu, T. Hybrid Dynamic Density Functional Theory for Polymer Melts and Blends. Macromolecules 2007, 40, 1227- 1237.

(494) Müller, M .; Daoulas, K. C. Speeding Up Intrinsically Slow Collective Processes in Particle Simulations by Concurrent Coupling to a Continuum Description. Phys. Rev. Lett. 2011, 107, 227801.

(495) Warshel, A .; Levitt, M. Theoretical studies of enzymatic reactions: Dielectric, electrostatic and steric stabilization of the carbonium ion in the reaction of lysozyme. J. Mol. Biol. 1976, 103, 227-280.

(496) Praprotnik, M .; Delle Site, L .; Kremer, K. Adaptive resolution molecular-dynamics simulation: Changing the degrees of freedom on the fly. J. Chem. Phys. 2005, 123, 224106.

(497) de Fabritiis, G .; Delgado-Buscalioni, R .; Coveney, P. V. Multiscale Modeling of Liquids with Molecular Specificity. Phys. Rev. Lett. 2006, 97, 134501.

(498) Neri, M .; Anselmi, C .; Cascella, M .; Maritan, A .; Carloni, P. Coarse-Grained Model of Proteins Incorporating Atomistic Detail of the Active Site. Phys. Rev. Lett. 2005, 95, 218102.

(499) Potestio, R .; Fritsch, S .; Español, P .; Delgado-Buscalioni, R .; Kremer, K .; Everaers, R .; Donadio, D. Hamiltonian Adaptive Resolution Simulation for Molecular Liquids. Phys. Rev. Lett. 2013, 110, 108301.

(500) Delgado-Buscalioni, R .; de Fabritiis, G. Embedding Molecular Dynamics within Fluctuating Hydrodynamics in Multiscale Simula- tions of Liquids. Phys. Rev. Lett. 2007, 76, 036709.

(501) Ensing, B .; Nielsen, S. O .; Moore, P. B .; Klein, M. L .; Parrinello, M. Energy Conservation in Adaptive Hybrid Atomistic/Coarse-Grain Molecular Dynamics. J. Chem. Theory Comput. 2007, 3, 1100-1105. (502) Oestereich, M .; Gauss, J .; Diezemann, G. Force probe simulations using an adaptive resolution scheme. J. Phys .: Cond. Matt. 2021, 33, 194005.

(503) Delgado-Buscalioni, R .; Kremer, K .; Praprotnik, M. Concurrent triple-scale simulation of molecular liquids. J. Chem. Phys. 2008, 128, 114110.

(504) Delgado-Buscalioni, R .; Kremer, K .; Praprotnik, M. Coupling atomistic and continuum hydrodynamics through a mesoscopic model: Application to liquid water. J. Chem. Phys. 2009, 131, 244107.

(505) Qi, S .; Behringer, H .; Schmid, F. Using field theory to construct hybrid particle-continuum simulation schemes with adaptive resolution for soft matter systems. New J. of Physics 2013, 15, 125009.

(506) Qi, S .; Behringer, H .; Raasch, T .; Schmid, F. A hybrid particle- continuum resolution method and its application to a homopolymer solution. Eur. Phys. J. - Spec. Topics 2016, 225, 1527-1549.

(507) Qi, S .; Schmid, F. Hybrid particle-continuum simulations coupling Brownian dynamics and local dynamic density functional theory. Soft Matter 2017, 13, 7938-7947.

(508) Abrams, C. F. Concurrent dual-resolution Monte Carlo simulation of liquid methane. J. Chem. Phys. 2005, 123, 234101. (509) Heidari, M .; Kremer, K .; Cortes-Huerto, R .; Potestio, R. Spatially Resolved Thermodynamic Integration: An Efficient Method To Compute Chemical Potentials of Dense Fluids. J. Chem. Theory Comput. 2018, 14, 3409-3417.

(510) Heidari, M .; Kremer, K .; Golestanian, R .; Potestio, R .; Cortes- Huerto, R. Open-boundary Hamiltonian adaptive resolution. From grand canonical to non-equilibrium molecular dynamics simulations. J. Chem. Phys. 2020, 152, 194104.

(511) Baptista, L. A .; Dutta, R. C .; Sevilla, M .; Heidari, M .; Potestio, R .; Kremer, K .; Cortes-Huerto, R. Density-functional-theory approach

56

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

to the Hamiltonian adaptive resolution simulation method. J. Phys .: Cond. Matt. 2021, 33, 184003.

(512) Stieffenhofer, M .; Wand, M .; Bereau, T. Adversarial reverse mapping of equilibrated condensed-phase molecular structures. Machine Learning - Science and Technology 2020, 1, 045014. (513) Stieffenhofer, M .; Bereau, T .; Wand, M. Adversarial reverse mapping of condensed-phase molecular structures: Chemical trans- ferability. APL Materials 2021, 9, 031107.

(514) Santangelo, G .; Di Matteo, A .; Müller-Plathe, F .; Milano, G. From mesoscale back to atomistic models: A fast reverse-mapping procedure for vinyl polymer chains. J. Phys. Chem. B 2007, 111, 2765- 2773.

(515) Rzepiela, A. J .; Schäfer, L. V .; Goga, N .; Risselada, H. J .; de Vries, A. H .; Marrink, S. Reconstruction of atomistic details from coarse-grained structures. J. Comput. Chem. 2010, 31, 1333-1343.

(516) Lombardi, L. E .; Marti, M. A .; Capece, L. CG2AA: backmapping protein coarse-grained structures. Bioinformatics 2016, 32, 1235-1237.

(517) Liu, P .; Shi, Q .; Lyman, E .; Voth, G. A. Reconstructing atomistic detail for coarse-grained models with resolution exchange. J. Chem. Phys. 2008, 129, 114103.

(518) Kmiecik, S .; Gront, D .; Kolinski, M .; Wieteska, L .; Dawid, A. E .; Kolinski, A. Coarse-Grained Protein Models and Their Applications. Chem. Rev. 2016, 116, 7898-7936.

(519) Li, W .; Burkhart, C .; Polinska, P .; Harmandaris, V .; Doxastakis, M. Backmapping coarse-grained macromolecules: An efficient and versatile machine learning approach. J. Chem. Phys. 2020, 153, 041101. (520) Svaneborg, C .; Karimi-Varzaneh, H. A .; Hojdis, N .; Fleck, F .; Everaers, R. Multiscale approach to equilibrating model polymer melts. Phys. Rev. E 2016, 94, 032502.

(521) Uhlherr, A .; Mavrantzas, V .; Doxastakis, M .; Theodorou, D. Directed bridging methods for fast atomistic Monte Carlo simulations of bulk polymers. Macromolecules 2001, 34, 8554-8568.

(522) Mavrantzas, V .; Boone, T .; Zervopoulou, E .; Theodorou, D. End-bridging Monte Carlo: A fast algorithm for atomistic simulation of condensed phases of long polymer chains. Macromolecules 1999, 32, 5072-5096.

(523) Karayiannis, N .; Giannousaki, A .; Mavrantzas, V .; Theodorou, D. Atomistic Monte Carlo simulation of strictly monodisperse long polyethylene melts through a generalized chain bridging algorithm. J. Chem. Phys. 2002, 117, 5465-5479.

(524) Karayiannis, N .; Mavrantzas, V .; Theodorou, D. A novel Monte Carlo scheme for the rapid equilibration of atomistic model polymer systems of precisely defined molecular architecture. Phys. Rev. Lett. 2002, 88, 105503. (525) Auhl, R .; Everaers, R .; Grest, G. G .; Kremer, K .; Plimpton, S. J. Equilibration of long chain polymer melts in computer simulations. J. Chem. Phys. 2003, 119, 12718.

(526) Moreira, L. A .; Zhang, G .; Müller, F .; Stuehn, T .; Kremer, K. Direct Equilibration and Characterization of Polymer Melts for Computer Simulations. Macromol. Theory Sim. 2015, 24, 419-431. (527) Ozog, D .; McCarty, J .; Gossett, G .; Malony, A. D .; Guenza, M. Fast equilibration of coarse-grained polymeric liquids. J. Comp. Sci. 2015, 9, 33-38.

(528) Sliozberg, Y. R .; Kroger, M .; Chantawansri, T. L. Fast equilibration protocol for million atom systems of highly entangled linear polyethylene chains. J. Chem. Phys. 2016, 144, 154901.

(529) Subramanian, G. A topology preserving method for generating equilibrated polymer melts in computer simulations. J. Chem. Phys. 2010, 133, 164902.

(530) Subramanian, G. An Iterative Method for Producing Equilibrated Symmetric Three-Arm Star Polymer Melts in Molecular Dynamics. Macromol. Theory Sim 2011, 20, 46-53.

(531) de Nicola, A .; Kawakatsu, T .; Milano, G. Generation of Well- Relaxed All-Atom Models of Large Molecular Weight Polymer Melts: A Hybrid Particle-Continuum Approach Based on Particle-Field Molecular Dynamics Simulations. J. Chem. Theory Comput. 2014, 10, 5651-5667.

(532) de Nicola, A .; Munaó, G .; Grizzuti, N .; Auriemma, F .; De Rosa, C .; Sevink, A .; Milano, G. Generation of well-relaxed all atom models of stereoregular polymers: A validation of hybrid particle-field molecular dynamics for polypropylene melts of different tacticities. Soft Mater. 2020, 18, 228-241.

(533) Zhang, G .; Moreira, L. A .; Stuehn, T .; Daoulas, K. C .; Kremer, K. Equilibration of High Molecular Weight Polymer Melts: A Hierarchical Strategy. ACS Macro Lett. 2014, 3, 198-203.

(534) Zhang, G .; Stuehn, T .; Daoulas, K. C .; Kremer, K. Communication: One size fits all: Equilibrating chemically different polymer liquids through universal long-wavelength description. J. Chem. Phys. 2015, 142, 221102.

(535) Ohkuma, T .; Kremer, K .; Daoulas, K. Equilibrating high- molecular-weight symmetric and miscible polymer blends with hierarchical back-mapping. J. Phys .: Cond. Matt. 2018, 30, 174001. (536) Zhang, G .; Chazirakis, A .; Harmandaris, V. A .; Stuehn, T .; Daoulas, K. C .; Kremer, K. Hierarchical modelling of polystyrene melts: from soft blobs to atomistic resolution. Soft Matter 2019, 15, 289-302. (537) Meyer, H .; Horwath, E .; Virnau, P. Mapping onto Ideal Chains Overestimates Self-Entanglements in Polymer Melts. ACS Macro Lett. 2018, 7, 757-761.

(538) Tubiana, L .; Kobayashi, H .; Potestio, R .; Dünweg, B .; Kremer, K .; Virnau, P .; Daoulas, K. Comparing equilibration schemes of high- molecular-weight polymer melts with topological indicators. J. Phys .: Cond. Matt. 2021, 33, 204003.

(539) Bozkurt Varolguenes, Y .; Bereau, T .; Rudzinski, J. F. Interpretable embeddings from molecular simulations using Gaussian mixture variational autoencoders. Machine Learning - Science and Technology 2020, 1, 015012.

(540) Unke, O. T .; Chmiela, S .; Sauceda, H. E .; Gastegger, M .; Poltavsky, I .; Schütt, K. T .; Tkatchenko, A. Machine Learning Force Fields. Chem. Rev. 2021, 121, 10142-10186.

(541) Bereau, T .; Andrienko, D .; von Lilienfeld, O. A. Transferable Atomic Multipole Machine Learning Models for Small Organic Molecules. J. Chem. Theory Comput. 2015, 11, 3225-3233.

(542) Ye, H .; Xian, W .; Li, Y. Machine Learning of Coarse-Grained Models for Organic Molecules and Polymers: Progress, Opportunities, and Challenges. ACS Omega 2021, 6, 1758-1772.

(543) Webb, M. A .; Jackson, N. E .; Gil, P. S .; de Pablo, J. Targeted sequence design within the coarse-grained polymer genome. Sci. Adv. 2020, 6, eabc6216.

(544) Hoffmann, C .; Menichetti, R .; Kanekal, K. H .; Bereau, T. Controlled exploration of chemical space by machine learning of coarse-grained representations. Phys. Rev. E 2019, 100, 033302. (545) Zhang, Z .; Friedrich, K. Artificial neural networks applied to polymer composites: a review. Compos. Sci. Technol. 2003, 63, 2029- 2044.

(546) Rong, Q .; Wei, H .; Huang, X .; Bao, H. Predicting the effective thermal conductivity of composites from cross sections images using deep learning methods. Compos. Sci. Technol. 2019, 184, 107861.

(547) Liu, B .; Vu-Bac, N .; Rabczuk, T. A stochastic multiscale method for the prediction of the thermal conductivity of Polymer nano- composites through hybrid machine learning algorithms. Composite Structures 2021, 273, 114269.

(548) Garcia-Carrillo, M .; Espinoza-Martinez, A. B .; Ramos-de Valle, L. F .; Sanchez-Valdes, S. Simultaneous optimization of thermal and electrical conductivity of high density polyethylene-carbon particle composites by artificial neural networks and multi-objective genetic algorithm. Comput. Mater. Sci. 2022, 201, 110956.

(549) Tu, K .- H .; Huang, H .; Lee, S .; Lee, W .; Sun, Z .; Alexander-Katz, A .; Ross, C. A. Machine Learning Predictions of Block Copolymer Self- Assembly. Adv. Mater. 2020, 32, 2005713.

(550) Mattioni, B .; Jurs, P. Prediction of glass transition temperatures from monomer and repeat unit structure using computational neural networks. J. Chem. Inf. and Comp. J. Chem. Inf. and Comp. 2002, 42, 232-240.

(551) Ning, L. Artificial neural network prediction of glass transition temperature of fluorine-containing polybenzoxazoles. J. Mater. Sci. 2009, 44, 3156-3164.

57

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

Perspective

## ACS Polymers Au



pubs.acs.org/polymerau

(552) Liu, W. Prediction of Glass Transition Temperatures of Aromatic Heterocyclic Polyimides Using an ANN Model. Polym. Eng. Sci. 2010, 50, 1547-1557.

(553) Liu, Y .; Tan, Z .; Zhang, S. Prediction of Glass Transition Temperatures of Polyquinolines and Polyquinoxalines. Polym. Sci. A 2012, 54, 48-60.

(554) Liu, W .; Cao, C. Artificial neural network prediction of glass transition temperature of polymers. Colloid Polym. Sci. 2009, 287, 811- 818.

(555) Palomba, D .; Esteban Vazquez, G .; Fatima Diaz, M. Novel descriptors from main and side chains of high-molecular-weight polymers applied to prediction of glass transition temperatures. J. Mol. Graph. & Model. 2012, 38, 137-147.

(556) Higuchi, C .; Horvath, D .; Marcou, G .; Yoshizawa, K .; Varnek, A. Prediction of the Glass-Transition Temperatures of Linear Homo/ Heteropolymers and Cross-Linked Epoxy Resins. ACS Appl. Polym. Mater. 2019, 1, 1430-1442.

(557) Pilania, G .; Iverson, C. N .; Lookman, T .; Marrone, B. L. Machine-Learning-Based Predictive Modeling of Glass Transition Temperatures: A Case of Polyhydroxyalkanoate Homopolymers and Copolymers. J. Chem. Inf. Model. 2019, 59, 5013-5025.

(558) Miccio, L. A .; Schwartz, G. A. Localizing and quantifying the intra-monomer contributions to the glass transition temperature using artificial neural networks. Polymer 2020, 203, 122786.

(559) Miccio, L. A .; Schwartz, G. A. From chemical structure to quantitative polymer properties prediction through convolutional neural networks. Polymer 2020, 193, 122341.

(560) Wen, C .; Liu, B .; Wolfgang, J .; Long, T. E .; Odle, R .; Cheng, S. Determination of glass transition temperature of polyimides from atomistic molecular dynamics simulations and machine-learning algorithms. J. Polym. Sci. 2020, 58, 1521-1534.

(561) Tao, L .; Varshney, V .; Li, Y. Benchmarking Machine Learning Models for Polymer Informatics: An Example of Glass Transition Temperature. J. Chem. Inf. Model. 2021, 61, 5395-5413.

(562) Karuth, A .; Alesadi, A .; Xia, W .; Rasulev, B. Predicting glass transition of amorphous polymers by application of cheminformatics and molecular dynamics simulations. Polymer 2021, 218, 123495. (563) Chen, G .; Tao, L .; Li, Y. Predicting Polymers' Glass Transition Temperature by a Chemical Language Processing Model. Polymers 2021, 13, 1898. (564) Zhang, Y .; Xu, X. Machine learning glass transition temperature of polyacrylamides using quantum chemical descriptors. Polym. Chem. 2021, 12, 843-851.

(565) Tao, L .; Chen, G .; Li, Y. Machine learning discovery of high- temperature polymers. Patterns 2021, 2, 100225. (566) Audus, D. J .; de Pablo, J. J. Polymer Informatics: Opportunities and Challenges. ACS Macro Lett. 2017, 6, 1078-1082.

(567) Bereau, T. Compuational compound screening of biomolecules and soft materials by molecular simulations. Modelling Simul. Mater. Sci. Eng. 2021, 29, 023001. (568) Gormley, A. J .; Webb, M. A. Machine learning in combinatorial polymer chemistry. Nature Reviews Materials 2021, 6, 642-644. (569) Jablonka, K. M .; Jothiappan, G. M .; Wang, S .; Smit, B .; Yoo, B. Bias free multiobjective active learning for materials design and discovery. Nat. Commun. 2021, 12, 2312.

(570) Kim, C .; Chandrasekaran, A .; Huan, T. D .; Das, D .; Ramprasad, R. Polymer Genome: A Data-Powered Polymer Informatics Platform for Property Predictions. J. Phys. Chem. C 2018, 122, 17575-17585. (571) Doan Tran, H .; Kim, C .; Chen, L .; Chandrasekaran, A .; Batra, R .; Venkatram, S .; Kamal, D .; Lightstone, J. P .; Gurnani, R .; Shetty, P .; Ramprasad, M .; Laws, J .; Shelton, M .; Ramprasad, R. Machine-learning predictions of polymer properties with Polymer Genome. J. Appl. Phys. 2020, 128, 171104.

(572) Ma, R .; Liu, Z .; Zhang, Q .; Liu, Z .; Luo, T. Evaluating Polymer Representations via Quantifying Structure-Property Relationships. J. Chem. Inf. Model. 2019, 59, 3110-3119. (573) Jangizehi, A .; Schmid, F .; Besenius, P .; Kremer, K .; Seiffert, S. Defects and Defect Engineering in Soft Matter. Soft Matter 2022, 972, 10809.

(574) Vakis, A. I .; et al. Modeling and simulation in tribology across scales: An overview. Tribol. Int. 2018, 125, 169-199. (575) Krauklis, A. E .; Karl, C. W .; Rocha, U. B. C. M .; Burlakovs, J .; Ozola-Davidane, R .; Gagni, A. I .; Starkova, O. Modelling of environmental Ageing of Polymers and Polymer Composities - Modular and Multiscale Methods. Polymers 2022, 14, 216. (576) Starkova, O .; Gagani, A. I .; Karl, C. W .; Rocha, I. B. C. M .; Burlakovs, J .; Kraklis, A. E. Modelling of environmental Ageing of Polymers and Polymer Composities - Durability Prediction Methods. Polymers 2022, 14, 907.

## :unselected: Recommended by ACS



Constraints on Knot Insertion, Not Internal Jamming, Control Polycatenane Translocation Dynamics through Crystalline Pores

Zifeng Wang, Mesfin Tsige, et al. APRIL 10, 2023 MACROMOLECULES

READ & :selected:

Single-Chain Inherent Elasticity of Macromolecules: From Concept to Applications

Yu Bao and Shuxun Cui FEBRUARY 27, 2023 LANGMUIR READ G :selected:

Canonicalizing BigSMILES for Polymers with Defined Backbones

Tzyy-Shyang Lin, Bradley D. Olsen, et al. OCTOBER 14, 2022 ACS POLYMERS AU

READ E :selected:

Rheological Characterization and Theoretical Modeling Establish Molecular Design Rules for Tailored Dynamically Associating Polymers

Pamela C. Cai, Andrew J. Spakowitz, et al. SEPTEMBER 12, 2022 ACS CENTRAL SCIENCE

READ E :selected:

Get More Suggestions >

58

https://doi.org/10.1021/acspolymersau.2c00049 ACS Polym. Au 2023, 3, 28-58

