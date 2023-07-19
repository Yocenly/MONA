# -*- coding: utf-8 -*-
# @Time     : 2023/6/26 13:56
# @Author   : lv yuqian
# @File     : method_degree.py
# @Desc     : None
import os
import time
import pickle as pkl
import networkx as nx
from typing import Union
from methods.base_graph import BaseGraph


class Degree(BaseGraph):
    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        super().__init__(graph, dataset_name)
        if os.path.exists(f"caches/{dataset_name}_core.pkl"):
            print(f"{dataset_name}存在已有的k核分解记录, 加载保存的分解结果")
            self.core_number = pkl.load(open(f"caches/{dataset_name}_core.pkl", 'rb'))
        else:
            print(f"{dataset_name}不存在已有的k核分解记录, 重新获取分解结果")
            self.core_number = self.decompose_core(self.graph)
            pkl.dump(self.core_number, open(f"caches/{dataset_name}_core.pkl", 'wb'))

    def attack_cluster(self, k: int, target_nodes: list, graph: nx.Graph, core_number: dict):
        """
        :param k: 目标核数
        :param target_nodes: 目标节点列表
        :param graph: 网络图
        :param core_number: 节点核数
        :return:
        """
        # 提取目标k核子图, 计算核数为k的节点的MO值, 构建Backtrack Tree
        core = nx.k_core(graph, k, core_number)
        candidate_edges = [(u, v) for u, v in core.edges if min(core_number[u], core_number[v]) == k]
        print(f"当前目标节点集合为: {target_nodes}; 节点核数为: {k}; 候选连边数量为: {len(candidate_edges)}")

        removed_edges = []
        for removed_edge in candidate_edges:
            if removed_edge not in core.edges:
                continue
            f, _ = self.maintain_deletion(core, [removed_edge], core_number)
            core.remove_nodes_from(f)
            removed_edges.append(removed_edge)
            if len(set(target_nodes) & set(core.nodes)) == 0:
                break

        graph.remove_edges_from(removed_edges)
        success_flag = [self.core_number[node] != core_number[node] for node in target_nodes]
        success_flag = "Success!" if sum(success_flag) == len(target_nodes) else "Defeat!"
        print(f"删除的连边为: {len(removed_edges)}, {removed_edges}")
        print(f"攻击后的核数为: {dict([(u, core_number[u]) for u in target_nodes])}; 攻击结果: {success_flag}")

        return removed_edges

    def attack(self, target_nodes: Union[int, list]):
        """
        :param target_node: 目标节点
        :return:
        """
        target_nodes = [target_nodes] if isinstance(target_nodes, int) else target_nodes
        graph, core_number, total_removed_edges = self.graph, self.core_number.copy(), []
        # 按照核数对目标节点进行分流, 对不同核数的节点依次进行攻击
        node_clusters = self.node_diversion(target_nodes, self.core_number)
        tick = time.process_time()
        for k, nodes in node_clusters.items():
            removed_edges = self.attack_cluster(k, nodes, graph, core_number)
            total_removed_edges.extend(removed_edges)
        print(f"本次攻击消耗时间: {time.process_time() - tick: .6f}")
        print(f"总共删除的连边数量为: {len(total_removed_edges)}")


if __name__ == '__main__':
    edges = pkl.load(open(f'../datasets/deezereu.pkl', 'rb'))
    attacker = Degree(edges)
    print(attacker.graph.number_of_nodes(), attacker.graph.number_of_edges(), max(attacker.core_number.values()))
    for node in [4142, 12346, 24122, 9252, 1622]:
        attacker.attack(node)
    # for node in attacker.graph.nodes:
    #     attacker.attack([node])
