from __future__ import division

import numpy as np

from magpie.evaluation.rank_metrics import mean_average_precision, \
    mean_reciprocal_rank, ndcg_at_k, r_precision, precision_at_k
from magpie.misc.labels import get_labels


def evaluate_results(kw_conf, kw_vector, gt_answers):
    """
    Compute basic evaluation ranking metrics and return them
    :param kw_conf: vector with confidence levels, return by the LearningModel
    :param kw_vector: vector with tuples (doc_id:int, kw:unicode)
    :param gt_answers: dictionary of the form dict(doc_id:int=kws:set(unicode))

    :return: dictionary with basic metrics
    """
    y_true, y_pred = build_result_matrices(kw_conf, kw_vector, gt_answers)

    y_pred = np.fliplr(y_pred.argsort())
    for i in xrange(len(y_true)):
        y_pred[i] = y_true[i][y_pred[i]]

    return calculate_basic_metrics(y_pred)


def calculate_basic_metrics(y_pred):
    """ Calculate the basic metrics and return a dictionary with them. """

    return {
        'map': mean_average_precision(y_pred),
        'mrr': mean_reciprocal_rank(y_pred),
        'ndcg': np.mean([ndcg_at_k(row, len(row)) for row in y_pred]),
        'r_prec': np.mean([r_precision(row) for row in y_pred]),
        'p_at_3': np.mean([precision_at_k(row, 3) for row in y_pred]),
        'p_at_5': np.mean([precision_at_k(row, 5) for row in y_pred]),
    }


def build_result_matrices(lab_conf, lab_vector, gt_answers):
    """
    Build result matrices from dict with answers and candidate vector.
    :param lab_conf: vector with confidence levels, return by the LearningModel
    :param lab_vector: vector with tuples (doc_id:int, lab:unicode)
    :param gt_answers: dictionary of the form dict(doc_id:int=labs:set(unicode))

    :return: y_true, y_pred numpy arrays
    """
    labels = get_labels()
    label_indices = {lab: i for i, lab in enumerate(labels)}
    min_docid = min(gt_answers.keys())

    y_true = build_y_true(gt_answers, label_indices, min_docid)

    y_pred = np.zeros((len(gt_answers), len(labels)))

    for conf, (doc_id, lab) in zip(lab_conf, lab_vector):
        if lab in label_indices:
            index = label_indices[lab]
            y_pred[doc_id - min_docid][index] = conf

    return y_true, y_pred


def build_y_true(gt_answers, label_indices, min_docid):
    """
    Built the ground truth matrix
    :param gt_answers: dictionary with answers for documents
    :param label_indices: {lab: index} dictionary
    :param min_docid: the lowest doc_id in the batch

    :return: numpy array
    """
    y_true = np.zeros((len(gt_answers), len(label_indices)), dtype=np.bool_)

    for doc_id, labels in gt_answers.iteritems():
        for lab in labels:
            if lab in label_indices:
                index = label_indices[lab]
                y_true[doc_id - min_docid][index] = True

    return y_true
