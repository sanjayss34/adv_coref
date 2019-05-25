import tensorflow as tf
import coref_model_original as cm
import coref_model_adv as cm_adv
import util
import spacy
import os
import json
from demo import make_predictions
from gap_coreference.gap_scorer import Annotation, read_annotations, calculate_scores, make_scorecard
import sys

if __name__ == '__main__':
    config = util.initialize_from_env()
    config['context_embeddings']['path'] = config['context_embeddings_full']['path']
    adv = False
    if len(sys.argv) >= 6 and sys.argv[5].lower() == 'adv':
        adv = True
    if adv:
        model = cm_adv.CorefModel(config)
    else:
        model = cm.CorefModel(config)
    saver = tf.train.Saver()
    f = open(sys.argv[2])
    lines = f.readlines()
    nlp = spacy.load('en')
    system_annotations = {}
    output_file = open(sys.argv[3], 'w+')
    output_json_file = open(sys.argv[4], 'w+')
    with tf.Session() as sess:
        if adv:
            saver.restore(sess, os.path.join(config['adv_log_root'], 'final', 'model.max.ckpt'))
        else:
            model.restore(sess)
        for j, line in enumerate(lines[1:]):
            parts = line.split('\t')
            example_id = parts[0].strip()
            text = parts[1].strip()
            doc = nlp(unicode(text))
            sentences = [[unicode(str(w)) for w in sent] for sent in doc.sents]
            example = {'sentences': sentences, 'doc_key': 'nw', 'speakers': [['' for _ in sent] for sent in doc.sents], 'clusters': []}
            result = make_predictions(text, model, sess, example)
            words = util.flatten(result['sentences'])
            c = 0
            nameA = parts[4].strip()
            nameA_offset = int(parts[5].strip())
            nameB = parts[7].strip()
            nameB_offset = int(parts[8].strip())
            pronoun_char_offset = int(parts[3].strip())
            pronoun_index = None
            nameA_index = None
            nameB_index = None
            for k, token in enumerate(doc):
                if token.idx == pronoun_char_offset or (pronoun_index is None and k+1 < len(doc) and doc[k+1].idx > pronoun_char_offset):
                    pronoun_index = token.i
                elif token.idx == nameA_offset or (nameA_index is None and (k+1 >= len(doc) or doc[k+1].idx > nameA_offset)):
                    nameA_index = token.i
                elif token.idx == nameB_offset or (nameB_index is None and (k+1 >= len(doc) or doc[k+1].idx > nameB_offset)):
                    nameB_index = token.i
            nameA_end_index = nameA_index+len(nameA.split())-1
            nameB_end_index = nameB_index+len(nameB.split())-1
            clusterA = None
            clusterB = None
            annotation = Annotation()
            for cluster in result['predicted_clusters']:
                for mention in cluster:
                    if doc[nameA_index:nameA_end_index+1].root.i == doc[mention[0]:mention[1]+1].root.i or doc[nameA_index:nameA_end_index+1].root.head.i == doc[mention[0]:mention[1]+1].root.i:
                        clusterA = cluster
                    if doc[nameB_index:nameB_end_index+1].root.i == doc[mention[0]:mention[1]+1].root.i or doc[nameB_index:nameB_end_index+1].root.head.i == doc[mention[0]:mention[1]+1].root.i:
                        clusterB = cluster
            if clusterA is None:
                annotation.name_a_coref = False
            else:
                annotation.name_a_coref = ((pronoun_index, pronoun_index) in set(m for m in clusterA))
            if clusterB is None:
                annotation.name_b_coref = False
            else:
                annotation.name_b_coref = ((pronoun_index, pronoun_index) in set(m for m in clusterB))
            system_annotations[example_id] = annotation
            output_file.write(example_id+'\t'+str(annotation.name_a_coref)+'\t'+str(annotation.name_b_coref)+'\n')
            json_output = {'example_id': example_id, 'sentences': sentences, 'predicted_clusters': result['predicted_clusters']}
            output_json_file.write(json.dumps(json_output)+'\n')
    output_file.close()
    output_json_file.close()
    gold_annotations = read_annotations(sys.argv[2], True)
    print(make_scorecard(calculate_scores(gold_annotations, system_annotations)))
