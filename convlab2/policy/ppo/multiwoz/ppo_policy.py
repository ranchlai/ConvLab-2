# -*- coding: utf-8 -*-
import json
import os

from convlab2.policy.ppo import PPO


class PPOPolicy(PPO):
    def __init__(
        self,
        is_train=False,
        dataset="Multiwoz",
        archive_file="",
        model_file="https://huggingface.co/ConvLab/ConvLab-2_models/resolve/main/ppo_policy_multiwoz.zip",
    ):
        super().__init__(is_train=is_train, dataset=dataset)
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "config.json"
            ),
            "r",
        ) as f:
            cfg = json.load(f)
        self.load_from_pretrained(archive_file, model_file, cfg["load"])
