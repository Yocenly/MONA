# -*- coding: utf-8 -*-
# @Time     : 2023/6/27 20:35
# @Author   : lv yuqian
# @File     : interface_attack.py
# @Desc     : None
import json
import argparse
import pickle as pkl
import networkx as nx
from methods.method_optimal import Optimal
from methods.method_mona import MONA
from methods.method_random import Random
from methods.method_degree import Degree
from methods.method_coreattack import COREATTACK
from methods.method_kcedge import KCEdge


def arg_parse():
    parser = argparse.ArgumentParser(description='Get Target Nodes by CKC Algorithm')
    parser.add_argument('--dataset', type=str, default="wikipedia", help='Used Dataset')
    parser.add_argument('--method', type=str, default="random", help='Used Attack Method')
    parser.add_argument('--b', type=int, default=10, help='The Number of Selected Target Nodes')
    return parser.parse_args()


_METHODS_ = {
    "optimal": Optimal,
    "mona": MONA,
    "random": Random,
    "degree": Degree,
    "coreattack": COREATTACK,
    "kcedge": KCEdge
}


if __name__ == "__main__":
    args = arg_parse()
    edges = pkl.load(open(f"./datasets/{args.dataset}.pkl", "rb"))
    print(f"攻击方法为: {args.method}, 攻击的数据集为: {args.dataset}, 目标节点数量为: {args.b}")
    print(f"正在加载数据集...")
    attacker = _METHODS_[args.method](edges, args.dataset)
    k_core = nx.k_core(attacker.graph, max(attacker.core_number.values()), attacker.core_number)
    print(f"数据集加载完成.\n"
          f"{args.dataset}数据集包含: {len(attacker.graph.nodes())}个节点; {len(attacker.graph.edges())}条连边; "
          f"平均度为{2 * len(attacker.graph.edges) / len(attacker.graph.nodes): .2f}; "
          f"最内核为{max(attacker.core_number.values())}核; "
          f"最内核包含{len(k_core.nodes)}个节点, {len(k_core.edges)}条连边")
    print(f"获取目标节点...")
    k = max(attacker.core_number.values())
    targets = [u for u in k_core.nodes if attacker.core_number[u] == k]
    targets = sorted(targets, key=lambda x: nx.degree(k_core, x))[:args.b]
    print(f"获取目标节点完成")
    attacker.attack(targets)
