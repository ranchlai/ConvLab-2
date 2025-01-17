# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 21:03:36 2020

@author: truthless
"""
import os
import zipfile

import torch

from convlab2.dialog_agent import Agent
from convlab2.e2e.damd.multiwoz.config import global_config as cfg
from convlab2.e2e.damd.multiwoz.damd_net import DAMD, cuda_, get_one_hot_input
from convlab2.e2e.damd.multiwoz.ontology import eos_tokens
from convlab2.e2e.damd.multiwoz.reader import MultiWozReader
from convlab2.util.file_util import cached_path

DEFAULT_DIRECTORY = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_ARCHIVE_FILE_URL = "https://huggingface.co/ConvLab/ConvLab-2_models/resolve/main/damd_multiwoz_data.zip"
DEFAULT_MODEL_URL = "https://huggingface.co/ConvLab/ConvLab-2_models/resolve/main/damd_multiwoz.zip"


class Damd(Agent):
    def __init__(self, model_file=DEFAULT_MODEL_URL, name="DAMD"):
        """
        Sequicity initialization

        Args:
            model_file (str):
                trained model path or url.
        Example:
            damd = Damd()
        """
        super(Damd, self).__init__(name=name)
        if not os.path.exists(
            os.path.join(DEFAULT_DIRECTORY, "multiwoz/data")
        ):
            print("down load data from", DEFAULT_ARCHIVE_FILE_URL)
            archive_file = cached_path(DEFAULT_ARCHIVE_FILE_URL)
            archive = zipfile.ZipFile(archive_file, "r")
            print("unzip to", os.path.join(DEFAULT_DIRECTORY, "multiwoz/"))
            archive.extractall(os.path.join(DEFAULT_DIRECTORY, "multiwoz/"))
            archive.close()
        model_path = os.path.join(
            os.path.join(DEFAULT_DIRECTORY, "multiwoz/"), cfg.eval_load_path
        )
        if not os.path.exists(model_path):
            model_dir = os.path.dirname(model_path)
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
            print("Load from model_file param")
            print("down load data from", model_file)
            archive_file = cached_path(model_file)
            archive = zipfile.ZipFile(archive_file, "r")
            print("unzip to", model_dir)
            archive.extractall(model_dir)
            archive.close()

        self.reader = MultiWozReader()
        self.m = DAMD(self.reader)
        if cfg.cuda and torch.cuda.is_available():
            self.m = self.m.cuda()  # cfg.cuda_device[0]

        if cfg.limit_bspn_vocab:
            self.reader.bspn_masks_tensor = {}
            for key, values in self.reader.bspn_masks.items():
                v_ = cuda_(torch.Tensor(values).long())
                self.reader.bspn_masks_tensor[key] = v_
        if cfg.limit_aspn_vocab:
            self.reader.aspn_masks_tensor = {}
            for key, values in self.reader.aspn_masks.items():
                v_ = cuda_(torch.Tensor(values).long())
                self.reader.aspn_masks_tensor[key] = v_

        cfg.model_path = os.path.join(model_path, "model.pkl")
        self.load_model(cfg.model_path)
        self.m.eval()

        self.init_session()

    def load_model(self, path=None):
        if not path:
            path = cfg.model_path
        all_state = torch.load(path, map_location="cpu")
        self.m.load_state_dict(all_state["lstd"])
        print("model loaded!")

    def add_torch_input(self, inputs, first_turn=False):
        need_onehot = [
            "user",
            "usdx",
            "bspn",
            "aspn",
            "pv_resp",
            "pv_bspn",
            "pv_aspn",
            "dspn",
            "pv_dspn",
            "bsdx",
            "pv_bsdx",
        ]
        if "db_np" in inputs:
            inputs["db"] = cuda_(torch.from_numpy(inputs["db_np"]).float())
        for item in ["user", "usdx"]:
            inputs[item] = cuda_(
                torch.from_numpy(inputs[item + "_unk_np"]).long()
            )
            if item in ["user", "usdx"]:
                inputs[item + "_nounk"] = cuda_(
                    torch.from_numpy(inputs[item + "_np"]).long()
                )
            else:
                inputs[item + "_nounk"] = inputs[item]
            if item in need_onehot:
                inputs[item + "_onehot"] = get_one_hot_input(
                    inputs[item + "_unk_np"]
                )

        for item in ["resp", "bspn", "aspn", "bsdx"]:
            if "pv_" + item + "_unk_np" not in inputs:
                continue
            inputs["pv_" + item] = cuda_(
                torch.from_numpy(inputs["pv_" + item + "_unk_np"]).long()
            )
            inputs["pv_" + item + "_nounk"] = inputs["pv_" + item]
            if "pv_" + item in need_onehot:
                inputs["pv_" + item + "_onehot"] = get_one_hot_input(
                    inputs["pv_" + item + "_unk_np"]
                )

        return inputs

    def init_session(self):
        """Reset the class variables to prepare for a new session."""
        self.hidden_states = {}
        self.reader.reset()

    def response(self, usr):
        """
        Generate agent response given user input.

        Args:
            observation (str):
                The input to the agent.
        Returns:
            response (str):
                The response generated by the agent.
        """

        u, u_delex = self.reader.preprocess_utterance(usr)
        # print('usr:', usr)

        inputs = self.reader.prepare_input_np(u, u_delex)

        first_turn = self.reader.first_turn
        inputs = self.add_torch_input(inputs, first_turn=first_turn)
        decoded = self.m(inputs, self.hidden_states, first_turn, mode="test")

        decode_fn = self.reader.vocab.sentence_decode
        resp_delex = decode_fn(
            decoded["resp"][0], eos=eos_tokens["resp"], indicate_oov=True
        )

        response = self.reader.restore(
            resp_delex, self.reader.turn_domain, self.reader.constraint_dict
        )
        # print('sys:', sys)

        self.reader.py_prev["pv_resp"] = decoded["resp"]
        if cfg.enable_bspn:
            self.reader.py_prev["pv_" + cfg.bspn_mode] = decoded[cfg.bspn_mode]
            # py_prev['pv_bspn'] = decoded['bspn']
        if cfg.enable_aspn:
            self.reader.py_prev["pv_aspn"] = decoded["aspn"]
        # torch.cuda.empty_cache()
        self.reader.first_turn = False

        return response.lower()


if __name__ == "__main__":
    s = Damd()
    print(s.response("I want to find a cheap restaurant"))
    print(s.response("ok, what is the address ?"))
