#!/usr/bin/env python3

import sys
from twingraph import TwinGraph, dtId, list_get
import functools
import operator
import json


def extract(twin_json):
    prod = lambda xs: functools.reduce(operator.mul, xs)

    priv_total = lambda xs: sum([0] + xs)
    priv_avail_total = lambda xs: prod([1] + [x/100 for x in xs])
    accessLevelMap = {
        "visitor": 0.75,
        "staff": 0.5,
        "security": 0.25
    }
    level_total = lambda xs: min([1] + [accessLevelMap.get(x, 0) for x in xs])
    level_avail_total = lambda xs: prod([1] + [x/100 for x in xs])
    # default to failclosed unless at least one device specifies failopen
    level_fail_total = lambda xs: "failopen" if "failopen" in xs else "failclosed"

    tg = TwinGraph(twin_json)
    nodes = []
    for t in tg.twins("dtmi:digitaltwins:rec_3_3:core:Space;1"):
        nodes.append(dtId(t))
    
    edges = []
    edge_props = []
    for t in tg.twins("dtmi:digitaltwins:rec_3_3:asset:Door;1"):
        fr = tg.rel_targets("fromSpace", dtId(t), "dtmi:digitaltwins:rec_3_3:core:Space;1")
        to = tg.rel_targets("toSpace", dtId(t), "dtmi:digitaltwins:rec_3_3:core:Space;1") 
        su = tg.rel_targets("servedBy", dtId(t), "dtmi:au:edu:deakin:a2i2:SurveillanceAsset;1")
        priv = priv_total(list_get("privacyCost", su))
        priv_avail = priv_avail_total(list_get("availability", su))
        ac = tg.rel_targets("servedBy", dtId(t), "dtmi:au:edu:deakin:a2i2:AccessReader;1")
        level = level_total(list_get("accessLevel", ac))
        level_avail = level_avail_total(list_get("availability", ac))
        level_failmode = level_fail_total(list_get("failMode", ac))
        es = [
            {
                "from": dtId(i),
                "to": dtId(j),
                "priv": priv,
                "privAvail": priv_avail,
                "level": level,
                "levelAvail": level_avail,
                "failMode": level_failmode
            }
            for i in fr for j in to
        ]
        edges += es
        # Assume we can also exit through door (unless specified otherwise).
        # Assume that we don't need to prove access to exit via door
        if t.get("direction", "twoway") == "twoway":
            es_reverse = [
                {
                    "from": dtId(j),
                    "to": dtId(i),
                    "priv": priv,
                    "privAvail": priv_avail,
                    "level": 1,
                    "levelAvail": 1,
                    "failMode": level_failmode
                }
                for i in fr for j in to
            ]
            edges += es_reverse
    
    network = {
        "nodes": nodes,
        "edges": edges
    }
    return network


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        raise("needs twin as first argument")

    twin_file = sys.argv[1]
    with open(twin_file, 'r') as f:
        twin_json = json.load(f)

    network = extract(twin_json)
    print(json.dumps(network, indent=4))
