==========
What's new
==========

Version 0.3
-----------

chemlab.core:
    - New bond handling with the Molecule.bonds and System.bonds attributes
    - Possibility to add charges

chemlab.graphics:
    - Post Processing Effects:
        - FXAA -- Fast Approximate Antialiasing
	- Gamma Correction
	- Glow
	- Outline
        - SSAO -- Screen Space Ambient Occlusion

     - Renderers:
        - Implemented toon shading for different shapes.
        - CylinderImpostorRenderer -- a really fast way to draw cylinders
 
     - Offline Rendering at any resolution supported by the video card.
     - Started some work on user interaction for a full molecular viewer.

chemlab.db:

      - New Databases:
         - RCSB for protein structures
	 - ToxNetDB for properties
	 - ChemspiderDB
	  
Version 0.2
-----------

chemlab.core:

    - Serialization through json with from_json 
      and tojson for Atom, System and Molecule;
    - Removing atoms and molecules from System. System.remove_atoms,
      System.remove_molecules;
    - Experimental support for customized Atom/Molecule/System types.
    - Some indexing routines: System.atom_to_molecules_indices and
      System.mol_to_atom_indices;
    - Custom sorting of systems throught System.reorder_molecules;
    - Support for bonds in molecules and experimental support for
      bonds in Systems throught Molecule.bonds and
      System.get_bonds_array
    - System.merge_systems has a better overlap handling.
    - Removed boxsize attribute, now you have to always specify
      box_vectors.
    - Implemented random_lattice_box to do random solvent boxes.

chemlab.graphics:

    - New Renderers:
      - BallAndStickRenderer
      - BondRenderer
      - WireframeRenderer

    - Implemented Camera.autozoom for autoscaling
    - Reimplemented BondRenderer in cython.

chemlab.io:

    - New Handlers:
       - MDL molfile (.mol extension)
       - Chemical Markup Language (.cml extension)

chemlab.db:

    - New package to handle databases
    - CirDB to retrieve molecules from chemical identifier resolver
    - ChemlabDB to retrieve built-in data
    - LocalDB to make personal databases

chemlab.ipython:
    
    - Preliminary ipython notebook integration. It can display
      Molecule and System instances by using out-of-screen rendering.

chemlab.utils:

    - Implemented some (periodic/non-periodic) distance finding
      routines.
