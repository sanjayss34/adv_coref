import json
import os
import sys
import random
import copy
import time

all_countries_path = '/scratch/sanjay/allCountries.txt'
countries_only_path = '/scratch/sanjay/countryInfo.txt'
last_names_path = '/scratch/sanjay/last_names.txt'
first_names_path = 'firstname-gender-score.txt'
gap_path = '/scratch/sanjay/gap-coreference/'

def randomly_insert_gpe(input_examples, test_gpe_fname, train_gpe_fname):
    examples = [copy.deepcopy(example) for example in input_examples]
    geofile = open(all_countries_path)
    countries_file = open(countries_only_path)
    geolines = geofile.readlines()
    countries_lines = countries_file.readlines()
    countries_set = set()
    for line in countries_lines:
        country_name = line.split('\t')[4].strip().lower()
        countries_set.add(country_name)
    countries_set = sorted(list(countries_set))
    loc_to_code = {}
    loc_types = {'ADM1', 'ADM1H', 'ADM2', 'ADM2H', 'ADM3', 'ADM3H', 'ADM4', 'ADM4H', 'ADM5'}
    code_to_loc = {t: {} for t in loc_types}
    for line in geolines:
        parts = [part.strip() for part in line.split('\t')]
        if parts[6] != 'A' or parts[7] not in loc_types:
            continue
        if any(c.isdigit() for c in parts[1]):
            continue
        loc_to_code[parts[1].lower()] = parts[7]
        name_parts = parts[1].lower().split()
        if len(name_parts) not in code_to_loc[parts[7]]:
            code_to_loc[parts[7]][len(name_parts)] = []
        code_to_loc[parts[7]][len(name_parts)].append(parts[1].lower())
    for t in code_to_loc:
        for length in code_to_loc[t]:
            code_to_loc[t][length] = sorted(code_to_loc[t][length])
    gpe_file = open(train_gpe_fname)
    gpe_lines = gpe_file.readlines()
    gpe_examples = [json.loads(line) for line in gpe_lines]
    train_gpe_names = set()
    for example in gpe_examples:
        # entity_indices = example['entity_indices']
        conversion_map = {}
        gpe_indices = set(tuple(t) for t in example['people'])
        words = [word for sent in example['sentences'] for word in sent]
        for i in gpe_indices:
            name_parts = words[i[0]:i[1]+1]
            name = ' '.join(name_parts)
            train_gpe_names.add(name.lower())
    for code in code_to_loc:
        for length in code_to_loc[code]:
            code_to_loc[code][length] = list(set(code_to_loc[code][length])-train_gpe_names)
    gpe_file = open(test_gpe_fname)
    gpe_lines = gpe_file.readlines()
    gpe_examples = {json.loads(line)['doc_key']: json.loads(line) for line in gpe_lines}
    code_indices = {}
    for t in loc_types:
        code_indices[t] = {}
        for length in code_to_loc[t]:
            code_indices[t][length] = 0
            random.shuffle(code_to_loc[t][length])
    # code_indices = {t: 0 for t in loc_types}
    count = 0
    new_examples = []
    for example in examples:
        print(example['doc_key'])
        entity_indices = example['entity_indices']
        conversion_map = {}
        gpe_indices = set(tuple(t) for t in gpe_examples[example['doc_key']]['people'])
        example['changed_entities'] = {}
        for entity in entity_indices:
            is_gpe = False
            replacement_name = None
            replacement_name_parts = None
            name_parts = entity.split()
            for pair in entity_indices[entity]:
                if tuple(pair) in gpe_indices:
                    is_gpe = True
                    break
            if is_gpe: # and len(name_parts) == 1:
                if entity.lower() in countries_set:
                    continue
                if entity.lower() in loc_to_code:
                    count += 1
                    code = loc_to_code[entity.lower()]
                    length = len(name_parts)
                    replacement_name = code_to_loc[code][length][code_indices[code][length]].decode('utf-8')
                    replacement_name_parts = replacement_name.split()
                    code_indices[code][length] = code_indices[code][length]+1
            new_sentences = []
            indices = sorted(tuple(t) for t in entity_indices[entity])
            indices_index = 0
            token = 0
            offset = 0
            for sent in example['sentences']:
                new_sentence = []
                while token < len(sent)+offset:
                    if indices_index < len(indices) and token == indices[indices_index][0] and replacement_name is not None:
                        for j in range(indices[indices_index][1]-indices[indices_index][0]+1):
                            if sent[token-offset+j][0].islower():
                                new_sentence.append(replacement_name_parts[j])
                            else:
                                new_sentence.append(replacement_name_parts[j].title())
                        token += indices[indices_index][1]-indices[indices_index][0]+1
                        indices_index += 1
                    else:
                        if type(sent[token-offset]) == str:
                            sent[token-offset] = sent[token-offset].decode('utf-8')
                        new_sentence.append(sent[token-offset])
                        token += 1
                offset += len(sent)
                new_sentences.append(new_sentence)
            example['sentences'] = new_sentences
            if replacement_name is not None:
                example['changed_entities'][entity] = replacement_name
        new_examples.append(example)
    print('Count', count)
    return new_examples

def randomly_insert_per(input_examples, test_per_fname, train_per_fname, start_index=0, end_index=10000):
    examples = [copy.deepcopy(example) for example in input_examples]
    last_name_file = open(last_names_path)
    last_name_lines = last_name_file.readlines()
    last_names = []
    for line in last_name_lines:
        last_names.append(line.split()[0])
    train_file = open(train_per_fname)
    lines = train_file.readlines()
    train_examples = [json.loads(line) for line in lines]
    train_name_parts = set()
    for example in train_examples:
        words = [word for sent in example['sentences'] for word in sent]
        for indices in example['people']:
            for i in range(indices[0], indices[1]+1):
                train_name_parts.add(words[i].lower())
    first_name_file = open(first_names_path)
    first_name_lines = first_name_file.readlines()
    first_names_male = []
    first_names_female = []
    male_score_map = {}
    for line in first_name_lines[1:]:
        parts = line.split()
        male_score_map[parts[0].lower()] = float(parts[1])
        if float(parts[1]) > 0.7:
            first_names_male.append(parts[0])
        elif float(parts[1]) < 0.3:
            first_names_female.append(parts[0])
    gap_v_lines = (open(os.path.join(gap_path, 'gap-validation.tsv'))).readlines()
    gap_d_lines = (open(os.path.join(gap_path, 'gap-development.tsv'))).readlines()
    gap_t_lines = (open(os.path.join(gap_path, 'gap-test.tsv'))).readlines()
    gap_names = set()
    for line in gap_v_lines[1:]+gap_d_lines[1:]+gap_t_lines[1:]:
        parts = line.split('\t')
        A_parts = parts[4].strip().split()
        B_parts = parts[7].strip().split()
        for part in A_parts:
            gap_names.add(part.lower())
        for part in B_parts:
            gap_names.add(part.lower())
    first_names_male = list(set(first_names_male)-gap_names-train_name_parts)
    first_names_female = list(set(first_names_female)-gap_names-train_name_parts)
    last_names = list(set(last_names)-gap_names-train_name_parts)
    print(len(first_names_male), len(first_names_female), len(last_names))
    first_names_male = first_names_male[start_index:end_index]
    first_names_female = first_names_female[start_index:end_index]
    last_names = last_names[start_index:end_index]
    print(len(first_names_male), len(first_names_female), len(last_names))
    per_file = open(test_per_fname)
    per_lines = per_file.readlines()
    per_examples = {}
    for line in per_lines:
        example = json.loads(line)
        per_examples[example['doc_key']] = example
    last_name_index = 0
    first_male_index = 0
    first_female_index = 0
    random.shuffle(last_names)
    random.shuffle(first_names_male)
    random.shuffle(first_names_female)
    count = 0
    for example in examples:
        entity_indices = example['entity_indices']
        for entity in entity_indices:
            is_person = False
            for pair in entity_indices[entity]:
                if pair in per_examples[example['doc_key']]['people']:
                    # if pair in example['people']:
                    is_person = True
                    break
            if is_person:
                name_parts = entity.split()
                name_parts = [np.encode('utf-8') for np in name_parts]
                pair_index = 0
                entity_indices[entity] = sorted([tuple(pair) for pair in entity_indices[entity]])
                conversion_map = {}
                conversion_map[name_parts[-1]] = last_names[last_name_index].encode('utf-8').lower()
                last_name_index += 1
                new_name_parts = name_parts[:-1]+[conversion_map[name_parts[-1]]]
                count += 1
                words = []
                for sent in example['sentences']:
                    for word in sent:
                        if type(word) == unicode:
                            words.append(word.encode('utf-8'))
                        else:
                            words.append(word)
                cluster_phrases_lower = [' '.join(words[m[0]:m[1]+1]) for m in example['clusters'][example['entity_cluster'][entity]]]
                if len(name_parts) > 1:
                    if (name_parts[0].lower() not in male_score_map or male_score_map[name_parts[0].lower()] >= 0.5 or 'he' in cluster_phrases_lower or 'him' in cluster_phrases_lower or 'his' in cluster_phrases_lower) and ('she' not in cluster_phrases_lower and 'her' not in cluster_phrases_lower and 'hers' not in cluster_phrases_lower):
                        conversion_map[name_parts[0]] = first_names_male[first_male_index].lower()
                        first_male_index += 1
                    else:
                        conversion_map[name_parts[0]] = first_names_female[first_female_index].lower()
                        first_female_index += 1
                    new_name_parts = [conversion_map[name_parts[0]]] + name_parts[1:-1] + [conversion_map[name_parts[-1]]]
                new_sentences = []
                sentence_num = 0
                offset = 0
                while sentence_num < len(example['sentences']):
                    new_sentence = []
                    token = 0
                    while token < len(example['sentences'][sentence_num]):
                        if pair_index < len(entity_indices[entity]) and token+offset >= entity_indices[entity][pair_index][0] and token+offset <= entity_indices[entity][pair_index][1]:
                            if example['sentences'][sentence_num][token] in conversion_map:
                                if example['sentences'][sentence_num][token][0].isupper():
                                    new_sentence.append(conversion_map[example['sentences'][sentence_num][token]].title())
                                else:
                                    new_sentence.append(conversion_map[example['sentences'][sentence_num][token]])
                            else:
                                new_sentence.append(example['sentences'][sentence_num][token])
                            if token+offset == entity_indices[entity][pair_index][1]:
                                pair_index += 1
                        else:
                            new_sentence.append(example['sentences'][sentence_num][token])
                        token += 1
                    new_sentence_decoded = []
                    for word in new_sentence:
                        if type(word) == unicode:
                            new_sentence_decoded.append(word.encode('utf-8'))
                        else:
                            new_sentence_decoded.append(word)
                    new_sentences.append(new_sentence_decoded)
                    offset += len(example['sentences'][sentence_num])
                    sentence_num += 1
                try:
                    # new_entity_name = ' '.join(new_name_parts)
                    # example['entities'][new_entity_name] = example['entities'][entity]
                    # example['clusters'][new_entity_name] = example['clusters'][entity]
                    # example['entity_indices'][new_entity_name] = example['entity_indices'][entity]
                    # del example['entities'][entity]
                    # del example['entity_indices'][entity]
                    # del example['clusters'][entity]
                    example['sentences'] = new_sentences
                except Exception as e:
                    pass
    print('Count', count)
    return examples
