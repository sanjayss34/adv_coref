#!/bin/bash

python minimize_with_ner.py test per PER
python minimize_with_ner.py test gpe GPE
python merge_ner_types.py test.english.per.jsonlines test.english.gpe.jsonlines test.english.all.jsonlines
python minimize_with_ner.py train per PER
python minimize_with_ner.py train gpe GPE

python find_mention_heads.py test.english.all.jsonlines test.english.all.entity.jsonlines

python generate_noleakage.py test.english.all.entity.jsonlines test.english.replace.jsonlines test.english.per.jsonlines train.english.per.jsonlines test.english.gpe.jsonlines train.english.gpe.jsonlines
