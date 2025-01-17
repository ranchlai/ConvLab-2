# LAUG
**LAUG**[[repo]](https://github.com/thu-coai/LAUG/) is an open-source toolkit for Language understanding AUGmentation. It is an automatic method to approximate the natural perturbations to existing data. Augmented data could be used to conduct black-box robustness testing or enhancing training. [[paper]](https://arxiv.org/abs/2012.15262)

Here are the 4 augmentation methods described in our paper.
- Word Perturbation, at `Word_Perturbation/` dir.
- Text Paraphrasing, at `Text_Paraphrasing/`dir.
- Speech Recognition, at `Speech_Recognition/`dir.
- Speech Disfluency, at `Speech_Disfluency/`dir.

Please see our paper and README.md in each augmentation method for detailed information.

See `demo.py` for the usage of these augmentation methods.
> python demo.py


Noting that our augmentation methods contains several neural models, pre-trained parameters need to be downloaded before use. Parameters pre-trained by us are available at [Link](http://115.182.62.174:9876/). For parameters which released by others, please follow the instructions of each method.
