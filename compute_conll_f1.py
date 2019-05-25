import sys

with open(sys.argv[1]) as f:
    lines = f.readlines()
    f1s = []
    passed_ceafm = False
    for line in lines:
        if "Coreference" in line:
            if len(f1s) == 2 and not passed_ceafm:
                passed_ceafm = True
                continue
            f1s.append(float(line.split()[-1].split('%')[0]))
            if len(f1s) == 3:
                break
print(sys.argv[2] + ' CoNLL F1: ' + str(float(sum(f1s))/len(f1s)))
