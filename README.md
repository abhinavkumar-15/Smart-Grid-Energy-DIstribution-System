# Smart Grid Energy Distribution System

## Overview

The Smart Grid Energy Distribution System is a graph-based simulation of an adaptive electrical power grid that dynamically distributes energy according to consumer demand, network conditions, and consumer priority levels.

Unlike traditional power grids that rely on static allocation mechanisms, this system continuously optimizes energy flow using graph algorithms, fault detection, automatic recovery mechanisms, and priority-aware load allocation.

The project models generators, substations, and consumers as nodes in a directed graph and uses maximum-flow optimization to maximize energy delivery while maintaining high consumer satisfaction.

---

## Key Features

### Dynamic Energy Distribution

* Real-time energy routing based on current demand.
* Adaptive allocation under changing network conditions.
* Efficient utilization of available generation capacity.

### Priority-Based Consumer Allocation

Consumers are assigned priority levels.

Examples:

* Priority 5 → Hospitals & Emergency Services
* Priority 4 → Industrial Facilities & Data Centers
* Priority 2 → Residential Hubs
* Priority 1 → Standard Consumers

During energy shortages, higher-priority consumers receive preferential allocation.

### Maximum Flow Optimization

The system transforms the grid into an augmented flow network and computes optimal energy routing using:

```python
networkx.maximum_flow()
```

This guarantees maximum possible energy delivery within network constraints.

### Fault Injection System

The simulation models real-world transmission failures through:

#### Load-Based Faults

Triggered when transmission lines operate above 98% capacity.

#### Random Faults

Represents:

* Equipment failure
* Environmental damage
* Unexpected outages

### Priority-Aware Recovery

Faulty transmission lines are automatically repaired.

Higher-priority consumers receive faster recovery times, improving resilience for critical infrastructure.

### Real-Time Visualization

The system provides:

* Live network visualization
* Energy flow tracking
* Fault highlighting
* Consumer demand monitoring
* Satisfaction metrics

---

## System Architecture

```text
Generators
     ↓
Substations
     ↓
Consumers
```

### Network Layers

#### Generation Layer

* 3 Generator Nodes
* Fixed generation capacity

#### Distribution Layer

* 6 Substation Nodes
* Interconnected for rerouting capability

#### Consumer Layer

* 10 Consumer Nodes
* Assigned priority levels

---

## Technologies Used

* Python
* NetworkX
* Matplotlib
* Graph Theory
* Maximum Flow Algorithms

---

## How It Works

### Step 1: Generate Demand

Consumer demand is generated dynamically for each simulation cycle.

### Step 2: Allocate Energy

Available energy is distributed according to:

* Total supply
* Total demand
* Consumer priority

### Step 3: Compute Maximum Flow

The grid is converted into an augmented flow network with:

* Super Source
* Super Sink

The maximum-flow algorithm determines optimal routing.

### Step 4: Inject Faults

Transmission failures are introduced based on:

* Network overload
* Random failure probability

### Step 5: Recover Faults

Failed transmission lines are restored after a recovery period.

### Step 6: Display Telemetry

The simulation reports:

* Supply
* Demand
* Delivered Energy
* Satisfaction Ratio
* Active Fault Count

---

## Simulation Metrics

The system continuously measures:

### Total Supply

Available generation capacity.

### Total Demand

Aggregate consumer energy requirements.

### Delivered Energy

Energy successfully routed to consumers.

### Consumer Satisfaction

```text
Satisfaction =
Delivered Energy / Total Demand
```

### Fault Statistics

Tracks:

* Active faults
* Recovery progress
* Grid resilience

---

## Experimental Results

### Case 1: Surplus Energy Scenario

| Metric                | Value     |
| --------------------- | --------- |
| Supply                | 750 Units |
| Average Demand        | 565 Units |
| Average Delivered     | 539 Units |
| Consumer Satisfaction | 95.6%     |

Results:

* Full satisfaction achieved multiple times.
* High resilience under fault conditions.
* Rapid fault recovery.

### Case 2: Energy Deficit Scenario

| Metric                | Value     |
| --------------------- | --------- |
| Supply                | 450 Units |
| Average Demand        | 572 Units |
| Average Delivered     | 328 Units |
| Consumer Satisfaction | 57%       |

Results:

* Priority allocation protected critical consumers.
* Grid remained operational despite shortages.
* Recovery mechanism maintained stability.

---

## Research Contribution

This project introduces:

1. Graph-Theoretic Smart Grid Modeling
2. Priority-Based Energy Allocation
3. Real-Time Maximum Flow Optimization
4. Dual-Mode Fault Injection
5. Priority-Aware Fault Recovery
6. Adaptive Smart Grid Simulation Framework

---

## Future Improvements

* Machine Learning based demand prediction
* Renewable energy integration
* Reinforcement Learning optimization
* Real-time IoT sensor integration
* Multi-grid interconnection support
* Smart city deployment simulation

---

## Research Paper

This project was developed as part of the research work:

**"Smart Grid Energy Distribution System"**

Authors:

* Dr. A. Swathi
* Pathi Abhinav Kumar
* Dacapelly Anjali
* Pilligundla Aarthi
* Mandala Sai Ram

The paper proposes a graph-based adaptive energy distribution framework with fault tolerance and priority-aware energy routing.

---

## License

This project is intended for academic and research purposes.
