from demo import make_predictions
import os
import sys
import json
import tensorflow as tf
import spacy
import coref_model_adv as cm_adv
import coref_model as cm
import util
from copy import deepcopy

if __name__ == '__main__':
    eval_file = open(sys.argv[2])
    eval_lines = eval_file.readlines()
    res_file = open(sys.argv[3], 'w+')
    config = util.initialize_from_env()
    adv = False
    if len(sys.argv) >= 5 and sys.argv[4].lower() == 'adv':
        adv = True
    if adv:
        model = cm_adv.CorefModel(config)
    else:
        model = cm.CorefModel(config)
    saver = tf.train.Saver()
    with tf.Session() as session:
        if adv:
            saver.restore(session, os.path.join(config["adv_log_root"], 'final', 'model.max.ckpt'))
        else:
            model.restore(session)
        for line in eval_lines:
            example = json.loads(line)
            words = []
            sentences = []
            for sent in example['sentences']:
                sentences.append([])
                for word in sent:
                    if type(word) == unicode:
                        words.append(word.encode('utf-8'))
                    else:
                        words.append(word)
                    sentences[-1].append(words[-1])
            doc_key = str(example['doc_key'])
            res_example = make_predictions(' '.join(words), model, session, example=deepcopy(example))
            example['predicted'] = res_example['predicted_clusters']
            example['predicted_clusters'] = res_example['predicted_clusters']
            example['head_scores'] = res_example['head_scores']
            example['top_spans'] = res_example['top_spans']
            res_file.write(json.dumps(example)+'\n')
    res_file.close()
