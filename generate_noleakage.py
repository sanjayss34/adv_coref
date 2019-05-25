import sys
import json
import pickle
import replace_data
from replace_data import randomly_insert_gpe, randomly_insert_per
from copy import deepcopy

with open(sys.argv[1]) as f:
    original_examples = [json.loads(line) for line in f.readlines()]
replace_data.random.setstate(pickle.load(open('random.pkl')))
examples = randomly_insert_gpe(original_examples, sys.argv[5], sys.argv[6])
examples = randomly_insert_per(examples, sys.argv[3], sys.argv[4], start_index=10000, end_index=20000)
with open(sys.argv[2], 'w+') as f:
    for ex in examples:
        f.write(json.dumps(ex)+'\n')
    f.close()
