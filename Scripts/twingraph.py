#!/usr/bin/env python3

import json
import sys
from collections import defaultdict

# DTDL v2 spec only allows inheritance depth of up to 10 levels,
# but our parser is capable of understanding infinite levels
#MAX_DEPTH = 10
MAX_DEPTH = float("inf")


def dtId(twin):
    return twin["$dtId"]


def list_get(prop, twins):
    """Gets prop from list of twins (if present)"""
    return [t[prop] for t in twins if prop in t]


def _coerce_list(x):
    if x is None:
        return []
    
    if type(x) == list:
        return x

    return [x]


class TwinGraph():
    def __init__(self, twin_json):
        """create twin graph from json"""
        twins = twin_json["digitalTwinsGraph"]["digitalTwins"]
        relationships = twin_json["digitalTwinsGraph"]["relationships"]
        models = twin_json["digitalTwinsModels"]

        # id -> twin
        self.twin_index = {}
        # (relname, sourceId) -> [rel]
        self.rel_index = defaultdict(list)
        # mod_id -> mod, {direct_extends_mod_id}
        self.mod_index = {}
        # mod_id -> {indirect_extends_mod_id}
        self.mod_is_a = {}

        for t in twins:
            self.twin_index[dtId(t)] = t
        
        for r in relationships:
            self.rel_index[(r["$relationshipName"], r["$sourceId"])].append(r)
        
        for m in models:
            exts = _coerce_list(m.get("extends"))
            self.mod_index[m["@id"]] = (m, exts)
            self.mod_is_a[m["@id"]] = {m["@id"]} | set(exts)
        
        # Iteratively propogate indirect extensions
        for m_id in self.mod_index:
            i = 0
            converged = False
            # do until no new extensions detected (or we exceed max depth)
            while i < MAX_DEPTH and not converged:
                i += 1
                old_exts = self.mod_is_a[m_id]
                new_exts = old_exts.copy()
                for e in old_exts:
                    _, e_exts = self.mod_index[e]
                    new_exts |= set(e_exts)
                self.mod_is_a[m_id] = new_exts
                converged = new_exts == old_exts

    @classmethod
    def from_file(cls, twin_file):
        with open(twin_file, 'r') as f:
            twin_json = json.load(f)

        return cls(twin_json)


    def is_a(self, twin, type):
        m = twin["$metadata"]["$model"]
        exts = self.mod_is_a[m]
        return type in exts

    def twin(self, id):
        """search for twin by id"""
        return self.twin_index[id]

    def twins(self, type):
        """search for twins by type (pass None to match any)"""
        ts = self.twin_index.values()
        
        if type is not None:
            ts = filter(lambda t: self.is_a(t, type), ts)
        
        return list(ts)

    def rel_targets(self, relName, sourceId, targetType):
        """return all twins of TargetType with a relName relationship from sourceId"""
        rs = self.rel_index[(relName, sourceId)] 
        ts = [self.twin(r["$targetId"]) for r in rs]
        ts = filter(lambda t: self.is_a(t, targetType), ts)
        return list(ts)


# Simple CLI for testing (load a file and print internal indexes)
if __name__ == "__main__":
    if not len(sys.argv) > 1:
        raise("needs twin as first argument")

    twin_file = sys.argv[1]

    tg = TwinGraph.from_file(twin_file)
    print("=== Twin Index ===")
    print(tg.twin_index)
    print("=== Rel Index ===")
    print(tg.rel_index)
    print("=== Mod Index ===")
    print(tg.mod_index)
    print("=== Mod is a Index ===")
    for k, v in tg.mod_is_a.items():
        print(f"{k} is a {sorted(v)}")

