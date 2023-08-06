#! /usr/bin/env python
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2013. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt. Contact: ctb@msu.edu
#
import sys

file = open(sys.argv[1], 'r')

group_index = sys.argv[1].find('group')
group = sys.argv[1][group_index + 5:group_index + 8]
check_id2 = ''
count_total = 0
count_paired = 0

for line in file:
    count_total += 1
    line = line.rstrip().split('\t')

    # if there is mismatch the len(line)=10
    read = line[0]
    check_id1 = read[:-2]
    # print read, check_id1, check_id2
    if check_id1 == check_id2:
        count_paired += 1
        # print check_id1, check_id2

    check_id2 = check_id1

print group, count_total, count_paired
