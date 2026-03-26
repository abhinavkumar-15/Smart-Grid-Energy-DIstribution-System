import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# ---------------- CONFIG ----------------
NUM_GENERATORS = 3
NUM_SUBSTATIONS = 6
NUM_CONSUMERS = 10

FAILED_EDGES = {}  # {(u,v): remaining_time}


# ---------------- GRID ----------------
def create_grid():
    G = nx.DiGraph()

    generators = [f"G{i}" for i in range(NUM_GENERATORS)]
    substations = [f"S{i}" for i in range(NUM_SUBSTATIONS)]
    consumers = [f"C{i}" for i in range(NUM_CONSUMERS)]

    # generators
    for g in generators:
        G.add_node(g, type="generator", capacity=250)

    # substations
    for s in substations:
        G.add_node(s, type="substation")

    # consumers
    for c in consumers:
        G.add_node(c, type="consumer", priority=1)

    # manual priorities
    G.nodes["C0"]["priority"] = 5
    G.nodes["C3"]["priority"] = 4
    G.nodes["C7"]["priority"] = 2

    # connections
    for g in generators:
        for s in random.sample(substations, k=3):
            cap = random.randint(60, 120)
            G.add_edge(g, s, capacity=cap, base_capacity=cap, flow=0)

    for s in substations:
        others = [x for x in substations if x != s]
        for o in random.sample(others, k=2):
            cap = random.randint(40, 100)
            G.add_edge(s, o, capacity=cap, base_capacity=cap, flow=0)

    for c in consumers:
        for s in random.sample(substations, k=2):
            cap = random.randint(30, 90)
            G.add_edge(s, c, capacity=cap, base_capacity=cap, flow=0)

    return G, generators, substations, consumers


# ---------------- LAYOUT ----------------
def layered_layout(generators, substations, consumers):
    pos = {}

    g_space = 10
    g_offset = -(len(generators) - 1) * g_space / 2
    for i, g in enumerate(generators):
        pos[g] = (g_offset + i * g_space, 10)

    s_space = 7
    s_offset = -(len(substations) - 1) * s_space / 2
    for i, s in enumerate(substations):
        pos[s] = (s_offset + i * s_space, 5)


    c_space = 4
    c_offset = -(len(consumers) - 1) * c_space / 2
    for i, c in enumerate(consumers):
        pos[c] = (c_offset + i * c_space, 0)

    return pos


# ---------------- FAULT SYSTEM ----------------
def update_faults(G):
    global FAILED_EDGES

    to_restore = []

    for (u, v) in FAILED_EDGES:
        FAILED_EDGES[(u, v)] -= 1

        if FAILED_EDGES[(u, v)] <= 0:
            G[u][v]["capacity"] = G[u][v]["base_capacity"]
            to_restore.append((u, v))

    for e in to_restore:
        del FAILED_EDGES[e]


def inject_fault(G):
    global FAILED_EDGES

    for u, v in G.edges():

        #  Skip generator edges
        if G.nodes[u]["type"] == "generator":
            continue

        # (optional extra safety)
        if G.nodes[v]["type"] == "generator":
            continue

        # skip already failed edges
        if (u, v) in FAILED_EDGES:
            continue

        cap = G[u][v]["capacity"]
        flow = G[u][v]["flow"]

        if cap == 0:
            continue

        load_ratio = flow / cap if cap else 0

        # overload-based fault
        if load_ratio > 0.98 and random.random() < 0.1:
            fail_edge(G, u, v)

        # small random fault
        elif random.random() < 0.002:
            fail_edge(G, u, v)

def fail_edge(G, u, v):
    global FAILED_EDGES

    # find max priority of affected consumers
    affected_priority = 1

    if G.nodes[v]["type"] == "consumer":
        affected_priority = G.nodes[v]["priority"]

    # faster recovery for high priority
    base_time = random.randint(4,8)

    recovery_time = max(2, base_time - affected_priority)

    G[u][v]["capacity"] = 0
    FAILED_EDGES[(u,v)] = recovery_time


# ---------------- ENERGY DISTRIBUTION ----------------
def distribute_energy(G, generators, consumers, demands):

    total_supply = sum(G.nodes[g]["capacity"] for g in generators)
    total_demand = sum(demands.values())

    allocation = {}

    if total_supply >= total_demand:
        allocation = demands.copy()
    else:
        weighted_sum = sum(demands[c] * G.nodes[c]["priority"] for c in consumers)

        for c in consumers:
            share = total_supply * (demands[c] * G.nodes[c]["priority"]) / weighted_sum
            allocation[c] = min(demands[c], int(share))

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

    for u in flow_dict:
        for v in flow_dict[u]:
            if G.has_edge(u, v):
                G[u][v]["flow"] = flow_dict[u][v]

    return allocation


# ---------------- INIT ----------------
G, generators, substations, consumers = create_grid()
pos = layered_layout(generators, substations, consumers)

fig, ax = plt.subplots(figsize=(16, 8))
t = 0


# ---------------- ANIMATION ----------------
def animate(frame):
    global t
    ax.clear()
    t += 1

    # recover faults
    update_faults(G)

    # demand
    demands = {c: random.randint(30, 90) for c in consumers}

    # distribute energy
    distribute_energy(G, generators, consumers, demands)

    # inject faults AFTER flow
    inject_fault(G)

    # edge widths
    flows = [G[u][v]["flow"] for u, v in G.edges()]
    widths = [f / 20 + 1 for f in flows]

    # node styles
    sizes = []
    colors = []
    for n in G.nodes():
        typ = G.nodes[n]["type"]
        if typ == "generator":
            sizes.append(1400)
            colors.append("red")
        elif typ == "substation":
            sizes.append(800)
            colors.append("orange")
        else:
            sizes.append(350)
            colors.append("skyblue")

    nx.draw(G, pos, ax=ax, width=widths,
            node_size=sizes, node_color=colors, with_labels=True)

    # highlight failed edges
    if FAILED_EDGES:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=list(FAILED_EDGES.keys()),
            edge_color="red",
            width=3,
            ax=ax
        )

        edge_labels = {
            (u, v): f"{FAILED_EDGES[(u, v)]}"
            for (u, v) in FAILED_EDGES
        }

        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    # node attributes
    for n, (x, y) in pos.items():
        node = G.nodes[n]

        if node["type"] == "generator":
            txt = f"Cap:{node['capacity']}"

        elif node["type"] == "substation":
            incoming = sum(G[u][n]["flow"] for u in G.predecessors(n))
            outgoing = sum(G[n][v]["flow"] for v in G.successors(n))
            txt = f"\nIn:{incoming}\nOut:{outgoing}"

        else:
            incoming = sum(G[u][n]["flow"] for u in G.predecessors(n))
            txt = f"\nD:{demands[n]}\nS:{incoming}\nP:{node['priority']}"

        ax.text(x, y - 1, txt, fontsize=8, ha="center")

    # telemetry
    total_supply = sum(G.nodes[g]["capacity"] for g in generators)
    total_demand = sum(demands.values())
    total_delivered = sum(G[u][v]["flow"]
                          for u, v in G.edges() if v in consumers)

    satisfaction = total_delivered / total_demand if total_demand else 0

    ax.set_title(
        f"Adaptive Smart Grid with Fault Recovery\n"
        f"Time:{t} Supply:{total_supply} Demand:{total_demand} "
        f"Delivered:{total_delivered} Sat:{satisfaction:.2f}"
    )


ani = animation.FuncAnimation(fig, animate, frames=100, interval=1500)
plt.show()