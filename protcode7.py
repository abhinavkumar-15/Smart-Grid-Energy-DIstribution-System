import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# ----------------- CONFIGURATION base ---------------
NUM_GENERATORS = 3
NUM_SUBSTATIONS = 6
NUM_CONSUMERS = 10
PHEROMONE_DECAY = 0.9

# -----------==-- GRID MAKiNG ----------
def create_grid():
    G = nx.DiGraph()

    generators = [f"G{i}" for i in range(NUM_GENERATORS)]
    substations = [f"S{i}" for i in range(NUM_SUBSTATIONS)]
    consumers = [f"C{i}" for i in range(NUM_CONSUMERS)]

    for g in generators:
        G.add_node(g, type="generator", capacity=random.randint(150, 300))

    for s in substations:
        G.add_node(s, type="substation")

    for c in consumers:
        G.add_node(c, type="consumer", priority=1)

    ''' 
    manual priorities if needed otherwise default value is 1
    higher number means higher priority
    '''
    
    G.nodes["C0"]["priority"] = 5
    G.nodes["C3"]["priority"] = 4
    G.nodes["C7"]["priority"] = 2

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

    return G, generators, substations, consumers

# --=======---------- WIDE LAYOUT ---------
def layered_layout(generators, substations, consumers):
    pos = {}

    g_space = 10
    s_space = 7
    c_space = 4

    g_offset = -(len(generators)-1)*g_space/2
    s_offset = -(len(substations)-1)*s_space/2
    c_offset = -(len(consumers)-1)*c_space/2

    for i,g in enumerate(generators):
        pos[g]=(g_offset+i*g_space,10)

    for i,s in enumerate(substations):
        pos[s]=(s_offset+i*s_space,5)

    for i,c in enumerate(consumers):
        pos[c]=(c_offset+i*c_space,0)

    return pos


#  SMART DISTRIBUTION DISTRIBUTION --------------------------
 
def distribute_energy(G, generators, consumers, demands):

    # step 1 calculate supply of generators and demand of consumers
    total_supply = sum(G.nodes[g]["capacity"] for g in generators)
    total_demand = sum(demands[c] for c in consumers) # list comprehension of demands 

   #step 2 decide allocation method/regime

    allocation = {}

    # first case 
    if total_supply >= total_demand:

        # Everyone gets full demand
        for c in consumers:
            allocation[c] = demands[c]

    # second case (i.e we re distribute based on priorities)
    else:

        weighted_sum = sum(demands[c] * G.nodes[c]["priority"] for c in consumers)

        for c in consumers:
            if weighted_sum == 0:
                allocation[c] = 0
            else:
                share = total_supply * (demands[c] * G.nodes[c]["priority"]) / weighted_sum
                allocation[c] = min(demands[c], int(share))

    # step 3 (reset flows)
    for u, v in G.edges():
        G[u][v]["flow"] = 0

    # step4 build max flow model (super sink )
    temp = G.copy()
    temp.add_node("SuperSource")
    temp.add_node("SuperSink")

    # Connect SuperSource => Generators
    for g in generators:
        temp.add_edge("SuperSource", g, capacity=G.nodes[g]["capacity"])

    # Connect Consumers => SuperSink with allocation
    for c in consumers:
        temp.add_edge(c, "SuperSink", capacity=allocation[c])

   #step 5 deciding routing 
    _, flow_dict = nx.maximum_flow(temp, "SuperSource", "SuperSink")

    # Apply flows back to real graph
    for u in flow_dict:
        for v in flow_dict[u]:
            if G.has_edge(u, v):
                G[u][v]["flow"] = flow_dict[u][v]

    return allocation

# ==== ==initialization ----
G, generators, substations, consumers = create_grid()
pos = layered_layout(generators, substations, consumers)

fig, ax = plt.subplots(figsize=(16,8))
t=0


# ------------ animation --------------
def animate(frame):
    global t
    ax.clear()
    t+=1

    demands = {c:random.randint(20,100) for c in consumers}
    alloc = distribute_energy(G,generators,consumers,demands)

    flows=[G[u][v]["flow"] for u,v in G.edges()]
    widths=[f/20+1 for f in flows]

    # nodes
    sizes=[]
    colors=[]
    for n in G.nodes():
        typ=G.nodes[n]["type"]
        if typ=="generator":
            sizes.append(1400); colors.append("red")
        elif typ=="substation":
            sizes.append(800); colors.append("orange")
        else:
            sizes.append(350); colors.append("skyblue")

    nx.draw(G,pos,ax=ax,width=widths,node_size=sizes,node_color=colors,with_labels=True)

    # attributes
    for n,(x,y) in pos.items():
        node=G.nodes[n]

        if node["type"]=="generator":
            txt=f"Cap:{node['capacity']}"

        elif node["type"]=="substation":
            incoming=sum(G[u][n]["flow"] for u in G.predecessors(n))
            outgoing=sum(G[n][v]["flow"] for v in G.successors(n))
            txt=f"\nIn:{incoming}\nOut:{outgoing}"

        else:
            incoming=sum(G[u][n]["flow"] for u in G.predecessors(n))
            txt=f"\nD:{demands[n]}\nS:{incoming}\nP:{node['priority']}"

        ax.text(x,y-1,txt,fontsize=8,ha="center")

    # telemetry
    total_supply=sum(G.nodes[g]["capacity"] for g in generators)
    total_demand=sum(demands.values())
    total_delivered=sum(G[u][v]["flow"] for u,v in G.edges() if v in consumers)
    sat=total_delivered/total_demand if total_demand else 0

    ax.set_title(f"Smart Grid Energy Distribution System\nTime:{t} Supply:{total_supply} Demand:{total_demand} Delivered:{total_delivered} Sat:{sat:.2f}")


ani=animation.FuncAnimation(fig,animate,frames=60,interval=1500)
plt.show()