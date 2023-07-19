# -*- coding: utf-8 -*-
# @Time     : 2023/6/26 12:13
# @Author   : lv yuqian
# @File     : method_random.py
# @Desc     : None
import os
import time
import random
import numpy as np
import pickle as pkl
import networkx as nx
from tqdm import tqdm
from typing import Union
from methods.base_graph import BaseGraph


class Random(BaseGraph):
    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        super().__init__(graph, dataset_name)
        if os.path.exists(f"caches/{dataset_name}_core.pkl"):
            print(f"{dataset_name}存在已有的k核分解记录, 加载保存的分解结果")
            self.core_number = pkl.load(open(f"caches/{dataset_name}_core.pkl", 'rb'))
        else:
            print(f"{dataset_name}不存在已有的k核分解记录, 重新获取分解结果")
            self.core_number = self.decompose_core(self.graph)
            pkl.dump(self.core_number, open(f"caches/{dataset_name}_core.pkl", 'wb'))

    def attack_cluster(self, k: int, target_nodes: list, graph: nx.Graph, core_number: dict, repeat_num: int = 100):
        """
        :param target_node: 目标节点
        :return:
        """
        core = nx.k_core(graph, k, core_number)
        candidate_edges = [(u, v) for u, v in core.edges if min(core_number[u], core_number[v]) == k]
        print(f"当前目标节点集合为: {target_nodes}; 节点核数为: {k}; 候选连边数量为: {len(candidate_edges)}")
        # print(f"攻击前的CS值为: {self.update_core_strength(core, target_nodes, core_number)}")

        removed_edges = []
        for _ in tqdm(range(repeat_num)):
            _core_number = core_number.copy()
            core = nx.k_core(graph, k, _core_number)
            random.shuffle(candidate_edges)
            for removed_edge in candidate_edges:
                if removed_edge not in core.edges:
                    continue
                f, _ = self.maintain_deletion(core, [removed_edge], _core_number)
                core.remove_nodes_from(f)
                removed_edges.append(removed_edge)
                if len(set(target_nodes) & set(core.nodes)) == 0:
                    break

        return len(removed_edges) / repeat_num

    def attack(self, target_nodes: Union[int, list]):
        """
        相对于Optimal, Greedy将候选连边缩减为Backtrace Tree所包含的连边集合(可能还需要包含几条连边, 不过对整体规模的缩小是显著的)
        在后续的对最优连边组合的筛选过程, 与Optimal的过程保持一致
        :param target_nodes: 目标节点列表
        :return:
        """
        target_nodes = [target_nodes] if isinstance(target_nodes, int) else target_nodes
        graph, core_number, total_removed_edges = self.graph, self.core_number.copy(), []
        # 按照核数对目标节点进行分流, 对不同核数的节点依次进行攻击
        node_clusters = self.node_diversion(target_nodes, self.core_number)
        tick = time.process_time()
        for k, nodes in node_clusters.items():
            average_num = self.attack_cluster(k, nodes, graph, core_number)
            total_removed_edges.append(average_num)
        print(f"平均攻击消耗时间: {(time.process_time() - tick) / 100: .6f}")
        print(f"平均删除的连边数量为: {sum(total_removed_edges) / len(total_removed_edges)}\n")


if __name__ == '__main__':
    dataset = "deezereu"
    edges = pkl.load(open(f'../datasets/{dataset}.pkl', 'rb'))
    attacker = Random(edges)
    print(attacker.graph.number_of_nodes(), attacker.graph.number_of_edges(), max(attacker.core_number.values()))

    # for node in attacker.graph.nodes:
    #     attacker.attack([node])