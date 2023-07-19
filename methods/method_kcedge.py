# -*- coding: utf-8 -*-
# @Time     : 2023/7/4 15:24
# @Author   : lv yuqian
# @File     : method_kcedge.py
# @Desc     : None
import os
import time
import pickle as pkl
import networkx as nx
from typing import Union
from methods.base_graph import BaseGraph


class KCEdge(BaseGraph):
    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        super().__init__(graph, dataset_name)
        if os.path.exists(f"caches/{dataset_name}_core.pkl"):
            print(f"{dataset_name}存在已有的k核分解记录, 加载保存的分解结果")
            self.core_number = pkl.load(open(f"caches/{dataset_name}_core.pkl", 'rb'))
        else:
            print(f"{dataset_name}不存在已有的k核分解记录, 重新获取分解结果")
            self.core_number = self.decompose_core(self.graph)
            pkl.dump(self.core_number, open(f"caches/{dataset_name}_core.pkl", 'wb'))

    def attack(self, p: int = 10):
        """
        :return:
        """
        graph, core_number, total_removed_edges = self.graph, self.core_number.copy(), []
        # 按照核数对目标节点进行分流, 对不同核数的节点依次进行攻击
        tick = time.process_time()
        core = nx.k_core(graph, max(self.core_number.values()), core_number)
        while len(total_removed_edges) < p and len(core.nodes()) > 0:
            followers = {edge: self.maintain_deletion(core, [edge], core_number, True)[0] for edge in core.edges()}
            removed_edge = max(followers.keys(), key=lambda x: len(followers[x]))
            f, _ = self.maintain_deletion(core, [removed_edge], core_number)
            core.remove_nodes_from(f)
            total_removed_edges.append(removed_edge)

        print(f"本次攻击消耗时间: {time.process_time() - tick: .6f}")
        print(f"总共删除的连边数量为: {len(total_removed_edges)}")
        f, _ = self.maintain_deletion(graph, total_removed_edges, self.core_number)
        print(f"跟随节点的数量为: {len(f)}")


if __name__ == '__main__':
    edges = pkl.load(open(f'../datasets/socfb.pkl', 'rb'))
    attacker = KCEdge(edges, "socfb")
    print(attacker.graph.number_of_nodes(), attacker.graph.number_of_edges(), max(attacker.core_number.values()))
    attacker.attack()
    # for node in attacker.graph.nodes:
    #     attacker.attack([node])