import sys
from gap_coreference.gap_scorer import read_annotations
from gap_coreference.constants import Gender
from scipy.stats import chi2

if __name__ == '__main__':
    correct1_incorrect2 = 0
    correct2_incorrect1 = 0
    gold = read_annotations(sys.argv[1], is_gold=True)
    system1 = read_annotations(sys.argv[2], is_gold=False)
    system2 = read_annotations(sys.argv[3], is_gold=False)
    gender = None
    if len(sys.argv) == 5:
        gender = sys.argv[4]
        if gender.lower() not in {'f', 'm'}:
            print('Invalid gender')
            sys.exit(0)
    for k in gold:
        if gender is not None:
            if gold[k].gender == Gender.MASCULINE and gender.lower() == 'f':
                continue
            elif gold[k].gender == Gender.FEMININE and gender.lower() == 'm':
                continue
        if gold[k].name_a_coref and system1[k].name_a_coref and (not system2[k].name_a_coref):
            correct1_incorrect2 += 1
        elif gold[k].name_a_coref and system2[k].name_a_coref and (not system1[k].name_a_coref):
            correct2_incorrect1 += 1
        elif (not gold[k].name_a_coref) and (not system1[k].name_a_coref) and system2[k].name_a_coref:
            correct1_incorrect2 += 1
        elif (not gold[k].name_a_coref) and (not system2[k].name_a_coref) and system1[k].name_a_coref:
            correct2_incorrect1 += 1
        if gold[k].name_b_coref and system1[k].name_b_coref and (not system2[k].name_b_coref):
            correct1_incorrect2 += 1
        elif gold[k].name_b_coref and system2[k].name_b_coref and (not system1[k].name_b_coref):
            correct2_incorrect1 += 1
        elif (not gold[k].name_b_coref) and (not system1[k].name_b_coref) and system2[k].name_b_coref:
            correct1_incorrect2 += 1
        elif (not gold[k].name_b_coref) and (not system2[k].name_b_coref) and system1[k].name_b_coref:
            correct2_incorrect1 += 1
    test_stat = float((correct1_incorrect2-correct2_incorrect1)**2)/(correct1_incorrect2+correct2_incorrect1)
    pval = 1.0-chi2.cdf(test_stat, df=1)
    print('p-value: ' + str(pval))
