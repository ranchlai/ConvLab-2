# -*- coding: utf-8 -*-
import os
import sys
import time

sys.path.append("../")
import json

import torch as th

from convlab2.policy.larl.multiwoz.experiments_woz.dialog_utils import (
    task_generate,
)
from convlab2.policy.larl.multiwoz.latent_dialog.agent_task import (
    OfflineRlAgent,
)
from convlab2.policy.larl.multiwoz.latent_dialog.corpora import (
    NormMultiWozCorpus,
)
from convlab2.policy.larl.multiwoz.latent_dialog.main import (
    OfflineTaskReinforce,
)
from convlab2.policy.larl.multiwoz.latent_dialog.models_task import (
    SysPerfectBD2Word,
)
from convlab2.policy.larl.multiwoz.latent_dialog.utils import Pack, set_seed


def main():

    start_time = time.strftime(
        "%Y-%m-%d-%H-%M-%S", time.localtime(time.time())
    )
    print("[START]", start_time, "=" * 30)

    env = "gpu"
    pretrained_folder = "2018-11-13-21-27-21-sys_sl_bdu2resp"
    pretrained_model_id = 61
    exp_dir = os.path.join(
        "sys_config_log_model", pretrained_folder, "rl-" + start_time
    )
    # create exp folder
    if not os.path.exists(exp_dir):
        os.mkdir(exp_dir)

    # RL configuration
    rl_config = Pack(
        train_path="../data/norm-multi-woz/train_dials.json",
        valid_path="../data/norm-multi-woz/val_dials.json",
        test_path="../data/norm-multi-woz/test_dials.json",
        sv_config_path=os.path.join(
            "sys_config_log_model", pretrained_folder, "config.json"
        ),
        sv_model_path=os.path.join(
            "sys_config_log_model",
            pretrained_folder,
            "{}-model".format(pretrained_model_id),
        ),
        rl_config_path=os.path.join(exp_dir, "rl_config.json"),
        rl_model_path=os.path.join(exp_dir, "rl_model"),
        ppl_best_model_path=os.path.join(exp_dir, "ppl_best.model"),
        reward_best_model_path=os.path.join(exp_dir, "reward_best.model"),
        record_path=exp_dir,
        record_freq=200,
        sv_train_freq=1000,  # TODO pay attention to main.py, cuz it is also controlled there
        use_gpu=env == "gpu",
        nepoch=10,
        nepisode=0,
        max_words=100,
        episode_repeat=1.0,
        temperature=1.0,
        rl_lr=0.01,
        momentum=0.0,
        nesterov=False,
        gamma=0.99,
        rl_clip=5.0,
        random_seed=10,
    )

    # save configuration
    with open(rl_config.rl_config_path, "w") as f:
        json.dump(rl_config, f, indent=4)

    # set random seed
    set_seed(rl_config.random_seed)

    # load previous supervised learning configuration and corpus
    sv_config = Pack(json.load(open(rl_config.sv_config_path)))

    sv_config["use_gpu"] = rl_config.use_gpu
    corpus = NormMultiWozCorpus(sv_config)

    # TARGET AGENT
    sys_model = SysPerfectBD2Word(corpus, sv_config)
    if sv_config.use_gpu:
        sys_model.cuda()
    sys_model.load_state_dict(
        th.load(
            rl_config.sv_model_path,
            map_location=lambda storage, location: storage,
        )
    )
    sys_model.eval()
    sys = OfflineRlAgent(
        sys_model, corpus, rl_config, name="System", tune_pi_only=False
    )

    # start RL
    reinforce = OfflineTaskReinforce(
        sys, corpus, sv_config, sys_model, rl_config, task_generate
    )
    reinforce.run()

    # save sys model
    th.save(sys_model.state_dict(), rl_config.rl_model_path)

    end_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
    print("[END]", end_time, "=" * 30)


if __name__ == "__main__":
    main()
