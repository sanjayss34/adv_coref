import spacy
import json
import sys
import util
import os

if __name__ == '__main__':
    nlp = spacy.load('en')
    f = open(sys.argv[1])
    examples = [json.loads(line) for line in f.readlines()]
    f_out = open(sys.argv[2], 'w+')
    for example in examples:
        words = util.flatten(example['sentences'])
        doc = spacy.tokens.Doc(vocab=nlp.vocab, words=words)
        for name, proc in nlp.pipeline:
            doc = proc(doc)
        new_clusters = {}
        entities = {}
        entity_indices = {}
        entity_cluster = {}
        for j, clust in enumerate(example['clusters']):
            finished_clust = False
            names = set()
            name_indices = []
            longest_name = ""
            for mention in clust:
                pmention = None
                span = doc[mention[0]:mention[1]+1]
                # for entity_mention in entity_mentions:
                for entity_mention in example['people']:
                    if (span.root.i >= entity_mention[0] and span.root.i <= entity_mention[1]):
                        name = ' '.join(words[entity_mention[0]:entity_mention[1]+1])
                        names.add(name)
                        name_indices.append(entity_mention)
                        if len(name) > len(longest_name):
                            longest_name = name
            if len(longest_name) > 0 and longest_name not in new_clusters.keys():
                new_clusters[longest_name] = clust
                entities[longest_name] = list(names)
                entity_indices[longest_name] = list(name_indices)
                entity_cluster[longest_name] = j
        example['entities'] = entities
        example['entity_indices'] = entity_indices
        example['entity_cluster'] = entity_cluster
        example['clusters_dict'] = new_clusters
        f_out.write(json.dumps(example)+'\n')
        print(example['doc_key'])
    f_out.close()
