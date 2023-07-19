# -*- coding: utf-8 -*-
# @Time    : 2023/5/26 16:34
# @Author  : lv yuqian
# @File    : greedy.py
# @Email   : lvyuqian_email@163.com
import sys
sys.path.append("./")
sys.path.append("../")
sys.path.append("../../")
import os
import time
import pickle as pkl
import networkx as nx
from typing import Union
from methods.base_graph import BaseGraph
from itertools import combinations


class Optimal(BaseGraph):
    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        super().__init__(graph, dataset_name)
        if os.path.exists(f"caches/{dataset_name}_core.pkl"):
            print(f"{dataset_name}存在已有的k核分解记录, 加载保存的分解结果")
            self.core_number = pkl.load(open(f"caches/{dataset_name}_core.pkl", 'rb'))
        else:
            print(f"{dataset_name}不存在已有的k核分解记录, 重新获取分解结果")
            self.core_number = self.decompose_core(self.graph)
            pkl.dump(self.core_number, open(f"caches/{dataset_name}_core.pkl", 'wb'))

    def comb_effect(self, candidates: list, limit: int, core: nx.Graph, c: dict):
        """
        为了穷举每个可能的连边组合被删除后对节点核数的影响, 本函数用于生成一个迭代器
        返回当前组合数下, 每个连边组合被删除后产生的影响
        :param candidates: 候选连边列表
        :param limit: 组合数
        :param core: k核子图
        :param c: 节点核数
        :return: 一个迭代器, 每次迭代输出当前连边组合及其被删除后产生的影响
        """
        for comb in combinations(candidates, limit):
            yield comb, self.maintain_deletion(core, comb, c, test=True)[0]

    def enumerate_edges(self, targets: list, candidates: list, core: nx.Graph, c: dict, limit: int = 1):
        """
        针对一批目标节点, 通过穷举的方式选择使得所有目标节点核数发生改变的需要删除的最少连边
        :param targets: 目标节点列表
        :param candidates: 候选连边列表
        :param core: k核子图
        :param c: 节点核数
        :param limit: 组合数起始值
        :return:
        """
        while True:
            for removed_edges, followers in self.comb_effect(candidates, limit, core, c):
                if len(set(targets) - set(followers)) == 0:
                    return removed_edges, followers
            limit += 1

    def attack(self, target_nodes: Union[int, list]):
        """
        使用穷举法筛选能够使得所有目标节点核数发生改变的最优删边组合
        对于候选连边, 从组合数=1开始遍历所有的连边组合
        逐渐增加组合数, 直至找到那么一组连边组合, 删除这些连边可以使得所有目标节点的核数发生该百年
        :param target_nodes: 目标节点集合
        :return:
        """
        target_nodes = [target_nodes] if isinstance(target_nodes, int) else target_nodes
        graph, core_number, total_removed_edges = self.graph.copy(), self.core_number.copy(), []

        # 按照核数对目标节点进行分流, 对不同核数的节点依次进行攻击
        node_clusters = self.node_diversion(target_nodes, self.core_number)
        tick = time.process_time()
        for k, nodes in node_clusters.items():
            # 数据预处理, 获取目标k核及候选连边列表
            core = nx.k_core(graph, k, core_number)
            candidate_edges = [(u, v) for u, v in core.edges if min(core_number[u], core_number[v]) == k]
            print(f"当前的节点集合为: {nodes}; 节点核数为: {k}; 候选连边数量为: {len(candidate_edges)}")
            # print(f"攻击前的CS值为: {self.update_core_strength(core, nodes, core_number)}")

            # 使用穷举法筛选能够使得所有目标节点核数发生改变的最优删边组合
            removed_edges, followers = self.enumerate_edges(nodes, candidate_edges, core, core_number)
            total_removed_edges.extend(removed_edges)
            # 对筛选出来的删边组合进行验证
            self.maintain_deletion(graph, removed_edges, core_number)
            success_flag = [self.core_number[u] != core_number[u] for u in nodes]
            success_flag = "Success!" if sum(success_flag) == len(nodes) else "Defeat!"
            print(f"删除的连边为: {len(removed_edges)}, {removed_edges}")
            print(f"攻击后的核数为: {dict([(u, core_number[u]) for u in nodes])}; 攻击结果: {success_flag}")

        # pkl.dump(self.save_data, open(f"./visualization/optimal/{self.dataset_name}_cache.pkl", "wb"))
        print(f"本次攻击消耗时间: {time.process_time() - tick: .6f}")
        print(f"总共删除的连边数量为: {len(total_removed_edges)}, {total_removed_edges}\n")


if __name__ == '__main__':
    dataset = "tvshow"
    edges = pkl.load(open(f'../datasets/{dataset}.pkl', 'rb'))
    attacker = Optimal(edges, dataset)
    print(attacker.graph.number_of_nodes(), attacker.graph.number_of_edges(), max(attacker.core_number.values()))
    # import json
    # target_nodes = json.load(open(f"../caches/candidate_targets.json", 'r'))[dataset]
    # attacker.attack(target_nodes[:5])
    for node in attacker.graph.nodes:
        attacker.attack([node])
