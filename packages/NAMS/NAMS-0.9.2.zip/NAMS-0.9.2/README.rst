NAMS: Non-contiguous Atom Matching Structural Similarity
=========================================================

NAMS is a similarity method based on atom alignment for the analysis of structural similarity between molecules. This method is based on the comparison 
of the bonding profiles of atoms on comparable molecules, including features that are seldom found in other structural or graph matching approaches like 
chirality or double bond stereoisomerism. The similarity measure is then defined on the annotated molecular graph, based on an iterative directed graph 
similarity procedure and  optimal atom alignment between atoms using a pairwise matching algorithm. With the proposed approach the similarities detected 
are more intuitively understood because similar atoms in the molecules are explicitly shown. This module implements NAMS and also supports the classification 
of the type of isomerism present in a given atom or bond of a molecule. 

For background and cite the authors in any work or product based on this material:

- Ana L. Teixeira and Andre O. Falcao 2013: Noncontiguous atom matching structural similarity function. Journal of Chemical Information and Modeling, 53(10), pp 2511–2524. (DOI: 10.1021/ci400324u)

- Ana L. Teixeira, Joao P. Leal and Andre O. Falcao, Automated Identification and Classification of Stereochemistry: Chirality and Double Bond Stereoisomerism. Technical Report . LaSIGE, Department of Informatics, Faculty of Sciences, University of Lisbon, February 2013. (DOI: arXiv:1303.1724)	

Visit our webtool at http://nams.lasige.di.fc.ul.pt/


Disclaimer
==========


THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.



Typical usage
=============
Usage examples::

    from nams import nams
    from nams import chirality
    from nams import doubleb_e_z
    
    ms=nams.Nams()
    
    #Define 2 molecules: (molecular_representation_type, molecular_representation) 
    mol_t1 = ("smi", "CCC(=O)C(c1ccccc1)c2ccccc2")
    mol_t2= ("smi", "O=C(CC)N(c1ccncc1)c3ccccc3")
    
    #Extract the set of characteristics of the atoms/bonds 
    mol1, mol_info1 = ms.get_mol_info(mol_t1[0],mol_t1[1])
    mol2, mol_info2 = ms.get_mol_info(mol_t2[0],mol_t2[1])
    
    #Calculate the similarity between the pair of molecules
    sim11, d_atoms = ms.get_similarity(mol_info1, mol_info1) 
    sim22, d_atoms = ms.get_similarity(mol_info2, mol_info2)
    sim12, d_atoms = ms.get_similarity(mol_info1, mol_info2)
    
    #Chirality detection and classification classification
    chir=chirality.Chirality("C([C@@H](C(=O)O)N)S", "smi")
    chir.get_chirality(atom_id)
    
    #Double bond stereoisomerism detection and classification
    stereo=doubleb_e_z.Stereodoubleb("I/C=C/Cl", "smi")
    stereo.get_e_z_at(at1, at2)

More examples: http://nams.lasige.di.fc.ul.pt/downloads.php

Dependencies and Requirements
=============================
Python
------
Python 2.7

Modules
-------
* openbabel, a chemical toolbox designed to handle chemical data <http://openbabel.org/>. 

* pybel, which provides convenience functions and classes that make it simpler to use the Open Babel libraries from Python, especially for file input/output and for accessing the attributes of atoms and molecules. <http://openbabel.org/docs/current/UseTheLibrary/PythonInstall.html>. 

* munkres, which provides an implementation of the Munkres algorithm (also called the Hungarian algorithm or the Kuhn-Munkres algorithm), useful for solving the Assignment Problem. <https://pypi.python.org/pypi/munkres/>. 

Installation Instructions
============================

Windows Installer
-------------------
(1) Install the required Python Dependencies;
(2) Download the Windows Installer (32 or 64 bits) file;
(3) Execute the file and follow the instructions in the installation wizard. 

Source
--------

(1) Install the required Python Dependencies;
(2) Download the Raw Source (available in .zip or .tar.gz) file;
(3) Unpack the downloaded folder. 
(4) in the command line set the right path to the unpacked folder and run::

    python setup.py build
    python setup.py install	

	
Easy Install (for Python 2.7 only)
-----------------------------------

(1) Install the required Python Dependencies;
(2) Download the EasyInstall file;
(3) Install Easy_install, a python module to automatically download, build, install, and manage Python packages <http://pythonhosted.org/distribute/easy_install.html> 
(4) in the command line set the right path to the downloaded file and run::
	
	easy_install NAMS-0.9.2-py2.7.egg	

OR install NAMS package by name, searching PyPI for the latest version, and automatically downloading, building, and installing it::

	easy_install NAMS

Frequently Asked Questions
============================

**(1) Why does in a molecule such as *CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=C(OC1=O)C=CC=C2* the stereocenter is ignored?**

To avoid ambiguity we decided that we would only classify the chirality of a stereocenter or a double bond stereoisomerism if the stereo information is **explicitly** written in the molecular identifier. In the case of chirality, we verify if there is a carbon atom with four different groups attached and if the sense of rotation of these groups is explicitly described in SMILES as clockwise or anticlockwise with "@" or "@@" (more details about the notation of Configuration Around Tetrahedral Centers in SMILES: http://www.daylight.com/dayhtml/doc/theory/theory.smiles.html)

The SMILES CC(=O)CC(C1=CC=CC=C1)C1=C(O)C2=C(OC1=O)C=CC=C2, has a stereocenter in the atom 5, because it has 4 different groups attached to it, but the sense of rotation of these groups is not indicated.

To represent the R-stereocenter the correct SMILES would be:
CC(=O)C[C@H](C1=CC=CC=C1)C1=C(O)C2=C(OC1=O)C=CC=C2

To represent the S-stereocenter the correct SMILES would be:
CC(=O)C[C@@H](C1=CC=CC=C1)C1=C(O)C2=C(OC1=O)C=CC=C2
  

**(2) Why does when comparing molecules such as trans-1,4-Dimethylcyclohexane (*C[C@H]1CC[C@@H](C)CC1*) and cis-1,4-Dimethylcyclohexane (*C[C@H]1CC[C@H](C)CC1*) the similarity score is 1?**

This is a possible rare case where two substituents in an atom differ only in their absolute configuration (R or S). However, this (Cahn–Ingold–Prelog priority) rule can lead to ambiguity in the evaluation of pairs of ligands [1-2], therefore it was not yet considered in the present version. The same situation is verified to double bond configurations. 

1. Mata P, Lobo AM (2005): The Cahn, Ingold and Prelog System: eliminating ambiguity in the 
comparison of diastereomorphic and enantiomorphic ligands. Tetrahedron: Asymmetry, 16:2215-2223. 

2. Hirschmann H, Hanson KR (1974): Prochiral and pseudoasymmetric centers: Implications of recent 
definitions. Tetrahedron, 30:3649-3656

**(3) Is there help documentation available for NAMS?**

Yes. NAMS is thoroughly described:
- Ana L. Teixeira and Andre O. Falcao 2013: Noncontiguous atom matching structural similarity function. Journal of Chemical Information and Modeling, 53(10), pp 2511–2524. (DOI: 10.1021/ci400324u) <http://pubs.acs.org/doi/abs/10.1021/ci400324u> [Note: If you do not have free access to the manuscript please contact the authors]

The module that detects and classifies stereochemistry is thoroughly described:
- Ana L. Teixeira, Joao P. Leal and Andre O. Falcao, Automated Identification and Classification of Stereochemistry: Chirality and Double Bond Stereoisomerism. Technical Report . LaSIGE, Department of Informatics, Faculty of Sciences, University of Lisbon, February 2013. (DOI: arXiv:1303.1724) <http://docs.di.fc.ul.pt/jspui/bitstream/10455/6894/1/TR_stereo.pdf>	

There are several usage examples in the following Webpage: http://nams.lasige.di.fc.ul.pt/downloads.php

API documentation will be made available as soon as possible. 

**(4) Is NAMS platform independent?**

Yes, NAMS is platform independent. It requires python 2.X and the following python packages: openbabel, pybel and munkres. 


More questions, comments or suggestions can be sent by e-mail to ateixeira 'at' lasige.di.fc.ul.pt or using the following form: <http://nams.lasige.di.fc.ul.pt/contact.php>

Change Log
============================

**v0.9.2 release: 11-13-2013**

-- is a minor release that fixes issues discovered after the release of v0.9.1

* molecules with less than 3 atoms are not processed and an error message is printed out: "Error 3: NAMS cannot be applied to molecules with less than 3 atoms (including hydrogen atoms)."

* disconnected structures are automatically removed but the largest contiguous fragment. In such situation a warning message is printed out: "Warning: Disconnected structures were removed."

* includes Atom Substitution Matrixes for all possible Atoms.

* fixes a problem with the identification of the E/Z stereoisomerism for carbon atoms with charges.

* invalid input formats are not processed and an error message is printed out: "Error 1: Invalid input format. Please check here http://openbabel.org/docs/2.3.1/FileFormats/Overview.html the supported formats and respective names/codes"

* invalid molecules are not processed and an error message is printed out: "Error 2: Invalid molecule or correspondence between the molecule and input format."


**v0.9.1 release: 09-23-2013**

-- Initial release.


License
===========

The NAMS python package calculates the similarity between molecules based on the 
structural/topological relationships of each atom towards all the others 
within a molecule.

This program is free software: you can redistribute it and/or modify
it under the terms of the MIT License as published on the official site of Open Source Initiative
and attached below.

Copyright (C) 2013, Andre Falcao and Ana Teixeira, University of Lisbon - LaSIGE

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files 
(the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, 
publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, 
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

Please cite the authors in any work or product based on this material:

AL Teixeira, AO Falcao. 2013. Noncontiguous atom matching structural similarity function. J. Chem. Inf. Model., 53(10), pp 2511–2524. DOI: 10.1021/ci400324u.

