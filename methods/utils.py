# -*- coding: utf-8 -*-
# @Time    : 2023/2/21 13:07
# @Author  : lv yuqian
# @File    : utils.py
# @Email   : lvyuqian_email@163.com
import time
import random
import numpy as np
import networkx as nx
# from numba import jit
from typing import Union


class CoreMaintenance:
    """
    该方法类存放Core Maintenance相关的函数, 主要是增/删连边后更新节点核数的函数
    """

    @classmethod
    def _deletion_search(cls, root: list, graph: nx.Graph, core_number: dict, delta_number: dict) -> list:
        victims = []
        while len(root) > 0:
            u = root.pop(0)
            victims.append(u)
            supporters = [v for v in nx.neighbors(graph, u) if core_number[v] >= core_number[u]]
            if len(supporters) < core_number[u]:
                root.extend([v for v in supporters if core_number[v] == core_number[u] and v not in root])
                delta_number[u] = delta_number.get(u, 0) + 1
                core_number[u] -= 1

        return victims

    @classmethod
    def maintain_deletion(cls, graph: nx.Graph, edges: list, core_number: dict, is_test: bool = False) -> tuple:
        victims, delta_number = [], {}
        for u, v in edges:
            # 这里使用nx.Graph.remove_edge可以同时验证连边(u, v)是否存在于graph中
            # 若连边(u, v)不存在, 我们不希望对这种情况进行处理, 函数执行到这里会直接抛出异常
            # 因此, 使用删边核维护函数时需要确保待删除的连边存在于graph中
            graph.remove_edge(u, v)
            if core_number[u] != core_number[v]:
                root = u if core_number[u] < core_number[v] else v
                _victims = cls._deletion_search([root], graph, core_number, delta_number)
            else:
                _victims = cls._deletion_search([u, v], graph, core_number, delta_number)
            victims.extend(_victims)
        if is_test:
            graph.add_edges_from(edges)
            core_number.update({u: core_number[u] + val for u, val in delta_number.items()})

        return list(delta_number.keys()), list(set(victims))

    @staticmethod
    def _addition_search(root: Union[int, list], graph: nx.Graph, core_number: dict):
        raise ValueError('This function is not completed yet.')
        pass

    @classmethod
    def maintain_addition(cls, graph: nx.Graph, edges: list, core_number: dict = None, is_test: bool = True):
        raise ValueError('This function is not completed yet.')
        pass

    @staticmethod
    def _test_maintenance_del_no_recover():
        """
        本函数为功能测试函数, 用来测试无恢复的k核删边维护算法的可行性
        :return:
        """
        for _ in range(1000):
            test_graph = nx.random_graphs.erdos_renyi_graph(5000, 0.01)
            core_number = nx.core_number(test_graph)
            print(f"无恢复测试{_}, 节点数: {len(test_graph.nodes)}, 连边数: {len(test_graph.edges)}")
            deleted_edges = random.sample(test_graph.edges, 1000)
            ticks = time.process_time()
            CoreMaintenance.maintain_deletion(test_graph, deleted_edges, core_number, False)
            print(f"time1: {time.process_time() - ticks: .2f}", end="; ")

            ticks = time.process_time()
            test_graph.remove_edges_from(deleted_edges)
            _core_number = nx.core_number(test_graph)
            print(f"time2: {time.process_time() - ticks: .2f}", end="; ")
            validation = [0 if core_number[u] == _core_number[u] else 1 for u in test_graph.nodes]
            print(f"不一致点的数量: {sum(validation)}")

    @staticmethod
    def _test_maintenance_del_recover():
        """
        本函数为功能测试函数, 用来测试带恢复的k核删边维护算法的可行性
        :return:
        """
        for _ in range(1000):
            test_graph = nx.random_graphs.erdos_renyi_graph(5000, 0.01)
            core_number = nx.core_number(test_graph)
            print(f"有恢复测试{_}, 节点数: {len(test_graph.nodes)}, 连边数: {len(test_graph.edges)}")
            deleted_edges = random.sample(test_graph.edges, 1000)
            ticks = time.process_time()
            CoreMaintenance.maintain_deletion(test_graph, deleted_edges, core_number, True)
            print(f"time1: {time.process_time() - ticks: .2f}", end="; ")

            ticks = time.process_time()
            test_graph.add_edges_from(deleted_edges)
            _core_number = nx.core_number(test_graph)
            print(f"time2: {time.process_time() - ticks: .2f}", end="; ")
            validation = [0 if core_number[u] == _core_number[u] else 1 for u in test_graph.nodes]
            print(f"不一致点的数量: {sum(validation)}")


if __name__ == '__main__':
    # CoreMaintenance._test_maintenance_del_no_recover()
    CoreMaintenance._test_maintenance_del_recover()
