# MONA: An Efficient and Scalable Strategy for Targeted k-Nodes Collapse

## 1. Overview

We offer the introductions of files or folders in this part.

- _caches_: Results of k-core decomposition for each dataset on the considering of avoiding duplicate computations.
- _datasets_: Used datasets in our paper.
- _methods_: Proposed methods and used baselines, including **Optimal**, **MONA**, **Random**, **Degree**, **COREATTACK**, **KC-Edge**.
- _interface_attack_: The interface to implement our methods.

## 2. Requirements

    numpy >= 1.20.3
    networkx >= 2.6.3

## 3. Run the code

To implement attack methods, we could run the following command.

> python interface_attack.py --dataset [dataset_name] --method [method_name] --b [b]

- [dataset_name]: Tested dataset, e.g., usair/deezereu/crawl.
- [method_name]: Tested method, e.g., optimal/mona/random.
- [b]: The number of target nodes, e.g., 2/4/6.