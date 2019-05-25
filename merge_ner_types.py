import json
import sys

with open(sys.argv[1]) as f1:
    examples = [json.loads(line) for line in f1.readlines()]
with open(sys.argv[2]) as f2:
    for i, line in enumerate(f2.readlines()):
        example = json.loads(line)
        examples[i]['people'] += example['people']
with open(sys.argv[3], 'w+') as f3:
    for ex in examples:
        f3.write(json.dumps(ex)+'\n')
    f3.close()
