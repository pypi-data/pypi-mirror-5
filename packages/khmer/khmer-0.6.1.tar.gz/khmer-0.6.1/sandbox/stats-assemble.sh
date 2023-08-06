#! /bin/bash
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2013. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt. Contact: ctb@msu.edu
#
scriptpath=$1
filename=$2


BASE=`basename $filename`

python $scriptpath/assemstats3.py 500 $BASE/contigs.fa > $BASE.stat 
