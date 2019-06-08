#!/usr/bin/env python

import re
import os
import sys
import json
import tempfile
import subprocess
import collections

import util
import conll

regex = re.compile('[^a-zA-Z]')

class DocumentState(object):
  def __init__(self):
    self.doc_key = None
    self.text = []
    self.text_speakers = []
    self.speakers = []
    self.sentences = []
    self.clusters = collections.defaultdict(list)
    self.stacks = collections.defaultdict(list)
    self.people = []
    self.person_start = None

  def assert_empty(self):
    assert self.doc_key is None
    assert len(self.text) == 0
    assert len(self.text_speakers) == 0
    assert len(self.sentences) == 0
    assert len(self.speakers) == 0
    assert len(self.clusters) == 0
    assert len(self.stacks) == 0

  def assert_finalizable(self):
    assert self.doc_key is not None
    assert len(self.text) == 0
    assert len(self.text_speakers) == 0
    assert len(self.sentences) > 0
    assert len(self.speakers) > 0
    assert all(len(s) == 0 for s in self.stacks.values())

  def finalize(self):
    merged_clusters = []
    for c1 in self.clusters.values():
      existing = None
      for m in c1:
        for c2 in merged_clusters:
          if m in c2:
            existing = c2
            break
        if existing is not None:
          break
      if existing is not None:
        print("Merging clusters (shouldn't happen very often.)")
        existing.update(c1)
      else:
        merged_clusters.append(set(c1))
    merged_clusters = [list(c) for c in merged_clusters]
    all_mentions = util.flatten(merged_clusters)
    assert len(all_mentions) == len(set(all_mentions))

    return {
      "doc_key": self.doc_key,
      "sentences": self.sentences,
      "speakers": self.speakers,
      "clusters": merged_clusters,
      "people": self.people
    }

def normalize_word(word):
  if word == "/." or word == "/?":
    return word[1:]
  else:
    return word

def handle_line(line, document_state, ner_type):
  begin_document_match = re.match(conll.BEGIN_DOCUMENT_REGEX, line)
  if begin_document_match:
    document_state.assert_empty()
    document_state.doc_key = conll.get_doc_key(begin_document_match.group(1), begin_document_match.group(2))
    return None
  elif line.startswith("#end document"):
    document_state.assert_finalizable()
    return document_state.finalize()
  else:
    row = line.split()
    if len(row) == 0:
      document_state.sentences.append(tuple(document_state.text))
      del document_state.text[:]
      document_state.speakers.append(tuple(document_state.text_speakers))
      del document_state.text_speakers[:]
      return None
    assert len(row) >= 12

    word = normalize_word(row[3])
    coref = row[-1]
    doc_key = conll.get_doc_key(row[0], row[1])
    speaker = row[9]
    person = row[10]

    word_index = len(document_state.text) + sum(len(s) for s in document_state.sentences)
    document_state.text.append(word)
    document_state.text_speakers.append(speaker)

    if coref != "-":
      for segment in coref.split("|"):
        if segment[0] == "(":
          if segment[-1] == ")":
            cluster_id = int(segment[1:-1])
            document_state.clusters[cluster_id].append((word_index, word_index))
          else:
            cluster_id = int(segment[1:])
            document_state.stacks[cluster_id].append(word_index)
        else:
          cluster_id = int(segment[:-1])
          start = document_state.stacks[cluster_id].pop()
          document_state.clusters[cluster_id].append((start, word_index))
    if ner_type in person:
        t = regex.sub('', person)
        if ')' in person:
            document_state.people.append((word_index, word_index))
        else:
            document_state.person_start = word_index
    elif ')' in person and document_state.person_start is not None:
        document_state.people.append((document_state.person_start, word_index))
        document_state.person_start = None
    return None

def minimize_partition(name, language, extension, label="", ner_type=""):
  input_path = "{}.{}.{}".format(name, language, extension)
  output_path = "{}.{}.{}.jsonlines".format(name, language, label)
  count = 0
  print "Minimizing {}".format(input_path)
  with open(input_path, "r") as input_file:
    with open(output_path, "w") as output_file:
      document_state = DocumentState()
      for line in input_file.readlines():
        if ner_type.upper() == 'PER':
          ner_type = 'PERSON'
        document = handle_line(line, document_state, ner_type.upper())
        if document is not None:
          output_file.write(json.dumps(document))
          output_file.write("\n")
          count += 1
          document_state = DocumentState()
  print "Wrote {} documents to {}".format(count, output_path)

def minimize_language(language, part, label, ner_type):
  if part == 'test':
    minimize_partition(part, language, "v4_gold_conll", label, ner_type)
  else:
    minimize_partition(part, language, "v4_auto_conll", label, ner_type)

if __name__ == "__main__":
  minimize_language("english", sys.argv[1], sys.argv[2], sys.argv[3])
