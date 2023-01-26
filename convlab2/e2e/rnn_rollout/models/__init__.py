# -*- coding: utf-8 -*-
# Copyright 2019-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.

from convlab2.e2e.rnn_rollout.models.latent_clustering_model import (
    BaselineClusteringModel,
    LatentClusteringLanguageModel,
    LatentClusteringModel,
    LatentClusteringPredictionModel,
)
from convlab2.e2e.rnn_rollout.models.rnn_model import RnnModel
from convlab2.e2e.rnn_rollout.models.selection_model import SelectionModel

MODELS = {
    "latent_clustering_model": LatentClusteringModel,
    "latent_clustering_prediction_model": LatentClusteringPredictionModel,
    "latent_clustering_language_model": LatentClusteringLanguageModel,
    "baseline_clustering_model": BaselineClusteringModel,
    "selection_model": SelectionModel,
    "rnn_model": RnnModel,
}


def get_model_names():
    return MODELS.keys()


def get_model_type(name):
    return MODELS[name]
