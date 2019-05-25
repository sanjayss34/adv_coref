#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time
import json
import numpy as np

import tensorflow as tf
# import ecm as cm
# import name_coref_model as cm
# import coref_model as cm
# import coref_model_nesim as cm
# import coref_model_nameloss as cm
# import coref_model_original_data as cm
import coref_model_original as cm
# import coref_model_acronym as cm
# import coref_model_augment as cm
# import coref_model_mentions as cm
# import coref_model_adv3 as cm
import util
from demo_original import make_predictions
import evalnew
from copy import deepcopy

if __name__ == "__main__":
  config = util.initialize_from_env()

  report_frequency = config["report_frequency"]
  eval_frequency = config["eval_frequency"]

  model = cm.CorefModel(config)
  saver = tf.train.Saver()

  log_dir = config["log_dir"]
  writer = tf.summary.FileWriter(log_dir, flush_secs=20)

  max_f1 = 0

  # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.7)

  # with tf.Session(config=tf.ConfigProto(gpu_options=gpu_options)) as session:
  with tf.Session() as session:
    session.run(tf.global_variables_initializer())
    model.start_enqueue_thread(session)
    accumulated_loss = 0.0
    accumulated_loss2 = 0.0

    ckpt = tf.train.get_checkpoint_state(log_dir)
    if ckpt and ckpt.model_checkpoint_path:
      print("Restoring from: {}".format(ckpt.model_checkpoint_path))
      saver.restore(session, ckpt.model_checkpoint_path)
      _, max_f1 = model.evaluate(session)
      print('max_f1: ' + str(max_f1))
      # if True:
      """saver.restore(session, os.path.join(log_dir, 'model.max.ckpt'))
      evaluator = evalnew.NameCorefEvaluator()
      f = open('/scratch/sanjay/dev.all.gold.jsonlines')
      examples = {}
      lines = f.readlines()
      for line in lines:
        example = json.loads(line)
        input_example = deepcopy(example)
        input_example = make_predictions("", model, session, input_example)
        example['predicted'] = input_example['predicted_clusters']
        evaluator.process_file(example)
      evaluator.get_name_pred_clusts()
      evaluator.mistake_types()
      evaluator.f1()
      max_f1 = np.nanmean(util.flatten(evaluator.f1s))"""

    initial_time = time.time()
    while True:
      # tf_loss, tf_global_step, _, p1, p2, p3, p4, p5, p6, p7, p8 = session.run([model.loss, model.global_step, model.train_op, model.same_cluster_indicator, model.non_dummy_indicator, model.pairwise_labels, model.tokens, model.gold_starts, model.gold_ends, model.cluster_ids, model.top_antecedent_cluster_ids])
      # tf_loss, tf_global_step, _, antecedent_ids, antecedent_scores = session.run([model.loss, model.global_step, model.train_op, model.top_antecedent_labels, model.top_antecedent_scores])
      # tf_loss, tf_global_step, tf_loss2, _, antecedent_scores, antecedent_labels = session.run([model.loss, model.global_step, model.loss2, model.train_op, model.predictions[-2], model.predictions[-1]])
      tf_loss, tf_global_step, _ = session.run([model.loss, model.global_step, model.train_op])
      # print(antecedent_ids)
      # print(antecedent_scores)
      # print(antecedent_scores)
      # print(antecedent_labels)
      accumulated_loss += tf_loss
      # accumulated_loss2 += tf_loss2

      if tf_global_step % report_frequency == 0:
        total_time = time.time() - initial_time
        steps_per_second = tf_global_step / total_time

        average_loss = accumulated_loss / report_frequency
        average_loss2 = accumulated_loss2 / report_frequency
        print("[{}] loss={:.2f}, loss2={:.2f} steps/s={:.2f}".format(tf_global_step, average_loss, average_loss2, steps_per_second))
        sys.stdout.flush()
        writer.add_summary(util.make_summary({"loss": average_loss}), tf_global_step)
        """print('a ' + str(p1))
        print('b ' + str(p2))
        print('c '+str(p3))
        print('d '+str(p4))
        print('e '+str(p5))
        print('f '+str(p6))
        print('g '+str(p7))
        print('h '+str(p8))
        print('i '+str(make_predictions(text="", model=model, session=session, example=example)))"""
        accumulated_loss = 0.0
        accumulated_loss2 = 0.0

      if tf_global_step % eval_frequency == 0:
        saver.save(session, os.path.join(log_dir, "model"), global_step=tf_global_step)
        eval_summary, eval_f1 = model.evaluate(session)
        """evaluator = evalnew.NameCorefEvaluator()
        f = open('/scratch/sanjay/dev.all.gold.jsonlines')
        lines = f.readlines()
        for line in lines:
          example = json.loads(line)
          input_example = deepcopy(example)
          input_example = make_predictions("", model, session, input_example)
          example['predicted'] = input_example['predicted_clusters']
          evaluator.process_file(example)
        evaluator.get_name_pred_clusts()
        evaluator.mistake_types()
        evaluator.f1()
        eval_f1 = np.nanmean(util.flatten(evaluator.f1s))"""

        if eval_f1 > max_f1:
          max_f1 = eval_f1
          util.copy_checkpoint(os.path.join(log_dir, "model-{}".format(tf_global_step)), os.path.join(log_dir, "model.max.ckpt"))

        # writer.add_summary(eval_summary, tf_global_step)
        writer.add_summary(util.make_summary({"max_eval_f1": max_f1}), tf_global_step)

        print("[{}] evaL_f1={:.2f}, max_f1={:.2f}".format(tf_global_step, eval_f1, max_f1))
        # if tf_global_step >= 30000:
        #   break
