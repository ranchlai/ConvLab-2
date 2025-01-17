# -*- coding: utf-8 -*-
import pprint
import sys

sys.path.append("/root/NeuralDialog-LaRL")
import json
import logging
import os
import time

import torch
import torch as th
from numpy import array

import convlab2.policy.larl.multiwoz.latent_dialog.corpora as corpora
import convlab2.policy.larl.multiwoz.latent_dialog.domain as domain
from convlab2.policy.larl.multiwoz.experiments_woz.dialog_utils import (
    task_generate,
)
from convlab2.policy.larl.multiwoz.latent_dialog.corpora import EOS, PAD
from convlab2.policy.larl.multiwoz.latent_dialog.data_loaders import (
    BeliefDbDataLoaders,
)
from convlab2.policy.larl.multiwoz.latent_dialog.evaluators import (
    MultiWozEvaluator,
)
from convlab2.policy.larl.multiwoz.latent_dialog.main import train, validate
from convlab2.policy.larl.multiwoz.latent_dialog.models_task import (
    SysPerfectBD2Cat,
)
from convlab2.policy.larl.multiwoz.latent_dialog.utils import (
    Pack,
    prepare_dirs_loggers,
    set_seed,
)

domain_name = "object_division"
domain_info = domain.get_domain(domain_name)
config = Pack(
    seed=10,
    train_path="/root/NeuralDialog-LaRL/data/norm-multi-woz/train_dials.json",
    valid_path="/root/NeuralDialog-LaRL/data/norm-multi-woz/val_dials.json",
    test_path="/root/NeuralDialog-LaRL/data/norm-multi-woz/test_dials.json",
    max_vocab_size=1000,
    last_n_model=5,
    max_utt_len=50,
    max_dec_len=50,
    backward_size=2,
    batch_size=32,
    use_gpu=False,
    op="adam",
    init_lr=0.001,
    l2_norm=1e-05,
    momentum=0.0,
    grad_clip=5.0,
    dropout=0.5,
    max_epoch=100,
    embed_size=100,
    num_layers=1,
    utt_rnn_cell="gru",
    utt_cell_size=300,
    bi_utt_cell=True,
    enc_use_attn=True,
    dec_use_attn=True,
    dec_rnn_cell="lstm",
    dec_cell_size=300,
    dec_attn_mode="cat",
    y_size=10,
    k_size=20,
    beta=0.001,
    simple_posterior=True,
    contextual_posterior=True,
    use_mi=False,
    use_pr=True,
    use_diversity=False,
    #
    beam_size=20,
    fix_batch=True,
    fix_train_batch=False,
    avg_type="word",
    print_step=300,
    ckpt_step=1416,
    improve_threshold=0.996,
    patient_increase=2.0,
    save_model=True,
    early_stop=False,
    gen_type="greedy",
    preview_batch_num=None,
    k=domain_info.input_length(),
    init_range=0.1,
    pretrain_folder="2019-06-20-21-43-06-sl_cat",
    forward_only=False,
)
set_seed(config.seed)
start_time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))
stats_path = "sys_config_log_model"
if config.forward_only:
    saved_path = os.path.join(stats_path, config.pretrain_folder)
    config = Pack(json.load(open(os.path.join(saved_path, "config.json"))))
    config["forward_only"] = True
else:
    saved_path = os.path.join(
        stats_path, start_time + "-" + os.path.basename(__file__).split(".")[0]
    )
    if not os.path.exists(saved_path):
        os.makedirs(saved_path)
config.saved_path = saved_path

prepare_dirs_loggers(config)
logger = logging.getLogger()
logger.info("[START]\n{}\n{}".format(start_time, "=" * 30))
config.saved_path = saved_path

# save configuration
with open(os.path.join(saved_path, "config.json"), "w") as f:
    json.dump(config, f, indent=4)  # sort_keys=True

corpus = corpora.NormMultiWozCorpus(config)
train_dial, val_dial, test_dial = corpus.get_corpus()

train_data = BeliefDbDataLoaders("Train", train_dial, config)
val_data = BeliefDbDataLoaders("Val", val_dial, config)
test_data = BeliefDbDataLoaders("Test", test_dial, config)

evaluator = MultiWozEvaluator("SysWoz")

model = SysPerfectBD2Cat(corpus, config)

if config.use_gpu:
    model.cuda()


if config.use_gpu:
    model.load_state_dict(
        torch.load("/root/NeuralDialog-LaRL/larl_model/best-model")
    )
else:
    model.load_state_dict(
        torch.load(
            "/root/NeuralDialog-LaRL/larl_model/best-model",
            map_location=lambda storage, loc: storage,
        )
    )

data_feed = {
    "bs": array(
        [
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                1,
                1,
                0,
                0,
                1,
                0,
                0,
                1,
                0,
                0,
                1,
                0,
                0,
            ]
        ]
    ),
    "context_lens": array([2]),
    "outputs": array(
        [
            [
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                1,
                0,
                0,
                0,
                0,
                1,
                1,
                0,
                0,
                1,
                0,
                0,
                1,
                0,
                0,
                1,
                0,
                0,
            ]
        ]
    ),
    "contexts": array(
        [
            [
                [
                    4,
                    1,
                    6,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
                [
                    4,
                    1,
                    27,
                    16,
                    153,
                    40,
                    49,
                    8,
                    6,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                    0,
                ],
            ]
        ],
        dtype=int,
    ),
    "db": array(
        [
            [
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                1.0,
                0.0,
                1.0,
                0.0,
                1.0,
                0.0,
            ]
        ]
    ),
}
model.eval()
outputs, labels = model(
    data_feed,
    mode="gen",
    clf=False,
    gen_type="greedy",
    use_py=None,
    return_latent=False,
)

pprint.pprint(outputs)

import numpy as np

pred_labels = [t.cpu().data.numpy() for t in outputs["sequence"]]
pred_labels = (
    np.array(pred_labels, dtype=int).squeeze(-1).swapaxes(0, 1)
)  # (batch_size, max_dec_len)
true_labels = labels.data.numpy()  # (batch_size, output_seq_len)


def get_sent(vocab, de_tknize, data, b_id, stop_eos=True, stop_pad=True):
    ws = []
    for t_id in range(data.shape[1]):
        w = vocab[data[b_id, t_id]]
        # TODO EOT
        if (stop_eos and w == EOS) or (stop_pad and w == PAD):
            break
        if w != PAD:
            ws.append(w)

    return de_tknize(ws)


de_tknize = lambda x: " ".join(x)

for b_id in range(pred_labels.shape[0]):
    # only one val for pred_str now
    pred_str = get_sent(model.vocab, de_tknize, pred_labels, b_id)

print(pred_str)
