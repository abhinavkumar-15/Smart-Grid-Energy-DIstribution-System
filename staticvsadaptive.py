import networkx as nx
import random
import time
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
NUM_GENERATORS = 3
NUM_SUBSTATIONS = 6
NUM_CONSUMERS = 10
TIME_STEPS = 100


# ---------------- GRID ----------------
def create_grid():
    G = nx.DiGraph()

    generators = [f"G{i}" for i in range(NUM_GENERATORS)]
    substations = [f"S{i}" for i in range(NUM_SUBSTATIONS)]
    consumers = [f"C{i}" for i in range(NUM_CONSUMERS)]

    for g in generators:
        G.add_node(g, type="generator", capacity=250)

    for s in substations:
        G.add_node(s, type="substation")

    for c in consumers:
        G.add_node(c, type="consumer", priority=random.randint(1,5))

    # connections
    for g in generators:
        for s in random.sample(substations, k=3):
            G.add_edge(g, s, capacity=random.randint(60, 120), flow=0)

    for s in substations:
        others = [x for x in substations if x != s]
        for o in random.sample(others, k=2):
            G.add_edge(s, o, capacity=random.randint(40, 100), flow=0)

    for c in consumers:
        for s in random.sample(substations, k=2):
            G.add_edge(s, c, capacity=random.randint(30, 90), flow=0)

    return G, generators, consumers


# ---------------- STATIC ----------------
def static_distribution(G, generators, consumers, demands):

    total_supply = sum(G.nodes[g]["capacity"] for g in generators)

    # equal split (no intelligence)
    per_consumer = total_supply // len(consumers)

    allocation = {}
    for c in consumers:
        allocation[c] = min(demands[c], per_consumer)

    return run_flow(G, generators, consumers, allocation)


# ---------------- ADAPTIVE ----------------
def adaptive_distribution(G, generators, consumers, demands):

    total_supply = sum(G.nodes[g]["capacity"] for g in generators)
    total_demand = sum(demands.values())

    allocation = {}

    if total_supply >= total_demand:
        allocation = demands.copy()
    else:
        weighted_sum = sum(demands[c]*G.nodes[c]["priority"] for c in consumers)

        for c in consumers:
            share = total_supply * (demands[c]*G.nodes[c]["priority"]) / weighted_sum
            allocation[c] = min(demands[c], int(share))

    return run_flow(G, generators, consumers, allocation)


# ---------------- FLOW ENGINE ----------------
def run_flow(G, generators, consumers, allocation):

    # reset flows
    for u, v in G.edges():
        G[u][v]["flow"] = 0

    temp = G.copy()
    temp.add_node("SuperSource")
    temp.add_node("SuperSink")

    for g in generators:
        temp.add_edge("SuperSource", g, capacity=G.nodes[g]["capacity"])

    for c in consumers:
        temp.add_edge(c, "SuperSink", capacity=allocation[c])

    _, flow_dict = nx.maximum_flow(temp, "SuperSource", "SuperSink")

    # apply flows
    for u in flow_dict:
        for v in flow_dict[u]:
            if G.has_edge(u, v):
                G[u][v]["flow"] = flow_dict[u][v]

    # compute delivered per consumer
    delivered = {}
    for c in consumers:
        delivered[c] = sum(G[u][c]["flow"] for u in G.predecessors(c))

    return delivered


# ---------------- METRICS ----------------
def compute_metrics(G, generators, consumers, demands, delivered):

    total_demand = sum(demands.values())
    total_delivered = sum(delivered.values())

    # ✅ FIXED efficiency (demand-based)
    efficiency = total_delivered / total_demand if total_demand else 0

    # ⭐ priority-weighted efficiency
    weighted_eff = sum(
        delivered[c] * G.nodes[c]["priority"]
        for c in consumers
    ) / sum(
        demands[c] * G.nodes[c]["priority"]
        for c in consumers
    )

    # congestion (real overload)
    overload = sum(
        1 for u, v in G.edges()
        if G[u][v]["capacity"] > 0 and
        G[u][v]["flow"] / G[u][v]["capacity"] > 0.9
    )

    return efficiency, weighted_eff, overload


# ---------------- SIMULATION ----------------
eff_static, eff_adaptive = [], []
weff_static, weff_adaptive = [], []
over_static, over_adaptive = [], []
resp_static, resp_adaptive = [], []

# same grid
G_base, generators, consumers = create_grid()

for _ in range(TIME_STEPS):

    G1 = G_base.copy()
    G2 = G_base.copy()

    # force realistic stress
    demands = {c: random.randint(80,150) for c in consumers}

    # STATIC
    start = time.time()
    delivered_static = static_distribution(G1, generators, consumers, demands)
    resp_static.append(time.time() - start)

    eff, weff, over = compute_metrics(G1, generators, consumers, demands, delivered_static)
    eff_static.append(eff)
    weff_static.append(weff)
    over_static.append(over)

    # ADAPTIVE
    start = time.time()
    delivered_adaptive = adaptive_distribution(G2, generators, consumers, demands)
    resp_adaptive.append(time.time() - start)

    eff, weff, over = compute_metrics(G2, generators, consumers, demands, delivered_adaptive)
    eff_adaptive.append(eff)
    weff_adaptive.append(weff)
    over_adaptive.append(over)


# ---------------- RESULTS ----------------
print("\n===== RESULTS =====")
print("Avg Efficiency Static:", sum(eff_static)/len(eff_static))
print("Avg Efficiency Adaptive:", sum(eff_adaptive)/len(eff_adaptive))

print("Avg Weighted Efficiency Static:", sum(weff_static)/len(weff_static))
print("Avg Weighted Efficiency Adaptive:", sum(weff_adaptive)/len(weff_adaptive))

print("Avg Overload Static:", sum(over_static)/len(over_static))
print("Avg Overload Adaptive:", sum(over_adaptive)/len(over_adaptive))


# ---------------- PLOTS ----------------
plt.figure(figsize=(12,10))

plt.subplot(4,1,1)
plt.plot(eff_static, label="Static")
plt.plot(eff_adaptive, label="Adaptive")
plt.title("Efficiency (Demand Satisfaction)")
plt.legend()

plt.subplot(4,1,2)
plt.plot(weff_static, label="Static")
plt.plot(weff_adaptive, label="Adaptive")
plt.title("Priority Weighted Efficiency")
plt.legend()

plt.subplot(4,1,3)
plt.plot(over_static, label="Static")
plt.plot(over_adaptive, label="Adaptive")
plt.title("Overload Frequency")
plt.legend()

plt.subplot(4,1,4)
plt.plot(resp_static, label="Static")
plt.plot(resp_adaptive, label="Adaptive")
plt.title("Response Time")
plt.legend()

plt.tight_layout()
plt.show()