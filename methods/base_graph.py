# -*- coding: utf-8 -*-
# @Time    : 2023/2/11 18:06
# @Author  : lv yuqian
# @File    : global_utils.py
# @Email   : lvyuqian_email@163.com
import pickle as pkl
import networkx as nx
from typing import Union
from methods.utils import CoreMaintenance


_FILTER_ = {
    '>': lambda v, u: v > u,
    '<': lambda v, u: v < u,
    '==': lambda v, u: v == u,
    '>=': lambda v, u: v >= u,
    '<=': lambda v, u: v <= u,
    '!=': lambda v, u: v != u,
}


class BaseGraph:
    def __init__(self, graph: Union[list, nx.Graph], dataset_name: str = None):
        self.graph = nx.Graph(graph)
        self.dataset_name = dataset_name

    @staticmethod
    def decompose_core(g: nx.Graph) -> dict:
        """
        k-core分解, 获取图中每个节点的核数
        :param g: 网络图
        :return:
        """
        return nx.core_number(g)

    @staticmethod
    def decompose_onion(g: nx.Graph) -> dict:
        """
        Onion分解, 获取每个节点在全图中的层级
        :param g: 网络图
        :return:
        """
        return nx.onion_layers(g)

    @classmethod
    def decompose_shale(cls, g: nx.Graph, k: int, c: dict) -> dict:
        """
        Modified-Onion分解, 获取每个节点在目标k核中所属的层级
        值得注意的是, MO算法与O算法的不同之处在于, O算法在每次循环中都会删除不符合条件的节点
        而MO算法则不会将所有不符合"条件"的节点一网打尽, 而是会进一步甄别它们之间的差异, 将"结构脆弱性"更强的节点先删除.
        :param g: 网络图
        :param k: 核数约束
        :param c: 节点核数
        :return:
        """
        core_nodes = [u for u in g.nodes if c[u] == k]
        core_nbrs = {u: cls.spt_nbrs(g, u, c, '==') for u in core_nodes}
        core_degrees = {u: len(cls.spt_nbrs(g, u, c)) for u in core_nodes}
        shale, shale_num = {}, 1
        while len(core_nodes) > 0:
            lower = [u for u in core_nodes if core_degrees[u] < k]
            step = True if len(lower) == 0 else False
            equal = [u for u in core_nodes if core_degrees[u] == k] if step else None
            for u in equal or lower:
                shale[u] = shale_num
                for v in core_nbrs[u]:
                    core_nbrs[v].remove(u)
                    core_degrees[v] -= 1
                core_nodes.remove(u)
                core_nbrs.pop(u)
            shale_num += 1

        return shale

    @staticmethod
    def node_diversion(nodes: Union[int, list], c: dict) -> dict:
        """
        将目标节点按照各自的核数进行分流, 使用字典存储各个核数的节点
        :param nodes: 目标节点列表
        :param c: 节点核数
        :return:
        """
        cores = sorted(set([c[n] for n in nodes]), reverse=True)
        return {k: [n for n in nodes if c[n] == k] for k in cores}

    @staticmethod
    def extract_coronas(core: nx.Graph, k: int) -> list:
        """
        提取k-core中的日冕节点
        :param core: k核子图
        :param k: 度值约束
        :return:
        """
        degrees = nx.degree(core)
        return [u for u in core.nodes if degrees[u] == k]

    @staticmethod
    def spt_nbrs(g: nx.Graph, u: int, c: dict, r: str = '>=') -> list:
        """
        寻找核值符合条件的邻居节点
        :param g: 网络图
        :param u: 目标节点
        :param c: 图中节点的核数
        :param r: 支撑邻居的筛选条件
        :return: 目标节点的支撑邻居列表
        """
        return [v for v in nx.neighbors(g, u) if _FILTER_[r](c[v], c[u])]

    @staticmethod
    def update_core_strength(g: nx.Graph, nodes: list, c: dict) -> dict:
        """
        计算节点的CoreStrength
        :param g: 网络图
        :param nodes: 目标节点列表
        :param c: 图中节点的核数
        :return: 目标节点的核强度
        """
        return {u: len(BaseGraph.spt_nbrs(g, u, c)) - c[u] + 1 for u in nodes}

    @staticmethod
    def maintain_deletion(g: nx.Graph, edges: list, c: dict, test: bool = False) -> tuple:
        """
        核维护函数, 具体实现方法详见utils.py中的CoreMaintenance类
        :param g: 网络图
        :param edges: 增/删的连边列表
        :param c: 图中节点的核数
        :param test: 是否为测试操作, True: 函数执行后会恢复增/删的连边及节点的核数; False: 不会恢复
        :return: 坍塌的节点列表, 受影响的节点列表
        """
        return CoreMaintenance.maintain_deletion(g, edges, c, test)


# if __name__ == '__main__':
#     edges = pkl.load(open(f'../datasets/deezereu.pkl', 'rb'))
#     base_graph = BaseGraph(edges)
#     core_number = base_graph.decompose_core(base_graph.graph)
#     k_max = max(core_number.values())
#     k = 8
#     k_core = nx.k_core(base_graph.graph, k, core_number)
#     onion = base_graph.decompose_onion(k_core)
#     shale = base_graph.decompose_shale(k_core, k, core_number)
#     print([u for u in onion.keys() if onion[u] == 1])
