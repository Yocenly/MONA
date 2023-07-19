# -*- coding: utf-8 -*-
# @Time     : 2023/6/27 20:35
# @Author   : lv yuqian
# @File     : interface_attack.py
# @Desc     : None
import json
import argparse
import pickle as pkl
import networkx as nx
from methods.optimal import Optimal
from methods.greedy import Greedy
from methods.mona import MONA
from methods.my_random import Random
from methods.degree import Degree


def arg_parse():
    parser = argparse.ArgumentParser(description='Get Target Nodes by CKC Algorithm')
    parser.add_argument('--dataset', type=str, default="wikipedia", help='Used Dataset')
    parser.add_argument('--method', type=str, default="random", help='Used Attack Method')
    parser.add_argument('--b', type=int, default=10, help='The Number of Selected Target Nodes')
    return parser.parse_args()


_METHODS_ = {
    "optimal": Optimal,
    "greedy": Greedy,
    "mona": MONA,
    "random": Random,
    "degree": Degree,
}


if __name__ == "__main__":
    args = arg_parse()
    edges = pkl.load(open(f"./datasets/{args.dataset}.pkl", "rb"))
    print(f"攻击方法为: {args.method}, 攻击的数据集为: {args.dataset}, 目标节点数量为: {args.b if args.b else 'ALL'}")
    print(f"正在加载数据集...")
    attacker = _METHODS_[args.method](edges, args.dataset)
    k_core = nx.k_core(attacker.graph, max(attacker.core_number.values()), attacker.core_number)
    print(f"数据集加载完成.")
    if args.b is None:
        targets = list(k_core.nodes)
    else:
        targets = json.load(open(f"caches/candidate_targets.json", 'r'))[args.dataset][:args.b]
    print(f"{args.dataset}数据集包含: {len(attacker.graph.nodes())}个节点; {len(attacker.graph.edges())}条连边; "
          f"平均度为{2 * len(attacker.graph.edges) / len(attacker.graph.nodes): .2f}; "
          f"最内核为{max(attacker.core_number.values())}核; "
          f"最内核包含{len(k_core.nodes)}个节点, {len(k_core.edges)}条连边")
    attacker.attack(targets)
