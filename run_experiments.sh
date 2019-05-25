export GAP_ROOT=gap_coreference/

# Original CoNLL-2012 test set experiments
python evaluate_conll.py final test.english.all.entity.jsonlines test.english.lee2018.jsonlines
python evaluate_conll.py final test.english.all.entity.jsonlines test.english.adv.jsonlines adv

# No Leakage CoNLL-2012 test set experiments
python evaluate_conll.py final test.english.replace.jsonlines test.english.replace.lee2018.jsonlines
python evaluate_conll.py final test.english.replace.jsonlines test.english.replace.adv.jsonlines adv

# Convert jsonlines files to conll files
python json_to_conll.py test.english.all.entity.jsonlines test.english.conll y
python json_to_conll.py test.english.replace.jsonlines test.english.replace.conll y
python json_to_conll.py test.english.lee2018.jsonlines test.english.lee2018.conll n
python json_to_conll.py test.english.adv.jsonlines test.english.adv.conll n
python json_to_conll.py test.english.replace.lee2018.jsonlines test.english.replace.lee2018.conll n
python json_to_conll.py test.english.replace.adv.jsonlines test.english.replace.adv.conll n

# Run official CoNLL-2012 Scorer
perl reference-coreference-scorers/scorer.pl all test.english.conll test.english.lee2018.conll > conll_output_lee2018.txt
perl reference-coreference-scorers/scorer.pl all test.english.conll test.english.adv.conll > conll_output_adv.txt
perl reference-coreference-scorers/scorer.pl all test.english.replace.conll test.english.replace.lee2018.conll > conll_output_replace_lee2018.txt
perl reference-coreference-scorers/scorer.pl all test.english.replace.conll test.english.replace.adv.conll > conll_output_replace_adv.txt

# Report results for Original CoNLL-2012 Test Set
python compute_conll_f1.py conll_output_lee2018.txt OriginalCoNLLTest_Lee2018
python compute_conll_f1.py conll_output_adv.txt OriginalCoNLLTest_Adversarial
cat conll_output_lee2018.txt | grep "Recall" | grep -v "Coreference" | grep -v "coreference" | grep -v "Mention" | grep -v "BLANC" > conll_output_lee2018_filtered.txt
cat conll_output_adv.txt | grep "Recall" | grep -v "Coreference" | grep -v "coreference" | grep -v "Mention" | grep -v "BLANC" > conll_output_adv_filtered.txt
python significance.py conll_output_adv_filtered.txt conll_output_lee2018_filtered.txt

# Report results for No Leakage CoNLL-2012 Test Set
python compute_conll_f1.py conll_output_replace_lee2018.txt NoLeakageCoNLLTest_Lee2018
python compute_conll_f1.py conll_output_replace_adv.txt NoLeakageCoNLLTest_Adversarial
cat conll_output_replace_lee2018.txt | grep "Recall" | grep -v "Coreference" | grep -v "coreference" | grep -v "Mention" | grep -v "BLANC" > conll_output_replace_lee2018_filtered.txt
cat conll_output_replace_adv.txt | grep "Recall" | grep -v "Coreference" | grep -v "coreference" | grep -v "Mention" | grep -v "BLANC" > conll_output_replace_adv_filtered.txt
python significance.py conll_output_replace_adv_filtered.txt conll_output_replace_lee2018_filtered.txt

# Run experiments and report results for GAP Test Set
echo "GAP Test Results -- Lee2018"
python evaluate_gap.py final "${GAP_ROOT}gap-test.tsv" gap_test_lee2018.tsv gap_test_lee2018.jsonlines
echo "GAP Test Results -- Adversarial"
python evaluate_gap.py final "${GAP_ROOT}gap-test.tsv" gap_test_adv.tsv gap_test_adv.jsonlines adv
python significance_gap.py "${GAP_ROOT}gap-test.tsv" gap_test_lee2018.tsv gap_test_adv.tsv
