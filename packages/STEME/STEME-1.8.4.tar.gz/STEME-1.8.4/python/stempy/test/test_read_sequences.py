#
# Copyright John Reid 2010, 2011
#

"""
Test read sequences.
"""

from setup_environment import init_test_env, update_path_for_stempy, fasta_dir
init_test_env(__file__)
update_path_for_stempy()

import stempy, os

options = stempy.get_default_options()

# check reading in correct amount of data
fasta_file = os.path.join(fasta_dir(), 'find-starts-test.fa')
num_bases, seqs, ids, index = stempy.read_sequences(fasta_file, options)
assert num_bases == 22
assert len(seqs) == 2
assert '75' in ids
assert '76' in ids
assert 2 == len(ids)
