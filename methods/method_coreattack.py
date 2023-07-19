# -*- coding: utf-8 -*-
# @Time     : 2023/7/4 15:23
# @Author   : lv yuqian
# @File     : method_coreattack.py
# @Desc     : None
import os
import time
import pickle as pkl
import networkx as nx
from typing import Union
from methods.base_graph import BaseGraph


class COREATTACK(BaseGraph):
    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        super().__init__(graph, dataset_name)
        if os.path.exists(f"caches/{dataset_name}_core.pkl"):
            print(f"{dataset_name}存在已有的k核分解记录, 加载保存的分解结果")
            self.core_number = pkl.load(open(f"caches/{dataset_name}_core.pkl", 'rb'))
        else:
            print(f"{dataset_name}不存在已有的k核分解记录, 重新获取分解结果")
            self.core_number = self.decompose_core(self.graph)
            pkl.dump(self.core_number, open(f"caches/{dataset_name}_core.pkl", 'wb'))

    def attack(self):
        """
        :return:
        """
        core_number, removed_edges = self.core_number.copy(), []
        # 按照核数对目标节点进行分流, 对不同核数的节点依次进行攻击
        tick = time.process_time()
        core = nx.k_core(self.graph, max(self.core_number.values()), core_number)
        while len(core.nodes()) > 0:
            followers = {edge: self.maintain_deletion(core, [edge], core_number, True)[0] for edge in core.edges()}
            removed_edge = max(followers.keys(), key=lambda x: len(followers[x]))
            f, _ = self.maintain_deletion(core, [removed_edge], core_number)
            core.remove_nodes_from(f)
            core.remove_edges_from([removed_edge])
            removed_edges.append(removed_edge)

        print(f"本次攻击消耗时间: {time.process_time() - tick: .6f}")
        print(f"总共删除的连边数量为: {len(removed_edges)}")


if __name__ == '__main__':
    dataset = "socfb"
    print(f"攻击方法为: COREATTACK, 攻击的数据集为: {dataset}")
    print(f"正在加载数据集...")
    edges = pkl.load(open(f'../datasets/{dataset}.pkl', 'rb'))
    attacker = COREATTACK(edges, dataset)
    print(f"数据集加载完成.")
    print(f"{dataset}数据集包含: {len(attacker.graph.nodes())}个节点; {len(attacker.graph.edges())}条连边")
    attacker.attack()
