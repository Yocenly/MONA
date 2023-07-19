# Project for MONA

We provide this project for the support of our paper "_MONA: An Efficient and Scalable Strategy 
for Targeted $k$-Nodes Collapse_".

In this project, we mainly offer the source code of our proposed methods, including **Optimal**, **MOD**,
**BacktrackTree**, **PruneEdge** and most important **MONA**. Besides, we also provide the realization of 
used baselines, such as **Random**, **Degree**.

We could implement our attack methods by the following command.

> python interface_attack.py --dataset [dataset_name] --method [method_name] --b [b]

where [dataset_name] represents the used dataset; [method_name] represents the used attack method 
(optimal/mona/random/degree).