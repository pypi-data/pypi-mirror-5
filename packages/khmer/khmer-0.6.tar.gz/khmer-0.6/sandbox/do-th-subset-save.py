#! /usr/bin/env python
#
# This file is part of khmer, http://github.com/ged-lab/khmer/, and is
# Copyright (C) Michigan State University, 2009-2013. It is licensed under
# the three-clause BSD license; see doc/LICENSE.txt. Contact: ctb@msu.edu
#
import khmer
import sys
import threading
import Queue
import gc
import os.path

K = 32
HASHTABLE_SIZE = int(4e9)
N_HT = 4

SUBSET_SIZE = int(2e5)
N_THREADS = 8

ht = khmer.new_hashbits(K, HASHTABLE_SIZE, N_HT)

###


def worker(q, basename):
    while 1:
        try:
            (ht, n, start, stop) = q.get(False)
        except Queue.Empty:
            print 'exiting'
            return

        outfile = basename + '.subset.%d' % (n,)
        if os.path.exists(outfile + '.pmap'):
            print 'SKIPPING', basename, ' -- already exists'
            continue

        print 'starting:', basename, n
        subset = ht.do_subset_partition(start, stop)

        # filtering:
#        print 'filtering'
#        tagmap = ht.load_tagmap(basename + '.tagset')
#        ht.subset_maxify_partition_size(subset, tagmap)
#        ht.discard_tags(

        print 'saving:', basename, n

        outfile = basename + '.subset.%d' % (n,)
        ht.save_subset_partitionmap(subset, outfile + '.pmap')
        del subset
        gc.collect()


def main(filename):
    basename = os.path.basename(filename)

    print 'K', K
    print 'HASHTABLE SIZE %g' % HASHTABLE_SIZE
    print 'SUBSET SIZE', SUBSET_SIZE
    print 'N THREADS', N_THREADS
    print '--'

    # populate the hash table and tag set
    print 'reading sequences and loading tagset from %s...' % (filename,)
    # ht.do_threaded_partition(filename)
    ht.consume_fasta_and_tag(filename)

    # save to a file (optional)
    print 'saving...'
    ht.save(basename + '.ht')
    print 'saving tagset...'
    ht.save_tagset(basename + '.tagset')

    # calculate the hashtable occupancy
    print '---'
    print 'hashtable occupancy:', ht.n_occupied() / float(HASHTABLE_SIZE)
    print '---'

    # divide the tags up into subsets
    divvy = ht.divide_tags_into_subsets(SUBSET_SIZE)
    n_subsets = len(divvy)
    divvy.append(0)

    # build a queue of tasks:
    worker_q = Queue.Queue()

    for i in range(0, n_subsets):
        start = divvy[i]
        end = divvy[i + 1]
        worker_q.put((ht, i, start, end))

    print 'enqueued %d subset tasks' % n_subsets
    open('%s.info' % basename, 'w').write('%d subsets total\n' % (n_subsets))

    threads = []
    for n in range(N_THREADS):
        t = threading.Thread(target=worker, args=(worker_q, basename))
        threads.append(t)
        t.start()

    print 'started threads'

    # wait for threads
    for t in threads:
        t.join()

    print 'done! see %s.subset.*.pmap' % (basename,)

if __name__ == '__main__':
    main(sys.argv[1])
