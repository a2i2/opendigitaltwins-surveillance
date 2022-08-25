#!/usr/bin/env python3

import sys
import json
import random
from heapq import heappush, heappop
from statistics import mean
from collections import defaultdict

class Network:
    # TODO: Improve efficiency by converting
    #       string identifiers to ints

    def __init__(self, network_json):
        self.nodes = network_json["nodes"]
        self.edges = network_json["edges"]
    
        # (from, to) -> edge dict
        self.edge_index = {}
        # from -> [edge]
        self.neighbours_index = defaultdict(set)

        for e in self.edges:
            a = e["from"]
            b = e["to"]
            # assume at most one edge from a to b
            assert (a, b) not in self.edge_index
            self.edge_index[(a, b)] = e
            self.neighbours_index[a].add(b)
    
    def get_edge(self, a, b):
        """Gets edge, including all attributes"""
        return self.edge_index[a, b]

    def get_edge_keys(self):
        return self.edge_index.keys()
        
    def neighbours(self, a):
        """Gets set of nodes with edge from a"""
        return self.neighbours_index[a]

    def get_nodes(self):
        """Gets list of nodes"""
        return self.nodes


class Perc:
    def __init__(self, network, rho, zs, budget):
        self.network = network
        self.rho = rho
        self.zs = zs
        self.budget = budget

    def q(self, a, b):
        e = self.network.get_edge(a, b)
        return e["level"]

    def m(self, a, b):
        e = self.network.get_edge(a, b)
        return e["priv"]

    def f(self, a, b):
        e = self.network.get_edge(a, b)
        return 1 - e["privAvail"]

    def f_access(self, a, b):
        e = self.network.get_edge(a, b)
        return 1 - e["levelAvail"]

    def f_mode(self, a, b):
        e = self.network.get_edge(a, b)
        return e["failMode"]

    def z(self, a, b):
        return self.zs[(a, b)]

    def b_od(self, o, d):
        # assume constant budget
        return self.budget

    def f_od(self, o, d):
        # assume equal flow demand between all o,d pairs
        return 1

    # this is the most important function to define (rest will follow)
    def c_ab(self, a, b):
        z0, z1 = self.z(a, b)
        access_permission = self.q(a, b) > self.rho
        access_failure = z0 < self.f_access(a, b)
        access_failure_mode = self.f_mode(a, b)
        sensor_failure = z1 < self.f(a, b)

        if access_failure_mode == "failclosed":
            has_access = access_permission and not access_failure
        else:
            has_access = access_permission or access_failure

        if has_access:
            if sensor_failure:
                return 0
            return self.m(a, b)

        return float("inf")

    def c_star_od(self, o, d, budget=float("inf")):
        # Apply Dijkstra's algorithm to find minimum cost path from o to d
        # TODO: Find more efficient implementation at scale (e.g. could use approximate solution)
        
        if budget <= 0:
            return None

        # Based on https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm#Using_a_priority_queue
        dist = {}
        q = []
        
        dist[o] = 0
        heappush(q, (0, o))
        
        while q:
            dist_u, u = heappop(q)
            
            if u == d:
                # We found the target node
                return dist_u

            if dist[u] < dist_u:
                # Have already visited this node before.
                # Is a stale entry with a greater tentative distance.
                continue

            for v in self.network.neighbours(u):
                # TODO: cache c_ab
                # (computed once per run of Dijkstra's alg)
                alt = dist_u + self.c_ab(u, v)
                if alt < dist.get(v, budget):
                    dist[v] = alt
                    # The old tentative distance (if any) will be left in
                    # the list, but will be ignored as a stale entry
                    # during processing loop.
                    heappush(q, (alt, v))
        
        # Target node not reachable (or has cost >= budget)
        return None

    def r_od(self, o, d):
        # Pass budget to c_star_od to allow terminating search early
        return 0 if self.c_star_od(o, d, self.b_od(o, d)) is None else 1

    def UD(self):
        flow_unaffected = 0
        flow_demand = 0
        for o in self.network.get_nodes():
            for d in self.network.get_nodes():
                flow_unaffected += self.f_od(o, d) * self.r_od(o, d)
                flow_demand += self.f_od(o, d)
        return flow_unaffected / flow_demand


def alpha(network, budget, integral_steps=4, rand_steps=1000):
    # Example of integral_steps=4
    # 0    0.25  0.5  0.75    1
    # V     V     V     V     V
    # [0.125,0.375,0.625,0.875]
    delta = 1/integral_steps
    integral = 0

    for step in range(integral_steps):
        rho = delta * step + delta/2
        UD_rho = []
        
        for _ in range(rand_steps):
            # Todo: use a seed for repeatability
            zs = {
              (i, j): [random.random(), random.random()]
              for (i, j) in network.get_edge_keys()
            }
            perc = Perc(network, rho, zs, budget)
            UD_rho.append(perc.UD())

        E_UD_rho = mean(UD_rho)
        integral += E_UD_rho * delta

    return integral


def percolation(network_json):
    network = Network(network_json)
    #budget = 10 # bits of entropy

    str = "budget, alpha\n"
    print("budget, alpha")
    results = {}
    for budget in range(0,16+1):
        a = alpha(network, budget)
        results[f"alpha_{budget}"] = a
        print(f"{budget:6d}, {a:.3f}")
        str += f"{budget:6d}, {a:.3f}\n"

    return results, str


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        raise("needs network as first argument")

    network_file = sys.argv[1]

    with open(network_file, 'r') as f:
        network_json = json.load(f)

    results, str = percolation(network_json)
    
    with open("budget-vs-alpha.csv", "w") as f:
        f.write(str)
    #print(json.dumps(results, indent=4))
