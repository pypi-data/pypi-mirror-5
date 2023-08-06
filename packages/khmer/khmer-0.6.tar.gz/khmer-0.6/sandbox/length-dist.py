#! /usr/bin/env python
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2013. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt. Contact: ctb@msu.edu
#

import sys
import screed
from screed import fasta

filein = sys.argv[1]

fp = open(filein)

lengths = [0] * 100
for n, record in enumerate(fasta.fasta_iter(fp)):
    length = len(record['sequence']) - 32
    lengths[length] += 1

for n, i in enumerate(lengths):
    print n, i
