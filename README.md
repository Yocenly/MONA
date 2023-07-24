# MONA: An Efficient and Scalable Strategy for Targeted k-Nodes Collapse

## 1. Overview

We offer the descriptions of files or folders in this part.

- _caches_: Results of k-core decomposition for each dataset for avoiding duplicate computations.
- _datasets_: Used [datasets](https://drive.google.com/file/d/1wm37pjW418kZTL_E-2ecG_3StcFxCUZB/view?usp=drive_link) in
  our paper.
- _methods_: Proposed methods and used baselines, including **Optimal**, **MONA**, **Random**, **Degree**,
**COREATTACK**, **KC-Edge**.
- _interface_attack_: The interface to implement our methods.

## 2. Requirements

    numpy >= 1.20.3
    networkx >= 2.6.3

## 3. Abstract

The concept of k-core plays a significant role in measuring the cohesiveness and the engagement of a network. And
recent studies have shown the vulnerability of k-core under adversarial attacks. However, there are few researchers
concentrating on the vulnerability of individual nodes within k-core. Therefore, in this paper, we make the attempt to
study Targeted k-Nodes Collapse Problem (TNsCP), which focuses on removing a minimal-size set of edges to make target
k-nodes collapse. For this purpose, we first propose a novel algorithm named MOD for candidate reduction, and we further
propose an efficient strategy named MONA, based on MOD, to address TNsCP. The extensive experiments validate the
effectiveness and scalability of MONA compared with several baselines.

## 3. Run the code

To implement attack methods, we could run the following command.

> python interface_attack.py --dataset [dataset_name] --method [method_name] --b [b]

- [dataset_name]: Tested dataset, e.g., usair/deezereu/crawl.
- [method_name]: Tested method, e.g., optimal/mona/random.
- [b]: The number of target nodes, e.g., 2/4/6.