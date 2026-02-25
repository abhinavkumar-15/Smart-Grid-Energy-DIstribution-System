import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# create realistic grid
#------------
def create_grid():

    G = nx.DiGraph()  # directed flow

    # Generator capacity
    G.add_node("Generator", capacity=200)

    # Substations with distribution limits
    G.add_node("S1", capacity=120)
    G.add_node("S2", capacity=100)

    # Consumers
    G.add_node("C1")
    G.add_node("C2")

    # Transmission lines
    edges = [
        ("Generator", "S1", 120),
        ("Generator", "S2", 100),
        ("S1", "C1", 80),
        ("S2", "C2", 70),
        ("S1", "S2", 50),
        ("S2", "S1", 50)
    ]

    for u, v, capacity in edges:
        G.add_edge(u, v, capacity=capacity, flow=0)

    return G


# distribute emerygy
# ---------------------------
def distribute_energy(G, demands):

    total_demand = sum(demands.values())
    generator_capacity = G.nodes["Generator"]["capacity"]

    # If demand exceeds supply : scale proportionally
    scaling_factor = min(1, generator_capacity / total_demand)

    adjusted_demands = {
        k: int(v * scaling_factor) for k, v in demands.items()
    }

    # Reset previous flows
    for u, v in G.edges():
        G[u][v]["flow"] = 0

    # Build super sink model
    temp = G.copy()
    temp.add_node("SuperSink")

    for consumer, demand in adjusted_demands.items():
        temp.add_edge(consumer, "SuperSink", capacity=demand)

    # Compute max flow
    flow_value, flow_dict = nx.maximum_flow(temp, "Generator", "SuperSink")

    # Apply flows to original graph
    for u in flow_dict:
        for v in flow_dict[u]:
            if G.has_edge(u, v):
                G[u][v]["flow"] = flow_dict[u][v]

    return adjusted_demands


# animation
#_----------------
G = create_grid()
pos = nx.spring_layout(G,k=1.5,iterations=100,seed=42)
fig, ax = plt.subplots()

time_step = 0


def animate(frame):
    global time_step
    ax.clear()
    time_step += 1

    # Random varying demand
    demands = {
        "C1": random.randint(50, 120),
        "C2": random.randint(40, 100)
    }

    adjusted = distribute_energy(G, demands)

    # Edge thickness proportional to flow
    flows = [G[u][v]["flow"] for u, v in G.edges()]
    widths = [flow / 10 + 1 for flow in flows]

    nx.draw(G, pos, with_labels=True, ax=ax, width=widths)

    edge_labels = {
        (u, v): f"{G[u][v]['flow']}/{G[u][v]['capacity']}"
        for u, v in G.edges()
    }

    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax)

    ax.set_title(
        f"Adaptive Energy Distribution\n"
        f"Time {time_step} | C1:{adjusted['C1']}MW C2:{adjusted['C2']}MW"
    )


ani = animation.FuncAnimation(fig, animate, frames=40, interval=5000)
plt.show()