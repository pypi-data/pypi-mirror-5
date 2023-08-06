NAMS: Non-contiguous Atom Matching Structural Similarity
=========================================================

NAMS is a similarity method based on atom alignment for the analysis of structural similarity between molecules. This method is based on the comparison 
of the bonding profiles of atoms on comparable molecules, including features that are seldom found in other structural or graph matching approaches like 
chirality or double bond stereoisomerism. The similarity measure is then defined on the annotated molecular graph, based on an iterative directed graph 
similarity procedure and  optimal atom alignment between atoms using a pairwise matching algorithm. With the proposed approach the similarities detected 
are more intuitively understood because similar atoms in the molecules are explicitly shown. This module implements NAMS and also supports the classification 
of the type of isomerism present in a given atom or bond of a molecule. 

For background and cite the authors in any work or product based on this material:

- Ana L. Teixeira and Andre O. Falcao 2013: A non-contiguous atom matching structural similarity function. Journal of Chemical Information and Modeling(DOI: 10.1021/ci400324u)

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

AL Teixeira, AO Falcao. 2013. A non-contiguous atom matching structural similarity function. J. Chem. Inf. Model. DOI: 10.1021/ci400324u.

