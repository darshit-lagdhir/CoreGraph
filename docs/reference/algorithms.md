# CoreGraph Mathematical Blueprint

This blueprint defines the formal mathematical derivations of the analytical algorithms within the CoreGraph engine.

## 1. Structural Importance (PageRank)

The platform evaluates the structural centrality of a package $u$ within the 3.88-million node Directed Acyclic Graph (DAG) utilizing the PageRank algorithm:

$$
\text{PR}(u) = \frac{1 - d}{N} + d \sum_{v \in B(u)} \frac{\text{PR}(v)}{L(v)}
$$

where:
- $d$ is the Damping Factor (typically strictly set to $0.85$ to emulate traversal probability).
- $N$ represents the total number of software packages currently mapped within the ecosystem.
- $B(u)$ represents the subset of network nodes that structurally depend on $u$.
- $L(v)$ defines the out-degree of node $v$ (its outward dependencies).

## 2. Topological Blast Radius

The Blast Radius is calculated through a reverse Breadth-First Search (BFS). Given a package $u$, the algorithm traverses upstream along the directed edges to identify all nodes $v$ that possess a path to $u$.

The time complexity of this topological traversal is tightly bounded to:

$$
O(V + E)
$$

where $V$ is the set of dependent packages and $E$ is the set of topological edges linking them. The algorithm guarantees absolute downstream impact measurement.

## 3. Composite Vulnerability Index (CVI)

The platform fuses standard metrics into a unified floating-point index. The risk scalar derivation is weighted according to strictly defined tuning parameters:

$$
\text{CVI} = (S_{human} \times W_{human}) + (S_{economic} \times W_{economic}) + (S_{structural} \times W_{structural})
$$

where $W_{human}$, $W_{economic}$, and $W_{structural}$ sum to exactly $1.0$, defining the proportion of relative risk assigned to active maintenance deficit, funding deficit, and PageRank weight, respectively.
