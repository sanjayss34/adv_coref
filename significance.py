import sys
import numpy as np

def compute_t(lines1, lines2):
    recalls1 = [[0, 0], [0, 0], [0, 0]]
    precisions1 = [[0, 0], [0, 0], [0, 0]]
    for s in range(3):
        start = s
        if start == 2:
            start += 1
        for i in range(start*len(lines1)/4, (start+1)*len(lines1)/4):
            line = lines1[i]
            recall_num = float(line.split('(')[1].split('/')[0])
            recall_den = float(line.split(')')[0].split('/')[1])
            recalls1[s][0] += recall_num
            recalls1[s][1] += recall_den
            precision_num = float(line.split('(')[2].split('/')[0])
            precision_den = float(line.split(')')[1].split('/')[1])
            precisions1[s][0] += precision_num
            precisions1[s][1] += precision_den
    f1s1 = [2*(p[0]/float(p[1]))*(r[0]/float(r[1]))/(p[0]/float(p[1])+r[0]/float(r[1])) for p, r in zip(precisions1, recalls1)]
    recalls2 = [[0, 0], [0, 0], [0, 0]]
    precisions2 = [[0, 0], [0, 0], [0, 0]]
    for s in range(3):
        start = s
        if start == 2:
            start += 1
        for i in range(start*len(lines2)/4, (start+1)*len(lines2)/4):
            line = lines2[i]
            recall_num = float(line.split('(')[1].split('/')[0])
            recall_den = float(line.split(')')[0].split('/')[1])
            recalls2[s][0] += recall_num
            recalls2[s][1] += recall_den
            precision_num = float(line.split('(')[2].split('/')[0])
            precision_den = float(line.split(')')[1].split('/')[1])
            precisions2[s][0] += precision_num
            precisions2[s][1] += precision_den
    f1s2 = [2*(p[0]/float(p[1]))*(r[0]/float(r[1]))/(p[0]/float(p[1])+r[0]/float(r[1])) for p, r in zip(precisions2, recalls2)]
    conllf1_1 = np.mean(f1s1)
    conllf1_2 = np.mean(f1s2)
    tval = conllf1_1-conllf1_2
    return tval

if __name__ == '__main__':
    f1 = open(sys.argv[1])
    f2 = open(sys.argv[2])
    lines1 = f1.readlines()
    lines2 = f2.readlines()
    original_t = compute_t(lines1, lines2)
    print('T: ' + str(original_t))
    greater = 0
    total = 10000
    for _ in range(total):
        lines1new = []
        lines2new = []
        for line1, line2 in zip(lines1, lines2):
            if np.random.rand() >= 0.5:
                lines1new.append(line1)
                lines2new.append(line2)
            else:
                lines1new.append(line2)
                lines2new.append(line1)
        tval = compute_t(lines1new, lines2new)
        if tval >= original_t:
            greater += 1
    print('p-value: ' + str(float(greater)/total))
