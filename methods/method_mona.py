# -*- coding: utf-8 -*-
# @Time    : 2023/2/26 18:35
# @Author  : lv yuqian
# @File    : MONA.py
# @Email   : lvyuqian_email@163.com
import os
import time
import numpy as np
import pickle as pkl
import networkx as nx
import matplotlib.pyplot as plt
from typing import Union
from methods.base_graph import BaseGraph


class MONA(BaseGraph):
    """
        Class for Modified Onion based k-Node Attack
    """

    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        super().__init__(graph, dataset_name)
        if os.path.exists(f"caches/{dataset_name}_core.pkl"):
            print(f"{dataset_name}存在已有的k核分解记录, 加载保存的分解结果")
            self.core_number = pkl.load(open(f"caches/{dataset_name}_core.pkl", 'rb'))
        else:
            print(f"{dataset_name}不存在已有的k核分解记录, 重新获取分解结果")
            self.core_number = self.decompose_core(self.graph)
            # pkl.dump(self.core_number, open(f"caches/{dataset_name}_core.pkl", 'wb'))

    @staticmethod
    def branch_pruning(tree: nx.DiGraph, edges: list, anchors: list) -> list:
        """
        回溯树(Backtrace Tree)剪枝操作, 剪除一条连边后会使得多少节点脱离回溯树
        :param tree:
        :param edges:
        :param anchors:
        :return:
        """
        in_degrees, pruned_nodes = dict(tree.in_degree()), []
        for u, v in edges:
            if (u, v) not in tree.edges:
                continue
            in_degrees[v] -= 1
            if v not in anchors and in_degrees[v] <= 0:
                pruned_nodes.append(v)
                edges.extend(tree.edges(v))

        return pruned_nodes

    def node_backtrack(self, target_nodes: list, core: nx.Graph, shale: dict, core_number: dict) -> nx.DiGraph:
        """
        根据目标节点的MO值, 使用BFS算法回溯MO值小于目标节点的所有其他节点, 使用有向图对回溯结果进行存储
        :param target_nodes: 目标节点列表
        :param core: k核子图
        :param shale: 节点的MO值
        :param core_number: 节点核数
        :return:
        """
        # 初始化回溯树（有向图），初始化节点栈为目标节点列表，准备开启BFS
        tree, cached_nodes = nx.DiGraph(), target_nodes.copy()
        # 将原始目标节点添加进回溯树中
        tree.add_nodes_from(cached_nodes)
        # BFS搜索core中所有shale值小于父节点且核数与父节点相同的的子节点，用有向图对遍历结果进行储存
        for u in cached_nodes:
            eff_nodes = [v for v in self.spt_nbrs(core, u, core_number, '==') if shale[u] > shale[v]]
            cached_nodes.extend([v for v in eff_nodes if v not in tree.nodes])
            tree.add_edges_from([(u, v) for v in eff_nodes])

        pos = nx.drawing.nx_agraph.graphviz_layout(tree, prog='dot')
        nx.draw(tree, pos, with_labels=True)
        plt.show()

        return tree

    def cal_followers(self, core: nx.Graph, tree: nx.DiGraph, candidates: list, c: dict, anchors: list) -> dict:
        followers, tree_nodes = dict(), set(tree.nodes)
        for edge in set(candidates):
            if edge not in core.edges:
                continue
            maintain_followers = self.maintain_deletion(core, [edge], c, True)[0]
            pruning_followers = self.branch_pruning(tree, [edge], anchors)
            followers[edge] = (set(maintain_followers) | set(pruning_followers)) & tree_nodes
        return followers

    def attack_cluster(self, k: int, target_nodes: list, graph: nx.Graph, core_number: dict):
        """
        针对一批核数全为k的目标节点, 使用MO对候选连边进行筛选, 而后使用启发式方法选择当前最优的删除连边组合
        设计该方法的意图在于验证使用MO进行候选连边缩减的可行性
        :param k: 目标核数
        :param target_nodes: 目标节点列表
        :param graph: 网络图
        :param core_number: 节点核数
        :return:
        """
        # 提取目标k核子图, 计算核数为k的节点的MO值, 构建Backtrack Tree
        core = nx.k_core(graph, k, core_number)
        shale = self.decompose_shale(core, k, core_number)
        tree = self.node_backtrack(target_nodes, core, shale, core_number)
        # 单纯使用BT-tree中的连边在某些情况中是有欠缺的, 需要给每个目标节点额外补充一条连边加入候选连边
        # 额外选择的连边需要满足: 1. 改连边连接目标节点及另一个核数不小于目标节点的节点; 2. 该连边不存在于BT-tree中
        core.remove_edges_from(list(tree.edges))
        root_edges = list(nx.Graph([list(core.edges(u))[0] for u in target_nodes if len(core.edges(u)) > 0]).edges)
        candidate_edges = list(tree.edges) + root_edges
        core.add_edges_from(list(tree.edges))
        print(f"当前目标节点集合为: {target_nodes}; 节点核数为: {k}; 候选连边数量为: {len(candidate_edges)}")
        # print(f"攻击前的CS值为: {self.update_core_strength(core, target_nodes, core_number)}")
        print(f"攻击前的MO值为: {dict([(n, shale[n]) for n in target_nodes])}")

        # 使用启发式方法在候选连边列表中迭代式删除连边, 直至目标节点核数发生改变
        tree_nodes, removed_edges = set(tree.nodes), []
        while len(tree_nodes) > 0:
            # 遍历每条连边删除后所造成的影响, 影响主要包含两方面:
            #   1. 删除连边后直接牵连的核数改变的节点数量;
            #   2. 在BT tree中, 删除连边后可能会导致一部分"枝干"脱离"根", 这类"枝干"上的节点也认为是受影响节点
            followers = self.cal_followers(core, tree, candidate_edges, core_number, target_nodes)
            # print(len(candidate_edges), tree, list(tree.nodes), followers)
            # 对followers进行后处理, 便于下面排序选择待删除连边
            removed_edge = max(followers.keys(), key=lambda x: len(followers[x]))

            f, _ = self.maintain_deletion(core, [removed_edge], core_number, False)
            core.remove_nodes_from(f)
            tree_nodes -= set(followers[removed_edge])
            tree.remove_nodes_from(followers[removed_edge])
            tree.remove_edges_from([removed_edge])
            candidate_edges = list(tree.edges) + list([e for e in root_edges if e in core.edges])
            removed_edges.append(removed_edge)

        graph.remove_edges_from(removed_edges)
        success_flag = [self.core_number[node] != core_number[node] for node in target_nodes]
        success_flag = "Success!" if sum(success_flag) == len(target_nodes) else "Defeat!"
        print(f"删除的连边为: {len(removed_edges)}, {removed_edges}")
        print(f"攻击后的核数为: {dict([(u, core_number[u]) for u in target_nodes])}; 攻击结果: {success_flag}")

        return removed_edges

    def attack(self, target_nodes: Union[int, list]):
        """
        相对于Greedy, MONA方法保持了候选连边筛选阶段的一致性, 但是在后续对待删除连边删除的阶段
        MONA使用了启发式迭代删除方法, 可以大大降低时间复杂度, 但同时也会损失一定的准确性
        :param target_nodes: 目标节点列表
        :return:
        """
        target_nodes = [target_nodes] if isinstance(target_nodes, int) else target_nodes
        graph, core_number, total_removed_edges = self.graph, self.core_number.copy(), []
        # 按照核数对目标节点进行分流, 对不同核数的节点依次进行攻击
        node_clusters = self.node_diversion(target_nodes, self.core_number)
        tick = time.time()
        for k, targets in node_clusters.items():
            removed_edges = self.attack_cluster(k, targets, graph, core_number)
            total_removed_edges.extend(removed_edges)
        print(f"本次攻击消耗时间: {time.time() - tick: .6f}")
        print(f"总共删除的连边数量为: {len(total_removed_edges)}, {total_removed_edges}\n")


if __name__ == '__main__':
    dataset = "dolphin"
    edges = pkl.load(open(f'../datasets/{dataset}.pkl', 'rb'))
    attacker = MONA(edges, dataset)
    print(attacker.graph.number_of_nodes(), attacker.graph.number_of_edges(), max(attacker.core_number.values()))
    # k_core = nx.k_core(attacker.graph, max(attacker.core_number.values()), attacker.core_number)
    # nx.draw(k_core, with_labels=True)
    # plt.show()
    # mona.attack(list(k_core.nodes))
    # import json
    # target_nodes = json.load(open(f"../caches/candidate_targets.json", 'r'))[dataset]
    attacker.attack(28)
    # for node in attacker.graph.nodes:
    #     attacker.attack([node])
