import datetime
import uuid
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import (
    DemoUser, Subject, Topic, Document, DocumentContent,
    Question, QuestionRevision, SourceEvidence, QuestionTopic,
    QuestionSet, QuestionSetItem, Paper, PaperSection, PaperItem,
    Attempt, AttemptItem, Response, Notification, DemoSeedVersion
)

# ==============================================================================
# CURRICULUM TEXTS
# ==============================================================================

ITS_DOCUMENT_TEXT = """
INTELLIGENT TRANSPORT SYSTEMS (ITS-401)
COURSE LECTURE NOTES & SYLLABUS REFERENCE
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING

UNIT 1: INTRODUCTION TO INTELLIGENT TRANSPORT SYSTEMS
1.1 Fundamentals and Architecture of ITS
Intelligent Transport Systems (ITS) integrate advanced information, communication, electronics, and sensor technologies into transportation networks to enhance mobility, improve road safety, and minimize environmental impact. The national ITS architecture consists of physical, logical, and communication layers that interconnect traffic management centers, roadside field equipment, vehicles, and commuters.

1.2 Sensor Technologies and Traffic Surveillance
Traffic data collection utilizes both intrusive and non-intrusive sensors. Inductive loop detectors embedded beneath pavement detect magnetic field disruptions caused by metallic vehicle chassis, providing reliable vehicle counts, speed, and occupancy metrics. Non-intrusive sensors include pneumatic road tubes, microwave radars, infrared sensors, and computer vision closed-circuit television (CCTV) cameras. Video Image Processing Systems (VIPS) employ deep learning for automated incident detection and license plate recognition.

UNIT 2: ADVANCED TRAFFIC MANAGEMENT SYSTEMS (ATMS)
2.1 Real-Time Traffic Signal Optimization
Advanced Traffic Management Systems (ATMS) dynamically adjust traffic signal timings based on real-time saturation levels. SCATS (Sydney Coordinated Adaptive Traffic System) and SCOOT (Split Cycle Offset Optimisation Technique) continually calculate green splits, cycle lengths, and coordinate intersection offsets to minimize vehicular delay and stop frequencies across arterial corridors.

2.2 Incident Detection and Ramp Metering
Automated incident detection algorithms monitor flow fluctuations. Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate at which vehicles enter mainline highways, preventing freeway breakdown and shockwave propagation during peak demand periods. Variable Message Signs (VMS) disseminate real-time advisory alerts and lane closure warnings.

UNIT 3: ADVANCED TRAVELER INFORMATION SYSTEMS (ATIS)
3.1 Architecture of ATIS and Commuter Guidance
Advanced Traveler Information Systems (ATIS) deliver pre-trip and en-route travel information to road users. By processing historical traffic baselines alongside live crowdsourced probe GPS feeds, ATIS platforms provide dynamic route guidance, estimated times of arrival (ETA), and multimodal transit alternatives.

3.2 Electronic Toll Collection (ETC) and RFID
Automated Electronic Toll Collection systems, such as FASTag, leverage Radio Frequency Identification (RFID) operating in the passive UHF band (865-868 MHz). As an RFID-tagged vehicle crosses an electronic toll plaza at speed, overhead transceivers read tag IDs and automatically debit linked prepaid bank wallets, eliminating manual cash delays and reducing emissions.

UNIT 4: CONNECTED AND AUTONOMOUS VEHICLES (CAV)
4.1 V2X Communication Frameworks
Vehicle-to-Everything (V2X) communication encompasses Vehicle-to-Vehicle (V2V), Vehicle-to-Infrastructure (V2I), and Vehicle-to-Pedestrian (V2P) exchanges. Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters). Cellular-V2X (C-V2X) utilizes 4G LTE and 5G sidelink PC5 direct communication, providing longer range and greater bandwidth for sensor sharing.

4.2 Cooperative Adaptive Cruise Control and Platooning
Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion.
""".strip()

CS301_DOCUMENT_TEXT = """
DISTRIBUTED SYSTEMS & CLOUD COMPUTING (CS-301)
COURSE LECTURE NOTES & SYLLABUS REFERENCE
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING

UNIT 1: FOUNDATIONS OF DISTRIBUTED SYSTEMS & REMOTE PROCEDURE CALLS
1.1 System Models, Logical Clocks, and the CAP Theorem
A distributed system consists of autonomous nodes communicating over an asynchronous, unreliable network. Lamport logical clocks assign partial ordering to events, while Vector Clocks track causality across $n$ processes via vectors $V = [v_1, v_2, \dots, v_n]$. The CAP theorem proves that any networked shared-data system can simultaneously satisfy at most two of: Consistency (every read receives the most recent write), Availability (non-failing nodes always return non-error responses), and Partition Tolerance (system tolerates arbitrary network packet drops). Systems choose CP (e.g., Paxos/Raft) or AP (e.g., DynamoDB eventual consistency).

1.2 Remote Procedure Calls and Serialization
Remote Procedure Calls (RPC) abstract inter-process network communication into standard function invocations. Modern frameworks like gRPC utilize HTTP/2 transport framing with multiplexed bidirectional streaming and Protocol Buffers (protobuf) for binary schema compilation, offering significantly lower serialization overhead and wire latency compared to text-based JSON/REST interfaces.

UNIT 2: CONSENSUS PROTOCOLS & FAULT TOLERANCE
2.1 Paxos and Raft Consensus Algorithms
Replicated state machines maintain consistency across cluster nodes. While classical Paxos is mathematically complex, the Raft consensus algorithm decomposes consensus into Leader Election, Log Replication, and Safety. Raft guarantees that if a server applies a log entry at a given index to its state machine, no other server will ever apply a different log entry for that index, requiring a strict majority quorum $Q = \lfloor n/2 \rfloor + 1$.

2.2 Byzantine Fault Tolerance
Byzantine Fault Tolerance (BFT) addresses malicious, arbitrary, or compromised nodes. In a system with $f$ Byzantine adversarial nodes, classical consensus requires at least $3f + 1$ total nodes to reach guaranteed agreement (e.g., PBFT algorithm), because $f$ nodes may remain silent while $f$ other nodes send conflicting Byzantine messages.

UNIT 3: DISTRIBUTED STORAGE ARCHITECTURES
3.1 Consistent Hashing and Dynamo Design Patterns
Consistent hashing organizes server node identifiers and key hashes along a circular ring $0$ to $2^b - 1$. When nodes join or leave, only $\mathcal{O}(K/N)$ keys are remapped on average, avoiding catastrophic cluster data migration. Virtual nodes (v-nodes) ensure uniform load balancing across heterogeneous physical servers. Quorum replication follows the equation $R + W > N$ to guarantee strong read-your-writes consistency.

3.2 Log-Structured Merge Trees (LSM) and Spanner TrueTime
Log-Structured Merge (LSM) trees optimize write performance by buffering mutations in an in-memory MemTable before flushing them sequentially to immutable disk SSTables, performing background compaction. Google Spanner achieves globally distributed external consistency (strict serializability) using TrueTime APIs backed by atomic clocks and GPS receivers, bounding uncertainty intervals to $\epsilon \approx \pm 1\text{ ms}$.

UNIT 4: CLOUD VIRTUALIZATION & CONTAINER ORCHESTRATION
4.1 Hypervisors, Namespaces, and Cgroups
Type-1 (bare-metal) hypervisors (e.g., VMware ESXi, KVM) run directly on host hardware, whereas Type-2 hypervisors execute atop a host OS. Linux containerization utilizes kernel Namespaces (PID, Mount, Network, UTS, IPC) for resource isolation and Control Groups (cgroups v2) for CPU, memory, and I/O quota enforcement, providing microsecond startup times.

4.2 Kubernetes Architecture and Pod Scheduling
Kubernetes manages containerized workloads across node clusters. The control plane consists of kube-apiserver, kube-controller-manager, kube-scheduler, and an etcd distributed key-value store utilizing Raft consensus. The kube-scheduler filters nodes via predicates and scores matching nodes to allocate Pods optimizing cluster resource utilization.
""".strip()

AI402_DOCUMENT_TEXT = """
NATURAL LANGUAGE PROCESSING & LARGE LANGUAGE MODELS (AI-402)
COURSE LECTURE NOTES & SYLLABUS REFERENCE
DEPARTMENT OF ARTIFICIAL INTELLIGENCE & DATA SCIENCE

UNIT 1: FOUNDATIONS OF LANGUAGE REPRESENTATION & TOKENIZATION
1.1 Tokenization and Subword Algorithms
Modern NLP models operate on subword vocabularies to handle rare and out-of-vocabulary terms. Byte-Pair Encoding (BPE) iteratively merges the most frequent pairs of adjacent characters or character sequences until reaching a pre-set vocabulary size $V$ (typically 32,000 to 128,000 tokens). WordPiece and SentencePiece further optimize unigram language modeling tokenization without language-specific pre-tokenizers.

1.2 Static vs Contextual Word Embeddings
Word2Vec Skip-Gram predicts context words from a center target word maximizing log-probability $\sum \log P(w_{t+j} \mid w_t)$ using Negative Sampling loss. GloVe utilizes global word-word co-occurrence matrix factorization. These static embeddings map each word token to a fixed invariant vector in $\mathbb{R}^d$, failing to distinguish polysemous senses (e.g., "bank" of a river vs financial "bank").

UNIT 2: TRANSFORMER ARCHITECTURE & SELF-ATTENTION
2.1 Scaled Dot-Product and Multi-Head Attention
The Transformer architecture eliminates recurrence, enabling massive parallelization. Given query matrix $Q$, key matrix $K$, and value matrix $V$ of dimension $d_k$, Scaled Dot-Product Attention is computed as:
$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
The scaling factor $\frac{1}{\sqrt{d_k}}$ prevents dot products from growing excessively large for high dimensions, which would drive the softmax function into regions with vanishing gradients. Multi-Head Attention projects $Q, K, V$ into $h$ distinct representation subspaces, concatenating outputs: $\text{MHA}(Q, K, V) = \text{Concat}(\text{head}_1, \dots, \text{head}_h)W^O$.

2.2 Positional Encodings and Normalization
Because self-attention is permutation-invariant, positional information must be injected. Sinusoidal absolute positional encodings use trigonometric frequencies: $PE_{(pos, 2i)} = \sin(pos / 10000^{2i/d})$. Modern foundation models (e.g., LLaMA) adopt Rotary Position Embeddings (RoPE), rotating key and query vectors in complex planes to preserve relative token distances. RMSNorm (Root Mean Square Normalization) replaces LayerNorm to accelerate inference.

UNIT 3: LARGE LANGUAGE MODEL PRE-TRAINING & FINE-TUNING
3.1 Pre-training Objectives: Masked vs Causal Language Modeling
BERT (Bidirectional Encoder Representations from Transformers) employs Masked Language Modeling (MLM), predicting randomly masked tokens (15% probability) using bidirectional context. Autoregressive Causal Language Models (e.g., GPT, Claude, Gemini) optimize next-token prediction using unilateral causal masking: $\mathcal{L}_{CLM} = -\sum_{t=1}^T \log P(x_t \mid x_{<t})$.

3.2 Parameter-Efficient Fine-Tuning (PEFT) and LoRA
Fine-tuning full trillion-parameter weights $\Delta W \in \mathbb{R}^{d \times k}$ is computationally prohibitive. Low-Rank Adaptation (LoRA) freezes pretrained weight $W_0$ and injects trainable rank decomposition matrices $A \in \mathbb{R}^{r \times k}$ and $B \in \mathbb{R}^{d \times r}$ with rank $r \ll \min(d, k)$:
$$W = W_0 + \frac{\alpha}{r}BA$$
This reduces trainable parameters by over 99% while maintaining downstream task performance.

UNIT 4: ALIGNMENT, RLHF & RETRIEVAL-AUGMENTED GENERATION (RAG)
4.1 Model Alignment: RLHF and Direct Preference Optimization (DPO)
Pretrained LLMs can generate toxic, biased, or untruthful text. Reinforcement Learning from Human Feedback (RLHF) trains a scalar Reward Model $R_\phi(x, y)$ on human pairwise preferences, optimizing policy $\pi_\theta$ via Proximal Policy Optimization (PPO) penalized by KL-divergence: $\mathbb{E}[R(x, y) - \beta D_{KL}(\pi_\theta \parallel \pi_{ref})]$. Direct Preference Optimization (DPO) algebraically bypasses the reward model, optimizing policy directly on paired preferences $(y_w \succ y_l)$.

4.2 Retrieval-Augmented Generation (RAG) Architectures
RAG systems mitigate hallucination by anchoring generation to factual enterprise knowledge. Documents are chunked, converted into dense vectors via neural embedding models, and indexed in high-dimensional vector databases using Approximate Nearest Neighbor (ANN) search (HNSW or ScaNN). Cosine similarity measures relevance: $\text{sim}(u, v) = \frac{u \cdot v}{\|u\| \|v\|}$. Retrieved context is injected into the LLM system prompt.
""".strip()

CY201_DOCUMENT_TEXT = """
CRYPTOGRAPHY & NETWORK SECURITY (CY-201)
COURSE LECTURE NOTES & SYLLABUS REFERENCE
DEPARTMENT OF COMPUTER SCIENCE & INFORMATION SECURITY

UNIT 1: CLASSICAL & MODERN SYMMETRIC CIPHERS
1.1 Shannon Information Secrecy and Feistel Structures
Claude Shannon established information-theoretic security: a cipher achieves perfect secrecy if and only if $P(M = m \mid C = c) = P(M = m)$, exemplified exclusively by the One-Time Pad where key entropy equals or exceeds message entropy. Practical ciphers balance confusion (complex relation between key and ciphertext) and diffusion (dissipating plaintext statistics across ciphertext). Feistel networks (DES) split plaintext into left and right halves, alternating rounds: $L_i = R_{i-1}$, $R_i = L_{i-1} \oplus F(R_{i-1}, K_i)$.

1.2 Advanced Encryption Standard (AES) and Authenticated Encryption
AES is a Substitution-Permutation Network (SPN) operating on a $4 \times 4$ byte state matrix over Galois Field $GF(2^8)$. Each round executes SubBytes (non-linear S-box), ShiftRows (cyclical byte permutation), MixColumns (matrix multiplication in $GF(2^8)$), and AddRoundKey. AES uses 128, 192, or 256-bit keys with 10, 12, or 14 rounds. Galois/Counter Mode (AES-GCM) provides Authenticated Encryption with Associated Data (AEAD), producing both ciphertext and a cryptographic GMAC authentication tag.

UNIT 2: ASYMMETRIC CRYPTOGRAPHY & KEY EXCHANGE
2.1 Diffie-Hellman Key Exchange and Discrete Logarithm
Diffie-Hellman enables two parties to negotiate a shared secret over an insecure channel. Alice and Bob agree on public prime modulus $p$ and generator $g$. Alice computes $A = g^a \pmod p$, Bob computes $B = g^b \pmod p$. Their shared secret is $K = B^a \pmod p = A^b \pmod p = g^{ab} \pmod p$. Security relies on the intractability of the Computational Diffie-Hellman (CDH) problem in cyclic groups.

2.2 RSA Cryptosystem and Elliptic Curve Cryptography (ECC)
RSA relies on integer factorization hardness. Choose large primes $p, q$, compute modulus $n = pq$ and Euler totient $\phi(n) = (p-1)(q-1)$. Select public exponent $e$ such that $\gcd(e, \phi(n)) = 1$, and compute private key $d \equiv e^{-1} \pmod{\phi(n)}$. Encryption: $c \equiv m^e \pmod n$; Decryption: $m \equiv c^d \pmod n$. Elliptic Curve Cryptography operates over Weierstrass curves $y^2 = x^3 + ax + b \pmod p$, offering equivalent 128-bit security with 256-bit keys compared to RSA 3072-bit keys.

UNIT 3: CRYPTOGRAPHIC HASH FUNCTIONS & DIGITAL SIGNATURES
3.1 Properties of Cryptographic Hash Functions & SHA-256
Cryptographic hash functions map arbitrary-length bitstrings to fixed-length outputs ($H: \{0, 1\}^* \to \{0, 1\}^n$) satisfying three core properties: Pre-image resistance (one-way), Second pre-image resistance (weak collision resistance), and Collision resistance (finding any $x \neq y$ such that $H(x) = H(y)$ requires $\mathcal{O}(2^{n/2})$ evaluations via the Birthday Attack). SHA-256 employs the Merkle-Damgård iterative compression structure with 64 rounds of non-linear logical functions.

3.2 HMAC and ECDSA Digital Signatures
HMAC provides message authentication using a shared key $K$: $\text{HMAC}(K, m) = H((K \oplus \text{opad}) \parallel H((K \oplus \text{ipad}) \parallel m))$. Digital signatures provide non-repudiation. ECDSA (Elliptic Curve Digital Signature Algorithm) signs message digest $e = H(m)$ using private key $d_A$ and ephemeral nonce $k$, producing signature pair $(r, s)$.

UNIT 4: NETWORK PROTOCOLS & ZERO TRUST SECURITY
4.1 TLS 1.3 Protocol Handshake
Transport Layer Security (TLS 1.3) streamlines the cryptographic handshake to 1 Round-Trip Time (1-RTT). It deprecates insecure cipher suites (RC4, 3DES, static RSA key exchange), mandates Ephemeral Diffie-Hellman (ECDHE) for Perfect Forward Secrecy (PFS), and encrypts all handshake certificates. Pre-Shared Key (PSK) mode enables 0-RTT resumption.

4.2 IPsec and Zero Trust Architecture
IPsec secures network layer packets using Authentication Header (AH, integrity/authentication without encryption) and Encapsulating Security Payload (ESP, confidentiality and integrity) in transport or tunnel modes. Zero Trust Network Architecture enforces the principle of "never trust, always verify", utilizing micro-segmentation, mutual TLS (mTLS), and centralized identity validation (OAuth 2.0 / OIDC tokens).
""".strip()

DS202_DOCUMENT_TEXT = """
ADVANCED DATA STRUCTURES & ALGORITHMS (DS-202)
COURSE LECTURE NOTES & SYLLABUS REFERENCE
DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING

UNIT 1: SELF-BALANCING BINARY SEARCH TREES
1.1 AVL Trees and Rotations
An AVL tree is a strictly height-balanced binary search tree where the balance factor $BF = \text{height}(\text{left}) - \text{height}(\text{right}) \in \{-1, 0, +1\}$ for every node. When insertions or deletions violate this invariant, four deterministic rotation cases restore balance: Left-Left (single Right Rotation), Right-Right (single Left Rotation), Left-Right (Left rotation on child followed by Right rotation on node), and Right-Left. Maximum height is bounded by $1.44 \log_2 N$, guaranteeing worst-case search, insertion, and deletion in $\mathcal{O}(\log N)$ time.

1.2 Red-Black Trees and Invariants
A Red-Black tree is a self-balancing BST satisfying five properties: (1) Every node is red or black, (2) The root is black, (3) Every leaf (NIL) is black, (4) If a node is red, both its children are black, (5) Every simple path from a node to descendant leaves contains identical numbers of black nodes (black-height $bh$). Height is at most $2 \log_2(N + 1)$. Red-black trees require at most 2 rotations on insertion and 3 on deletion, making them the preferred data structure for associative arrays (e.g., C++ `std::map`, Java `TreeMap`).

UNIT 2: PRIORITY QUEUES & ADVANCED HEAPS
2.1 Fibonacci Heaps and Amortized Analysis
A Fibonacci Heap is a collection of min-heap-ordered trees. Unlike binary heaps where `decrease-key` takes $\mathcal{O}(\log N)$, Fibonacci Heaps achieve amortized $\mathcal{O}(1)$ time for `insert`, `minimum`, `union`, and `decrease-key`, with `delete-min` taking amortized $\mathcal{O}(\log N)$. Cascading cuts prevent trees from becoming excessively deep: when a non-root node loses a second child, it is immediately cut from its parent and moved to the root list. This yields Dijkstra's shortest path time complexity of $\mathcal{O}(E + V \log V)$.

2.2 Binomial Heaps and Meld Operations
A Binomial Heap is a forest of binomial trees $B_k$ where tree $B_k$ has $2^k$ nodes, height $k$, and degree $k$. The binary representation of $N$ determines the unique set of binomial trees. Merging (melding) two Binomial Heaps parallels binary integer addition, executing in $\mathcal{O}(\log N)$ worst-case time.

UNIT 3: GRAPH FLOW NETWORKS & DISJOINT SETS
3.1 Disjoint Set Union (DSU) with Path Compression
Disjoint Set Union manages partitions of elements across dynamic equivalence classes using `find` and `union` operations. Combining Union by Rank (attaching shallower trees beneath deeper trees) with Path Compression (flattening tree structure during find operations) achieves an amortized operational time of $\mathcal{O}(\alpha(N))$, where $\alpha$ is the inverse Ackermann function ($\alpha(N) \le 4$ for all practical universe sizes $N < 10^{80}$).

3.2 Max-Flow Min-Cut and Edmonds-Karp Algorithm
A flow network is a directed graph $G = (V, E)$ with edge capacities $c(u, v) \ge 0$. The Max-Flow Min-Cut Theorem proves that the maximum amount of flow passing from source $s$ to sink $t$ equals the minimum capacity among all $s$-$t$ cuts. The Edmonds-Karp algorithm implements the Ford-Fulkerson method by selecting the shortest augmenting path using Breadth-First Search (BFS), strictly bounding time complexity to $\mathcal{O}(V \cdot E^2)$, avoiding infinite loops with irrational capacities.

UNIT 4: STRING MATCHING & GEOMETRIC DATA STRUCTURES
4.1 Knuth-Morris-Pratt (KMP) and Aho-Corasick Automata
The KMP algorithm performs linear-time string matching in $\mathcal{O}(N + M)$ by preprocessing pattern string $P$ into a longest proper prefix which is also a suffix ($\pi$ array). On character mismatch, the pattern pointer shifts without backtracking the text index. The Aho-Corasick algorithm generalizes KMP to multiple dictionary patterns simultaneously, constructing a trie equipped with failure transitions and output links for $\mathcal{O}(N + \text{matches})$ total inspection time.

4.2 KD-Trees and Convex Hull
A $k$-d tree (k-dimensional tree) is a space-partitioning data structure for organizing points in $k$-dimensional space. Splitting hyperplanes cycle cyclically through coordinate axes $(x, y, z)$ at alternating depths, enabling efficient range queries and nearest neighbor search in $\mathcal{O}(\log N)$ expected time. Graham's scan computes the 2D convex hull of $N$ points in $\mathcal{O}(N \log N)$ time by angular sorting followed by stack-based counter-clockwise cross-product verification.
""".strip()

# ==============================================================================
# SUBJECT DATA DICTIONARIES
# ==============================================================================

SUBJECTS_CONFIG = [
    {
        "id": "ITS-401",
        "code": "ITS-401",
        "name": "Intelligent Transport Systems",
        "description": "Comprehensive study of modern sensing, traffic optimization, V2X communications, and autonomous mobility architectures.",
        "doc_id": "doc_its_notes_01",
        "doc_title": "ITS Comprehensive Lecture Notes (Units 1-4)",
        "doc_file": "ITS_Lecture_Notes_2026.pdf",
        "doc_text": ITS_DOCUMENT_TEXT,
        "headings": [
            "UNIT 1: INTRODUCTION TO INTELLIGENT TRANSPORT SYSTEMS",
            "1.1 Fundamentals and Architecture of ITS",
            "1.2 Sensor Technologies and Traffic Surveillance",
            "UNIT 2: ADVANCED TRAFFIC MANAGEMENT SYSTEMS (ATMS)",
            "2.1 Real-Time Traffic Signal Optimization",
            "2.2 Incident Detection and Ramp Metering",
            "UNIT 3: ADVANCED TRAVELER INFORMATION SYSTEMS (ATIS)",
            "3.1 Architecture of ATIS and Commuter Guidance",
            "3.2 Electronic Toll Collection (ETC) and RFID",
            "UNIT 4: CONNECTED AND AUTONOMOUS VEHICLES (CAV)",
            "4.1 V2X Communication Frameworks",
            "4.2 Cooperative Adaptive Cruise Control and Platooning"
        ],
        "topics": [
            (1, "Unit 1: Introduction to ITS", "Fundamentals and Architecture of ITS", "Physical, logical, and communications subsystems in ITS architecture."),
            (1, "Unit 1: Introduction to ITS", "Sensor Technologies and Traffic Surveillance", "Intrusive inductive loop detectors and non-intrusive radar/video sensors."),
            (2, "Unit 2: ATMS", "Real-Time Traffic Signal Optimization", "SCATS and SCOOT coordinated adaptive split and offset algorithms."),
            (2, "Unit 2: ATMS", "Incident Detection and Ramp Metering", "Freeway queue breakdown prevention, VMS signage, automated incident algorithms."),
            (3, "Unit 3: ATIS", "Architecture of ATIS and Commuter Guidance", "Real-time trip planning, GPS probe ingestion, dynamic ETA computation."),
            (3, "Unit 3: ATIS", "Electronic Toll Collection and RFID", "FASTag passive UHF RFID operation, antenna arrays, transponder protocols."),
            (4, "Unit 4: CAV", "V2X Communication Frameworks", "DSRC IEEE 802.11p 5.9GHz vs Cellular-V2X direct sidelink PC5."),
            (4, "Unit 4: CAV", "Cooperative Adaptive Cruise Control and Platooning", "Radar plus V2V messaging for ultra-tight multi-truck platooning.")
        ]
    },
    {
        "id": "CS-301",
        "code": "CS-301",
        "name": "Distributed Systems & Cloud Computing",
        "description": "Foundations of distributed consensus, RPC frameworks, consistent hashing, LSM trees, and cloud orchestration.",
        "doc_id": "doc_cs301_notes_01",
        "doc_title": "Distributed Systems & Cloud Computing Lecture Notes (Units 1-4)",
        "doc_file": "CS301_Distributed_Systems_Notes.pdf",
        "doc_text": CS301_DOCUMENT_TEXT,
        "headings": [
            "UNIT 1: FOUNDATIONS OF DISTRIBUTED SYSTEMS & REMOTE PROCEDURE CALLS",
            "1.1 System Models, Logical Clocks, and the CAP Theorem",
            "1.2 Remote Procedure Calls and Serialization",
            "UNIT 2: CONSENSUS PROTOCOLS & FAULT TOLERANCE",
            "2.1 Paxos and Raft Consensus Algorithms",
            "2.2 Byzantine Fault Tolerance",
            "UNIT 3: DISTRIBUTED STORAGE ARCHITECTURES",
            "3.1 Consistent Hashing and Dynamo Design Patterns",
            "3.2 Log-Structured Merge Trees (LSM) and Spanner TrueTime",
            "UNIT 4: CLOUD VIRTUALIZATION & CONTAINER ORCHESTRATION",
            "4.1 Hypervisors, Namespaces, and Cgroups",
            "4.2 Kubernetes Architecture and Pod Scheduling"
        ],
        "topics": [
            (1, "Unit 1: Foundations & RPC", "Logical Clocks and the CAP Theorem", "Lamport clocks, Vector clocks, and CAP trade-offs between CP and AP."),
            (1, "Unit 1: Foundations & RPC", "gRPC and Binary Serialization", "HTTP/2 multiplexing and Protocol Buffers serialization."),
            (2, "Unit 2: Consensus & Fault Tolerance", "Raft Consensus and Log Replication", "Leader election, quorum requirements, and state machine replication."),
            (2, "Unit 2: Consensus & Fault Tolerance", "Byzantine Fault Tolerance", "3f + 1 node bounds and PBFT adversarial failure resilience."),
            (3, "Unit 3: Distributed Storage", "Consistent Hashing and Quorum Replication", "Hash ring token mapping, virtual nodes, and R + W > N quorum logic."),
            (3, "Unit 3: Distributed Storage", "LSM Trees and Spanner TrueTime", "MemTable flush to SSTables, TrueTime atomic clocks, and external consistency."),
            (4, "Unit 4: Cloud & Containers", "Linux Namespaces and Control Groups", "Cgroups v2 resource limits and namespace isolation."),
            (4, "Unit 4: Cloud & Containers", "Kubernetes Pod Scheduling Architecture", "Kube-scheduler predicates, scoring, and etcd Raft state persistence.")
        ]
    },
    {
        "id": "AI-402",
        "code": "AI-402",
        "name": "Natural Language Processing & Large Language Models",
        "description": "Deep dive into Transformer architectures, self-attention, pre-training objectives, LoRA PEFT, and RAG systems.",
        "doc_id": "doc_ai402_notes_01",
        "doc_title": "NLP & Large Language Models Comprehensive Notes (Units 1-4)",
        "doc_file": "AI402_NLP_LLM_Notes.pdf",
        "doc_text": AI402_DOCUMENT_TEXT,
        "headings": [
            "UNIT 1: FOUNDATIONS OF LANGUAGE REPRESENTATION & TOKENIZATION",
            "1.1 Tokenization and Subword Algorithms",
            "1.2 Static vs Contextual Word Embeddings",
            "UNIT 2: TRANSFORMER ARCHITECTURE & SELF-ATTENTION",
            "2.1 Scaled Dot-Product and Multi-Head Attention",
            "2.2 Positional Encodings and Normalization",
            "UNIT 3: LARGE LANGUAGE MODEL PRE-TRAINING & FINE-TUNING",
            "3.1 Pre-training Objectives: Masked vs Causal Language Modeling",
            "3.2 Parameter-Efficient Fine-Tuning (PEFT) and LoRA",
            "UNIT 4: ALIGNMENT, RLHF & RETRIEVAL-AUGMENTED GENERATION (RAG)",
            "4.1 Model Alignment: RLHF and Direct Preference Optimization (DPO)",
            "4.2 Retrieval-Augmented Generation (RAG) Architectures"
        ],
        "topics": [
            (1, "Unit 1: Representations & Tokenization", "Subword Tokenization (BPE & WordPiece)", "Byte-Pair Encoding merge operations and vocabulary construction."),
            (1, "Unit 1: Representations & Tokenization", "Static Word Embeddings & Polysemy", "Word2Vec negative sampling, GloVe factorization, and polysemy limitations."),
            (2, "Unit 2: Transformer Architecture", "Scaled Dot-Product and Multi-Head Attention", "Attention(Q, K, V) formulation, scaling factor 1/sqrt(d_k), and subspace projection."),
            (2, "Unit 2: Transformer Architecture", "Positional Encodings and Normalization", "Sinusoidal embeddings, Rotary Position Embeddings (RoPE), and RMSNorm."),
            (3, "Unit 3: Pre-training & Fine-Tuning", "Masked vs Autoregressive Causal LM", "BERT bidirectional MLM vs GPT causal language modeling objectives."),
            (3, "Unit 3: Pre-training & Fine-Tuning", "Parameter-Efficient Fine-Tuning and LoRA", "Low-Rank Adaptation W = W_0 + (alpha/r)BA with frozen base weights."),
            (4, "Unit 4: Alignment & RAG", "RLHF and Direct Preference Optimization", "PPO reward modeling, KL penalties, and DPO closed-form optimization."),
            (4, "Unit 4: Alignment & RAG", "Retrieval-Augmented Generation & Vector DBs", "Dense vector embedding retrieval, HNSW approximate nearest neighbor search, and cosine similarity.")
        ]
    },
    {
        "id": "CY-201",
        "code": "CY-201",
        "name": "Cryptography & Network Security",
        "description": "Comprehensive study of symmetric block ciphers, asymmetric key exchange, digital signatures, TLS 1.3, and zero-trust architectures.",
        "doc_id": "doc_cy201_notes_01",
        "doc_title": "Cryptography & Network Security Reference Notes (Units 1-4)",
        "doc_file": "CY201_Cryptography_Security_Notes.pdf",
        "doc_text": CY201_DOCUMENT_TEXT,
        "headings": [
            "UNIT 1: CLASSICAL & MODERN SYMMETRIC CIPHERS",
            "1.1 Shannon Information Secrecy and Feistel Structures",
            "1.2 Advanced Encryption Standard (AES) and Authenticated Encryption",
            "UNIT 2: ASYMMETRIC CRYPTOGRAPHY & KEY EXCHANGE",
            "2.1 Diffie-Hellman Key Exchange and Discrete Logarithm",
            "2.2 RSA Cryptosystem and Elliptic Curve Cryptography (ECC)",
            "UNIT 3: CRYPTOGRAPHIC HASH FUNCTIONS & DIGITAL SIGNATURES",
            "3.1 Properties of Cryptographic Hash Functions & SHA-256",
            "3.2 HMAC and ECDSA Digital Signatures",
            "UNIT 4: NETWORK PROTOCOLS & ZERO TRUST SECURITY",
            "4.1 TLS 1.3 Protocol Handshake",
            "4.2 IPsec and Zero Trust Architecture"
        ],
        "topics": [
            (1, "Unit 1: Symmetric Ciphers", "Shannon Perfect Secrecy and Feistel Networks", "Information-theoretic security, One-Time Pad entropy, confusion and diffusion."),
            (1, "Unit 1: Symmetric Ciphers", "AES Galois Field & Authenticated Encryption (GCM)", "SubBytes, ShiftRows, MixColumns over GF(2^8), and Galois Counter Mode."),
            (2, "Unit 2: Asymmetric Cryptography", "Diffie-Hellman Key Exchange", "Discrete logarithm problem in cyclic groups and shared secret negotiation."),
            (2, "Unit 2: Asymmetric Cryptography", "RSA and Elliptic Curve Cryptography", "Euler totient theorem, modular inverse, and Weierstrass curve group law."),
            (3, "Unit 3: Hash Functions & Signatures", "Properties of Cryptographic Hashes & SHA-256", "Pre-image resistance, collision resistance, Birthday attack, and Merkle-Damgard."),
            (3, "Unit 3: Hash Functions & Signatures", "HMAC and ECDSA Signatures", "Keyed-hash message authentication and elliptic curve digital signatures."),
            (4, "Unit 4: Network Protocols & Zero Trust", "TLS 1.3 1-RTT Handshake & Forward Secrecy", "Ephemeral Diffie-Hellman, zero-round trip resumption, and cipher suite hardening."),
            (4, "Unit 4: Network Protocols & Zero Trust", "IPsec and Zero Trust Network Architecture", "AH vs ESP, microsegmentation, mutual TLS, and OAuth2/OIDC validation.")
        ]
    },
    {
        "id": "DS-202",
        "code": "DS-202",
        "name": "Advanced Data Structures & Algorithms",
        "description": "Rigorous algorithmic study of self-balancing search trees, amortized analysis, Fibonacci heaps, network flow, and geometric structures.",
        "doc_id": "doc_ds202_notes_01",
        "doc_title": "Advanced Data Structures & Algorithms Notes (Units 1-4)",
        "doc_file": "DS202_Advanced_DSA_Notes.pdf",
        "doc_text": DS202_DOCUMENT_TEXT,
        "headings": [
            "UNIT 1: SELF-BALANCING BINARY SEARCH TREES",
            "1.1 AVL Trees and Rotations",
            "1.2 Red-Black Trees and Invariants",
            "UNIT 2: PRIORITY QUEUES & ADVANCED HEAPS",
            "2.1 Fibonacci Heaps and Amortized Analysis",
            "2.2 Binomial Heaps and Meld Operations",
            "UNIT 3: GRAPH FLOW NETWORKS & DISJOINT SETS",
            "3.1 Disjoint Set Union (DSU) with Path Compression",
            "3.2 Max-Flow Min-Cut and Edmonds-Karp Algorithm",
            "UNIT 4: STRING MATCHING & GEOMETRIC DATA STRUCTURES",
            "4.1 Knuth-Morris-Pratt (KMP) and Aho-Corasick Automata",
            "4.2 KD-Trees and Convex Hull"
        ],
        "topics": [
            (1, "Unit 1: Self-Balancing Trees", "AVL Trees and Rebalancing Rotations", "Balance factors in {-1, 0, 1}, single and double rotation invariants."),
            (1, "Unit 1: Self-Balancing Trees", "Red-Black Tree Color Invariants", "Black-height preservation, red-node child constraints, and rotation bounds."),
            (2, "Unit 2: Advanced Heaps", "Fibonacci Heaps and Amortized O(1) Operations", "Potential method amortized analysis, cascading cuts, and Dijkstra speedup."),
            (2, "Unit 2: Advanced Heaps", "Binomial Heaps and Forest Melds", "Binomial tree binomial coefficient properties and O(log N) heap merges."),
            (3, "Unit 3: Flow Networks & Sets", "Disjoint Set Union with Inverse Ackermann", "Union by rank, path compression, and O(alpha(N)) amortized complexity."),
            (3, "Unit 3: Flow Networks & Sets", "Max-Flow Min-Cut and Edmonds-Karp", "Augmenting paths via BFS and polynomial O(V * E^2) network flow bounds."),
            (4, "Unit 4: Strings & Geometry", "KMP String Matching and Prefix Automaton", "Failure function pi computation and O(N + M) text search."),
            (4, "Unit 4: Strings & Geometry", "KD-Trees and Convex Hull Algorithms", "Cyclic dimension splitting for nearest neighbor search and Graham scan.")
        ]
    }
]

# ==============================================================================
# SEED QUESTIONS BY SUBJECT (8 approved questions per subject: 5 MCQ, 2 Short, 1 Long = 30 Marks)
# ==============================================================================

SEED_QUESTIONS_BY_SUBJECT = {
    "ITS-401": [
        # 5 MCQs (2M each = 10M)
        {
            "text": "Which technology forms the basis of intrusive traffic surveillance by detecting magnetic disruptions caused by vehicle chassis?",
            "type": "mcq",
            "options": ["Inductive loop detectors", "Pneumatic road tubes", "Microwave radar sensors", "Video image processing cameras"],
            "correct": "Inductive loop detectors",
            "model_ans": None, "rubric": None,
            "explanation": "Inductive loop detectors are embedded beneath pavement and detect magnetic field disruptions caused by metallic vehicle chassis.",
            "diff": "easy", "marks": 2.0, "topic_idx": 1,
            "excerpt": "Inductive loop detectors embedded beneath pavement detect magnetic field disruptions caused by metallic vehicle chassis, providing reliable vehicle counts, speed, and occupancy metrics."
        },
        {
            "text": "What is the primary operational objective of freeway ramp metering in an ATMS framework?",
            "type": "mcq",
            "options": ["To eliminate speed limits on entry ramps", "To regulate vehicle entry rates and prevent mainline freeway breakdown", "To collect electronic tolls automatically", "To inspect vehicle emissions prior to highway entry"],
            "correct": "To regulate vehicle entry rates and prevent mainline freeway breakdown",
            "model_ans": None, "rubric": None,
            "explanation": "Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate of vehicle entry, mitigating shockwave propagation.",
            "diff": "medium", "marks": 2.0, "topic_idx": 3,
            "excerpt": "Freeway ramp metering utilizes traffic signals on entrance ramps to regulate the rate at which vehicles enter mainline highways, preventing freeway breakdown and shockwave propagation during peak demand periods."
        },
        {
            "text": "Which standard and frequency band does Dedicated Short-Range Communications (DSRC) utilize for V2X safety applications?",
            "type": "mcq",
            "options": ["IEEE 802.11b at 2.4 GHz", "IEEE 802.11p in the 5.9 GHz ITS band", "IEEE 802.15.4 at 868 MHz", "3GPP Release 16 at 28 GHz"],
            "correct": "IEEE 802.11p in the 5.9 GHz ITS band",
            "model_ans": None, "rubric": None,
            "explanation": "DSRC is based on IEEE 802.11p operating in the licensed 5.9 GHz ITS band, providing ultra-low latency (<5 ms) over short ranges.",
            "diff": "medium", "marks": 2.0, "topic_idx": 6,
            "excerpt": "Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters)."
        },
        {
            "text": "Electronic Toll Collection systems like FASTag operate primarily in which frequency spectrum?",
            "type": "mcq",
            "options": ["Low Frequency (125-134 kHz)", "High Frequency (13.56 MHz)", "Passive UHF band (865-868 MHz)", "Microwave band (2.4-5 GHz)"],
            "correct": "Passive UHF band (865-868 MHz)",
            "model_ans": None, "rubric": None,
            "explanation": "Automated Electronic Toll Collection systems utilize passive UHF RFID operating in the 865-868 MHz frequency band.",
            "diff": "easy", "marks": 2.0, "topic_idx": 5,
            "excerpt": "Automated Electronic Toll Collection systems, such as FASTag, leverage Radio Frequency Identification (RFID) operating in the passive UHF band (865-868 MHz)."
        },
        {
            "text": "What does the SCATS adaptive traffic control system stand for?",
            "type": "mcq",
            "options": ["Sydney Coordinated Adaptive Traffic System", "System for Coordinated Arterial Traffic Scheduling", "Sequential Computerized Adaptive Timing Strategy", "Synchronized Corridor Automated Traffic System"],
            "correct": "Sydney Coordinated Adaptive Traffic System",
            "model_ans": None, "rubric": None,
            "explanation": "SCATS stands for Sydney Coordinated Adaptive Traffic System, which dynamically adjusts signal timings based on real-time traffic saturation levels.",
            "diff": "easy", "marks": 2.0, "topic_idx": 2,
            "excerpt": "SCATS (Sydney Coordinated Adaptive Traffic System) and SCOOT (Split Cycle Offset Optimisation Technique) continually calculate green splits, cycle lengths, and coordinate intersection offsets."
        },
        # 2 Short Answers (5M each = 10M)
        {
            "text": "Explain the architectural layers of an Intelligent Transport System and discuss how traffic surveillance data flows between them.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "The national ITS architecture comprises physical, logical, and communication layers. The physical layer encompasses roadside sensors (inductive loops, VIPS cameras) and onboard units. The communication layer transmits raw metrics over fiber or cellular links to the logical layer situated in Traffic Management Centers, which executes coordination algorithms (such as SCATS/SCOOT) and issues real-time advisories.",
            "rubric": [
                {"criterion": "Identification of physical, logical, and communication layers", "marks": 2.0},
                {"criterion": "Explanation of roadside sensor data collection", "marks": 1.5},
                {"criterion": "Description of Traffic Management Center feedback loop", "marks": 1.5}
            ],
            "explanation": "Outlines the 3-tier ITS architecture and traces sensor telemetry from roadside equipment to central controllers.",
            "diff": "medium", "marks": 5.0, "topic_idx": 0,
            "excerpt": "The national ITS architecture consists of physical, logical, and communication layers that interconnect traffic management centers, roadside field equipment, vehicles, and commuters."
        },
        {
            "text": "Distinguish between DSRC and Cellular-V2X (C-V2X) communication technologies in terms of architecture, range, and latency.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "DSRC is based on IEEE 802.11p operating in the licensed 5.9 GHz band, designed for direct short-range communications (<300m) with ultra-low latency (<5ms). Conversely, C-V2X utilizes 4G/5G cellular standards, supporting direct sidelink PC5 for localized communications and Uu cellular network links for wide-area dissemination, offering higher data bandwidth and longer transmission ranges.",
            "rubric": [
                {"criterion": "DSRC standard (IEEE 802.11p) and performance specs", "marks": 2.0},
                {"criterion": "C-V2X architecture (PC5 sidelink and cellular Uu)", "marks": 2.0},
                {"criterion": "Comparison table/contrasting summary", "marks": 1.0}
            ],
            "explanation": "Compares vehicular wireless standards across bandwidth, range, and latency benchmarks.",
            "diff": "hard", "marks": 5.0, "topic_idx": 6,
            "excerpt": "Dedicated Short-Range Communications (DSRC) is based on the IEEE 802.11p standard operating in the licensed 5.9 GHz ITS band, offering ultra-low latency (<5 ms) over short ranges (~300 meters). Cellular-V2X (C-V2X) utilizes 4G LTE and 5G sidelink PC5 direct communication, providing longer range and greater bandwidth."
        },
        # 1 Long Answer (10M)
        {
            "text": "Provide a detailed system analysis of Cooperative Adaptive Cruise Control (CACC) and vehicle platooning. Discuss how sensor fusion and V2V communication maintain stable sub-second time gaps without compromising highway safety.",
            "type": "long_answer", "options": None, "correct": None,
            "model_ans": "Cooperative Adaptive Cruise Control (CACC) enhances conventional radar-based Adaptive Cruise Control by integrating Vehicle-to-Vehicle (V2V) wireless telemetry. While standalone ACC is constrained by sensor perception delay (often requiring 1.2 to 2.0 second headway to guarantee string stability), CACC shares instantaneous acceleration, braking intention, and trajectory vectors between lead and following vehicles via DSRC or C-V2X.\n\nKey system components include:\n1. Onboard perception (radar, lidar, and wheel encoders) measuring relative distance and closing velocity.\n2. V2V transceiver exchanging emergency deceleration triggers with zero driver reaction delay.\n3. Longitudinal platoon controller executing string-stable decentralized control laws.\n\nThis architecture enables platooning vehicles to safely compress headways down to 0.5-0.8 seconds, eliminating string shockwaves, reducing aerodynamic drag by up to 25% for trailing commercial trucks, and dramatically maximizing arterial throughput.",
            "rubric": [
                {"criterion": "Distinction between standalone ACC and cooperative CACC", "marks": 3.0},
                {"criterion": "V2V communication integration and string stability explanation", "marks": 3.0},
                {"criterion": "Safety failure modes and fallback strategies", "marks": 2.0},
                {"criterion": "Aerodynamic and throughput benefits", "marks": 2.0}
            ],
            "explanation": "Evaluates advanced CAV coordination, string stability, and aerodynamic/traffic throughput enhancements.",
            "diff": "hard", "marks": 10.0, "topic_idx": 7,
            "excerpt": "Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion."
        }
    ],

    "CS-301": [
        # 5 MCQs (2M each = 10M)
        {
            "text": "Under the CAP theorem, which property must a distributed system sacrifice if it prioritizes complete Availability during an asynchronous network partition?",
            "type": "mcq",
            "options": ["Consistency", "Latency", "Durability", "Partition Tolerance"],
            "correct": "Consistency",
            "model_ans": None, "rubric": None,
            "explanation": "The CAP theorem proves that in the presence of a network partition (P), a distributed system must choose between returning current data (Consistency) or accepting writes on isolated nodes (Availability).",
            "diff": "easy", "marks": 2.0, "topic_idx": 0,
            "excerpt": "The CAP theorem proves that any networked shared-data system can simultaneously satisfy at most two of: Consistency (every read receives the most recent write), Availability (non-failing nodes always return non-error responses), and Partition Tolerance."
        },
        {
            "text": "What is the minimum quorum size $Q$ required in a Raft consensus cluster consisting of $n = 5$ server nodes?",
            "type": "mcq",
            "options": ["2 nodes", "3 nodes", "4 nodes", "5 nodes"],
            "correct": "3 nodes",
            "model_ans": None, "rubric": None,
            "explanation": "Raft requires a strict majority quorum $Q = \\lfloor n/2 \\rfloor + 1$. For $n = 5$, $Q = \\lfloor 5/2 \\rfloor + 1 = 2 + 1 = 3$ nodes.",
            "diff": "easy", "marks": 2.0, "topic_idx": 2,
            "excerpt": "requiring a strict majority quorum $Q = \\lfloor n/2 \\rfloor + 1$."
        },
        {
            "text": "In consistent hashing, what average fraction of keys must be remapped when a new node joins a cluster of $N$ physical machines?",
            "type": "mcq",
            "options": ["$\\mathcal{O}(1)$", "$\\mathcal{O}(K/N)$", "$\\mathcal{O}(K)$", "$\\mathcal{O}(N \\log K)$"],
            "correct": "$\\mathcal{O}(K/N)$",
            "model_ans": None, "rubric": None,
            "explanation": "Consistent hashing ensures that when a node joins or leaves, only $\\mathcal{O}(K/N)$ keys are remapped on average, avoiding full rehashing.",
            "diff": "medium", "marks": 2.0, "topic_idx": 4,
            "excerpt": "When nodes join or leave, only $\\mathcal{O}(K/N)$ keys are remapped on average, avoiding catastrophic cluster data migration."
        },
        {
            "text": "To achieve Practical Byzantine Fault Tolerance (PBFT) against $f$ adversarial nodes, what is the theoretical minimum total number of nodes required?",
            "type": "mcq",
            "options": ["$2f + 1$", "$3f$", "$3f + 1$", "$4f - 1$"],
            "correct": "$3f + 1$",
            "model_ans": None, "rubric": None,
            "explanation": "In Byzantine fault tolerance, a system requires at least $3f + 1$ nodes to guarantee consensus when $f$ nodes can act maliciously or send conflicting votes.",
            "diff": "medium", "marks": 2.0, "topic_idx": 3,
            "excerpt": "In a system with $f$ Byzantine adversarial nodes, classical consensus requires at least $3f + 1$ total nodes to reach guaranteed agreement (e.g., PBFT algorithm)."
        },
        {
            "text": "Which Linux kernel mechanism is primarily responsible for enforcing CPU, memory, and disk I/O quotas on container processes?",
            "type": "mcq",
            "options": ["Kernel Namespaces", "Control Groups (cgroups v2)", "Chroot jail", "Seccomp-BPF filters"],
            "correct": "Control Groups (cgroups v2)",
            "model_ans": None, "rubric": None,
            "explanation": "Control Groups (cgroups) meter and limit physical hardware resources (CPU, RAM, block I/O), whereas Namespaces isolate process visibility.",
            "diff": "easy", "marks": 2.0, "topic_idx": 6,
            "excerpt": "Linux containerization utilizes kernel Namespaces (PID, Mount, Network, UTS, IPC) for resource isolation and Control Groups (cgroups v2) for CPU, memory, and I/O quota enforcement."
        },
        # 2 Short Answers (5M each = 10M)
        {
            "text": "Explain the architectural differences between Log-Structured Merge (LSM) Trees and B-Trees with respect to write amplification and disk I/O patterns.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "B-Trees perform in-place updates on random disk blocks, causing heavy random I/O and page fragmentation on high write throughput. In contrast, LSM Trees buffer incoming writes sequentially in an in-memory MemTable (typically a SkipList). When full, the MemTable is flushed as an immutable Sorted String Table (SSTable) to disk via purely sequential append I/O. Background compaction merges SSTables to reclaim deleted space and maintain logarithmic read search times.",
            "rubric": [
                {"criterion": "B-Tree in-place update and random I/O limitations", "marks": 2.0},
                {"criterion": "LSM Tree MemTable sequential append to immutable SSTables", "marks": 2.0},
                {"criterion": "Explanation of background compaction process", "marks": 1.0}
            ],
            "explanation": "Compares storage engine architectures regarding random vs sequential disk writes and write amplification.",
            "diff": "medium", "marks": 5.0, "topic_idx": 5,
            "excerpt": "Log-Structured Merge (LSM) trees optimize write performance by buffering mutations in an in-memory MemTable before flushing them sequentially to immutable disk SSTables, performing background compaction."
        },
        {
            "text": "State the quorum replication condition required to guarantee strong read-your-writes consistency across $N$ replicas with $R$ read nodes and $W$ write nodes.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "Strong consistency in quorum replication requires: $$R + W > N$$ where $N$ is the replication factor, $W$ is the write quorum (nodes that must acknowledge a write before success), and $R$ is the read quorum. By the Pigeonhole Principle, if $R + W > N$, the set of nodes queried during a read operation is guaranteed to overlap with the set of nodes written to in at least one replica, ensuring that the latest timestamped value is always observed.",
            "rubric": [
                {"criterion": "Correct mathematical condition $R + W > N$", "marks": 2.0},
                {"criterion": "Pigeonhole principle and overlapping replica explanation", "marks": 2.0},
                {"criterion": "Timestamp reconciliation / read-repair mention", "marks": 1.0}
            ],
            "explanation": "Rigorous derivation of quorum intersection and strong consistency guarantees.",
            "diff": "medium", "marks": 5.0, "topic_idx": 4,
            "excerpt": "Quorum replication follows the equation $R + W > N$ to guarantee strong read-your-writes consistency."
        },
        # 1 Long Answer (10M)
        {
            "text": "Design a globally distributed key-value store architecture providing strict serializability across multiple geographical regions. Detail how TrueTime or Raft consensus coordinates transactions and prevents stale reads.",
            "type": "long_answer", "options": None, "correct": None,
            "model_ans": "A globally distributed key-value store achieving strict serializability (external consistency) can be designed around the Google Spanner architectural paradigm:\n\n1. Sharding and Replication:\nData is split into tablets and replicated across multi-region zones using Raft or Multi-Paxos consensus groups. Each consensus group maintains an elected leader handling transactional mutations.\n\n2. TrueTime API for External Consistency:\nTrueTime bounds clock skew between atomic clocks and GPS receivers across data centers to an uncertainty window $\\epsilon \\approx \\pm 1\\text{ ms}$. Transactions are assigned commit timestamps $s \\ge t_{latest}$. The leader implements a 'commit-wait' rule, delaying client response until $t_{now} > s + \\epsilon$, mathematically guaranteeing that if transaction $T_2$ initiates after $T_1$ commits anywhere on Earth, $s_2 > s_1$.\n\n3. Concurrency Control and Stale Read Prevention:\nTwo-Phase Locking (2PL) is used for read-write transactions, while Two-Phase Commit (2PC) orchestrates cross-shard distributed transactions. Read-only queries execute lock-free at a past timestamp without blocking concurrent writes, ensuring maximum read scalability without staleness.",
            "rubric": [
                {"criterion": "Multi-region consensus replication via Raft/Paxos", "marks": 2.5},
                {"criterion": "TrueTime uncertainty bound $\\epsilon$ and commit-wait rule", "marks": 3.0},
                {"criterion": "Two-Phase Commit (2PC) and Two-Phase Locking (2PL) integration", "marks": 2.5},
                {"criterion": "Lock-free consistent snapshot reads design", "marks": 2.0}
            ],
            "explanation": "Comprehensive system design demonstrating multi-region consensus, TrueTime synchronization, and strict serializability.",
            "diff": "hard", "marks": 10.0, "topic_idx": 5,
            "excerpt": "Google Spanner achieves globally distributed external consistency (strict serializability) using TrueTime APIs backed by atomic clocks and GPS receivers, bounding uncertainty intervals to $\\epsilon \\approx \\pm 1\\text{ ms}$."
        }
    ],

    "AI-402": [
        # 5 MCQs (2M each = 10M)
        {
            "text": "In the Transformer self-attention formula $\\text{Attention}(Q, K, V) = \\text{softmax}\\left(\\frac{QK^T}{\\sqrt{d_k}}\\right)V$, what is the mathematical purpose of the scaling factor $\\frac{1}{\\sqrt{d_k}}$?",
            "type": "mcq",
            "options": ["To normalize embedding dimensions to unit norm", "To prevent dot products from becoming excessively large, which pushes softmax into vanishing gradient regions", "To enforce causal masking on future tokens", "To eliminate the need for multi-head projections"],
            "correct": "To prevent dot products from becoming excessively large, which pushes softmax into vanishing gradient regions",
            "model_ans": None, "rubric": None,
            "explanation": "For large dimensions $d_k$, the dot products grow large in magnitude, pushing the softmax function into regions where gradients are extremely small.",
            "diff": "medium", "marks": 2.0, "topic_idx": 2,
            "excerpt": "The scaling factor $\\frac{1}{\\sqrt{d_k}}$ prevents dot products from growing excessively large for high dimensions, which would drive the softmax function into regions with vanishing gradients."
        },
        {
            "text": "Which subword tokenization algorithm initializes the vocabulary with individual characters and iteratively merges the most frequent adjacent symbol pairs?",
            "type": "mcq",
            "options": ["Byte-Pair Encoding (BPE)", "TF-IDF Bag-of-Words", "Continuous Bag-of-Words (CBOW)", "One-Hot Representation"],
            "correct": "Byte-Pair Encoding (BPE)",
            "model_ans": None, "rubric": None,
            "explanation": "Byte-Pair Encoding (BPE) iteratively merges the most frequently co-occurring pairs of characters or token strings until reaching target vocabulary size.",
            "diff": "easy", "marks": 2.0, "topic_idx": 0,
            "excerpt": "Byte-Pair Encoding (BPE) iteratively merges the most frequent pairs of adjacent characters or character sequences until reaching a pre-set vocabulary size $V$."
        },
        {
            "text": "In Low-Rank Adaptation (LoRA), how is a dense weight matrix update $\\Delta W \\in \\mathbb{R}^{d \\times k}$ decomposed using rank $r \\ll \\min(d, k)$?",
            "type": "mcq",
            "options": ["$\\Delta W = A \\otimes B$", "$\\Delta W = \\frac{\\alpha}{r} BA$ where $B \\in \\mathbb{R}^{d \\times r}$ and $A \\in \\mathbb{R}^{r \\times k}$", "$\\Delta W = W_0^{-1} \\cdot (A + B)$", "$\\Delta W = \\text{softmax}(BA)$"],
            "correct": "$\\Delta W = \\frac{\\alpha}{r} BA$ where $B \\in \\mathbb{R}^{d \\times r}$ and $A \\in \\mathbb{R}^{r \\times k}$",
            "model_ans": None, "rubric": None,
            "explanation": "LoRA freezes original weight $W_0$ and parameterizes the update via low-rank matrices: $W = W_0 + \\frac{\\alpha}{r}BA$.",
            "diff": "medium", "marks": 2.0, "topic_idx": 5,
            "excerpt": "Low-Rank Adaptation (LoRA) freezes pretrained weight $W_0$ and injects trainable rank decomposition matrices $A \\in \\mathbb{R}^{r \\times k}$ and $B \\in \\mathbb{R}^{d \\times r}$ with rank $r \\ll \\min(d, k)$."
        },
        {
            "text": "What is the primary architectural difference between BERT and GPT foundational language models?",
            "type": "mcq",
            "options": ["BERT is an autoregressive decoder, while GPT is an encoder-decoder", "BERT uses bidirectional self-attention with masked LM, while GPT uses causal masked self-attention for next-token prediction", "BERT uses recurrent LSTM units, while GPT uses self-attention", "BERT cannot be fine-tuned with PEFT"],
            "correct": "BERT uses bidirectional self-attention with masked LM, while GPT uses causal masked self-attention for next-token prediction",
            "model_ans": None, "rubric": None,
            "explanation": "BERT is an encoder utilizing bidirectional context via Masked Language Modeling (MLM), whereas GPT is a causal decoder predicting autoregressively.",
            "diff": "easy", "marks": 2.0, "topic_idx": 4,
            "excerpt": "BERT employs Masked Language Modeling (MLM), predicting randomly masked tokens (15% probability) using bidirectional context. Autoregressive Causal Language Models optimize next-token prediction using unilateral causal masking."
        },
        {
            "text": "Which metric is most commonly utilized in vector databases to measure the semantic similarity between normalized query and document embeddings?",
            "type": "mcq",
            "options": ["Levenshtein edit distance", "Cosine similarity", "Jaccard similarity coefficient", "Hamming distance"],
            "correct": "Cosine similarity",
            "model_ans": None, "rubric": None,
            "explanation": "Cosine similarity computes $\\frac{u \\cdot v}{\\|u\\| \\|v\\|}$, measuring the cosine of the angle between high-dimensional dense embedding vectors.",
            "diff": "easy", "marks": 2.0, "topic_idx": 7,
            "excerpt": "Cosine similarity measures relevance: $\\text{sim}(u, v) = \\frac{u \\cdot v}{\\|u\\| \\|v\\|}$. Retrieved context is injected into the LLM system prompt."
        },
        # 2 Short Answers (5M each = 10M)
        {
            "text": "Formulate the Direct Preference Optimization (DPO) objective and explain how it eliminates the requirement for training a separate reinforcement learning reward model.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "Direct Preference Optimization (DPO) leverages an analytical mapping between the Bradley-Terry preference model and optimal policy $\\pi^*$. Under KL-constrained RLHF, the optimal reward can be expressed directly as $R(x, y) = \\beta \\log \\frac{\\pi_\\theta(y \\mid x)}{\\pi_{ref}(y \\mid x)}$. Substituting this into the pairwise preference likelihood yields the DPO objective:\n$$\\mathcal{L}_{DPO}(\\theta) = -\\mathbb{E}_{(x, y_w, y_l)} \\left[ \\log \\sigma \\left( \\beta \\log \\frac{\\pi_\\theta(y_w \\mid x)}{\\pi_{ref}(y_w \\mid x)} - \\beta \\log \\frac{\\pi_\\theta(y_l \\mid x)}{\\pi_{ref}(y_l \\mid x)} \\right) \\right]$$\nThis converts the complex PPO actor-critic loop into a stable, closed-form binary cross-entropy loss directly on paired preferences without training or maintaining a separate reward network.",
            "rubric": [
                {"criterion": "Mathematical statement of DPO loss formulation", "marks": 2.0},
                {"criterion": "Derivation relating reward to log-ratio of policy over reference model", "marks": 1.5},
                {"criterion": "Elimination of PPO actor-critic instability and reward drift", "marks": 1.5}
            ],
            "explanation": "Explains DPO mathematical foundation and alignment advantages over traditional PPO-based RLHF.",
            "diff": "hard", "marks": 5.0, "topic_idx": 6,
            "excerpt": "Direct Preference Optimization (DPO) algebraically bypasses the reward model, optimizing policy directly on paired preferences $(y_w \\succ y_l)$."
        },
        {
            "text": "Explain how Rotary Position Embedding (RoPE) injects positional information into Transformer key and query vectors, and compare it with absolute sinusoidal encodings.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "Traditional Transformer architectures add an absolute positional encoding vector to input token embeddings ($x_i + PE_i$). However, this fails to natively encode relative token offsets $m - n$. Rotary Position Embedding (RoPE) resolves this by applying a rotation matrix $R_{\\Theta, m}^d$ directly to 2D sub-vectors of queries and keys: $q_m = R_m q$, $k_n = R_n k$. Because rotation preserves inner product properties, the attention dot product $(R_m q)^T (R_n k) = q^T R_{n-m} k$ depends exclusively on the relative distance $m - n$, dramatically improving length generalization during long-context inference.",
            "rubric": [
                {"criterion": "Contrast between additive absolute encoding and multiplicative rotation", "marks": 2.0},
                {"criterion": "Mathematical rotation operator $R_{n-m}$ encoding relative distance", "marks": 2.0},
                {"criterion": "Advantage for long-context length extrapolation", "marks": 1.0}
            ],
            "explanation": "Analyzes modern position embedding techniques used in contemporary foundation models.",
            "diff": "medium", "marks": 5.0, "topic_idx": 3,
            "excerpt": "Modern foundation models (e.g., LLaMA) adopt Rotary Position Embeddings (RoPE), rotating key and query vectors in complex planes to preserve relative token distances."
        },
        # 1 Long Answer (10M)
        {
            "text": "Design an enterprise-grade Retrieval-Augmented Generation (RAG) system capable of answering technical queries over massive unstructured documentation with strict hallucination mitigation. Detail document chunking, dense retrieval, reranking, and generation verification.",
            "type": "long_answer", "options": None, "correct": None,
            "model_ans": "An enterprise-grade RAG system architecture comprises four coordinated pipelines:\n\n1. Ingestion and Semantic Chunking:\nRaw PDFs and manuals are parsed with layout-aware extractors. Instead of fixed token slicing, semantic chunking groups coherent sub-sections (300-500 tokens) with 50-token sliding overlap, preserving table structures and hierarchical headings.\n\n2. Hybrid Multi-Stage Retrieval:\nQuery text is converted into dense vectors via dual-encoder embeddings and simultaneously tokenized for BM25 sparse lexical search. Dense retrieval (using HNSW graph index on cosine similarity) captures semantic intent, while sparse BM25 preserves exact part numbers and acronyms. Results are combined using Reciprocal Rank Fusion (RRF).\n\n3. Cross-Encoder Reranking:\nThe top 50 candidates pass through a cross-encoder reranker (e.g., BGE-Reranker) that scores full (query, document) joint attention, selecting the top 5 highest-relevance passages.\n\n4. Grounded Generation and Verification Loop:\nThe LLM system prompt is constrained to answer strictly based on provided excerpts, citing bracketed document IDs. A secondary lightweight model evaluates attribution by verifying that each generated claim is directly entailment-supported by source context, rejecting ungrounded hallucinated claims.",
            "rubric": [
                {"criterion": "Semantic chunking strategy with structural preservation", "marks": 2.5},
                {"criterion": "Hybrid dense (HNSW) + sparse (BM25) search with RRF fusion", "marks": 2.5},
                {"criterion": "Cross-encoder reranking stage for high-precision filtering", "marks": 2.5},
                {"criterion": "Hallucination mitigation via citation and entailment verification", "marks": 2.5}
            ],
            "explanation": "Comprehensive production RAG system design covering chunking, hybrid search, reranking, and hallucination guardrails.",
            "diff": "hard", "marks": 10.0, "topic_idx": 7,
            "excerpt": "RAG systems mitigate hallucination by anchoring generation to factual enterprise knowledge. Documents are chunked, converted into dense vectors via neural embedding models, and indexed in high-dimensional vector databases using Approximate Nearest Neighbor (ANN) search."
        }
    ],

    "CY-201": [
        # 5 MCQs (2M each = 10M)
        {
            "text": "Under Shannon's definition of perfect secrecy, which condition is both necessary and sufficient for a symmetric cipher?",
            "type": "mcq",
            "options": ["The key space must be equal to or greater than the message space, and each key must be used only once with uniform distribution", "The ciphertext length must equal twice the plaintext length", "The cipher must employ at least 16 rounds of Feistel permutations", "The encryption algorithm must utilize modular exponentiation"],
            "correct": "The key space must be equal to or greater than the message space, and each key must be used only once with uniform distribution",
            "model_ans": None, "rubric": None,
            "explanation": "Shannon proved that perfect secrecy requires key entropy $H(K) \\ge H(M)$, which is uniquely satisfied by the One-Time Pad.",
            "diff": "medium", "marks": 2.0, "topic_idx": 0,
            "excerpt": "Claude Shannon established information-theoretic security: a cipher achieves perfect secrecy if and only if $P(M = m \\mid C = c) = P(M = m)$, exemplified exclusively by the One-Time Pad where key entropy equals or exceeds message entropy."
        },
        {
            "text": "Which operation in the Advanced Encryption Standard (AES) round transformation provides non-linear confusion?",
            "type": "mcq",
            "options": ["SubBytes using the non-linear S-box", "ShiftRows cyclical permutation", "MixColumns matrix multiplication", "AddRoundKey XOR operation"],
            "correct": "SubBytes using the non-linear S-box",
            "model_ans": None, "rubric": None,
            "explanation": "SubBytes is the sole non-linear step in AES, utilizing multiplicative inverses over Galois Field $GF(2^8)$ followed by an affine transformation.",
            "diff": "easy", "marks": 2.0, "topic_idx": 1,
            "excerpt": "Each round executes SubBytes (non-linear S-box), ShiftRows (cyclical byte permutation), MixColumns (matrix multiplication in $GF(2^8)$), and AddRoundKey."
        },
        {
            "text": "In the Diffie-Hellman key exchange protocol over public prime $p$ and generator $g$, what is the shared secret negotiated between Alice ($a$) and Bob ($b$)?",
            "type": "mcq",
            "options": ["$K = g^{a+b} \\pmod p$", "$K = g^{ab} \\pmod p$", "$K = (g^a + g^b) \\pmod p$", "$K = g^{a/b} \\pmod p$"],
            "correct": "$K = g^{ab} \\pmod p$",
            "model_ans": None, "rubric": None,
            "explanation": "Alice computes $(g^b)^a = g^{ba} = g^{ab} \\pmod p$, and Bob computes $(g^a)^b = g^{ab} \\pmod p$.",
            "diff": "easy", "marks": 2.0, "topic_idx": 2,
            "excerpt": "Their shared secret is $K = B^a \\pmod p = A^b \\pmod p = g^{ab} \\pmod p$. Security relies on the intractability of the Computational Diffie-Hellman (CDH) problem."
        },
        {
            "text": "According to the Birthday Attack on an $n$-bit cryptographic hash function, approximately how many random hash evaluations are required to find a collision with 50% probability?",
            "type": "mcq",
            "options": ["$\\mathcal{O}(2^n)$", "$\\mathcal{O}(2^{n/2})$", "$\\mathcal{O}(n^2)$", "$\\mathcal{O}(\\log_2 n)$"],
            "correct": "$\\mathcal{O}(2^{n/2})$",
            "model_ans": None, "rubric": None,
            "explanation": "By the Birthday Paradox, finding any collision between two arbitrary inputs requires approximately $\\sqrt{2^n} = 2^{n/2}$ evaluations.",
            "diff": "medium", "marks": 2.0, "topic_idx": 4,
            "excerpt": "Collision resistance (finding any $x \\neq y$ such that $H(x) = H(y)$ requires $\\mathcal{O}(2^{n/2})$ evaluations via the Birthday Attack)."
        },
        {
            "text": "Which major architectural update was introduced in the TLS 1.3 protocol handshake to improve connection latency and security?",
            "type": "mcq",
            "options": ["Retaining static RSA key transport for backward compatibility", "Reducing the standard handshake to 1-RTT and mandating ephemeral Diffie-Hellman for Perfect Forward Secrecy", "Adding DES and RC4 ciphers to default suites", "Requiring a mandatory 3-RTT negotiation phase"],
            "correct": "Reducing the standard handshake to 1-RTT and mandating ephemeral Diffie-Hellman for Perfect Forward Secrecy",
            "model_ans": None, "rubric": None,
            "explanation": "TLS 1.3 deprecated static RSA key exchange, mandated Ephemeral Diffie-Hellman (PFS), and streamlined handshake latency to 1-RTT.",
            "diff": "easy", "marks": 2.0, "topic_idx": 6,
            "excerpt": "Transport Layer Security (TLS 1.3) streamlines the cryptographic handshake to 1 Round-Trip Time (1-RTT). It deprecates insecure cipher suites, mandates Ephemeral Diffie-Hellman (ECDHE) for Perfect Forward Secrecy (PFS)."
        },
        # 2 Short Answers (5M each = 10M)
        {
            "text": "Explain how the RSA cryptosystem generates public and private keypairs and demonstrate why decryption $m \\equiv c^d \\pmod n$ correctly recovers the original plaintext.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "RSA key generation proceeds as follows:\n1. Choose two large distinct primes $p$ and $q$. Compute modulus $n = pq$ and Euler totient $\\phi(n) = (p-1)(q-1)$.\n2. Select public exponent $e$ such that $1 < e < \\phi(n)$ and $\\gcd(e, \\phi(n)) = 1$.\n3. Compute private exponent $d \\equiv e^{-1} \\pmod{\\phi(n)}$ using the Extended Euclidean Algorithm ($e \\cdot d = 1 + k\\phi(n)$).\n\nDecryption proof: Ciphertext $c \\equiv m^e \\pmod n$. Then $c^d \\equiv (m^e)^d = m^{ed} = m^{1 + k\\phi(n)} \\pmod n$. By Euler's Theorem ($m^{\\phi(n)} \\equiv 1 \\pmod n$ for $\\gcd(m, n) = 1$), $m^{1 + k\\phi(n)} = m \\cdot (m^{\\phi(n)})^k \\equiv m \\cdot 1^k = m \\pmod n$.",
            "rubric": [
                {"criterion": "Key generation steps (modulus $n$, totient $\\phi(n)$, exponents $e, d$)", "marks": 2.0},
                {"criterion": "Mathematical derivation using Euler's theorem $m^{\\phi(n)} \\equiv 1 \\pmod n$", "marks": 2.0},
                {"criterion": "Condition on prime selection and coprimality", "marks": 1.0}
            ],
            "explanation": "Demonstrates RSA key generation and rigorous correctness proof based on number theory.",
            "diff": "medium", "marks": 5.0, "topic_idx": 3,
            "excerpt": "RSA relies on integer factorization hardness. Choose large primes $p, q$, compute modulus $n = pq$ and Euler totient $\\phi(n) = (p-1)(q-1)$. Select public exponent $e$ such that $\\gcd(e, \\phi(n)) = 1$, and compute private key $d \\equiv e^{-1} \\pmod{\\phi(n)}$."
        },
        {
            "text": "Distinguish between Transport Mode and Tunnel Mode in IPsec Encapsulating Security Payload (ESP). When is each mode utilized in network architectures?",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "In IPsec ESP:\n1. Transport Mode: Encrypts only the IP payload (transport layer segments like TCP/UDP) while keeping the original IP packet header intact and unencrypted. It is utilized primarily for end-to-end host-to-host communications across an existing trusted network.\n2. Tunnel Mode: Encrypts the entire original IP packet (both header and payload) and prepends a brand new outer IP header. It is the standard protocol for site-to-site Virtual Private Networks (VPNs) and gateway-to-gateway tunnels, concealing internal network topology and IP addressing schemes from external adversaries.",
            "rubric": [
                {"criterion": "Transport Mode mechanics and host-to-host use case", "marks": 2.0},
                {"criterion": "Tunnel Mode encapsulation (new outer IP header) and VPN use case", "marks": 2.0},
                {"criterion": "Privacy and topology-hiding benefits comparison", "marks": 1.0}
            ],
            "explanation": "Compares IPsec packet encapsulation modes and their security architectures.",
            "diff": "medium", "marks": 5.0, "topic_idx": 7,
            "excerpt": "IPsec secures network layer packets using Authentication Header (AH) and Encapsulating Security Payload (ESP, confidentiality and integrity) in transport or tunnel modes."
        },
        # 1 Long Answer (10M)
        {
            "text": "Design an enterprise Zero Trust Network Architecture (ZTNA) implementing Mutual TLS (mTLS), micro-segmentation, and OAuth 2.0 / OpenID Connect token validation. Explain how this architecture defends against lateral movement during credential compromise.",
            "type": "long_answer", "options": None, "correct": None,
            "model_ans": "An enterprise Zero Trust Network Architecture enforces the fundamental tenet 'Never trust, always verify':\n\n1. Cryptographic Identity and Mutual TLS (mTLS):\nEvery microservice and client is issued an X.509 certificate managed by an automated internal Public Key Infrastructure (such as HashiCorp Vault or SPIFFE/SPIRE). All inter-service communications mandate mTLS using TLS 1.3, authenticating both client and server identities and encrypting data-in-transit with ephemeral key exchange.\n\n2. Centralized Authentication & Authorization via OAuth 2.0 / OIDC:\nUsers authenticate against an enterprise Identity Provider (IdP) supporting Multi-Factor Authentication (MFA), receiving cryptographically signed JSON Web Tokens (JWT / OIDC ID tokens). A Policy Decision Point (PDP) evaluates continuous risk signals (device posture, IP geolocation, user roles) before minting short-lived scoped access tokens.\n\n3. Micro-segmentation and Policy Enforcement:\nNetwork perimeters are replaced with container-level service meshes (e.g., Istio). Ingress Sidecar proxies act as Policy Enforcement Points (PEPs), validating JWT signatures and enforcing granular Layer-7 AuthorizationPolicies (e.g., Service A can only invoke `GET /orders`, not `DELETE /orders`).\n\n4. Lateral Movement Defense:\nIf an adversary compromises an internal service, they cannot execute lateral scans or pivot across subnets: unauthenticated TCP traffic is rejected at kernel level, tokens cannot be forged without the IdP private key, and short token lifespans (15 mins) prevent replay attacks.",
            "rubric": [
                {"criterion": "mTLS X.509 identity lifecycle and service-to-service encryption", "marks": 2.5},
                {"criterion": "OAuth 2.0 / OIDC PDP and PEP token validation mechanics", "marks": 2.5},
                {"criterion": "Micro-segmentation via service mesh sidecars and L7 policy rules", "marks": 2.5},
                {"criterion": "Defense-in-depth analysis mitigating lateral movement and token replay", "marks": 2.5}
            ],
            "explanation": "Comprehensive security architecture detailing zero-trust identity, mTLS, and lateral movement mitigations.",
            "diff": "hard", "marks": 10.0, "topic_idx": 7,
            "excerpt": "Zero Trust Network Architecture enforces the principle of 'never trust, always verify', utilizing micro-segmentation, mutual TLS (mTLS), and centralized identity validation (OAuth 2.0 / OIDC tokens)."
        }
    ],

    "DS-202": [
        # 5 MCQs (2M each = 10M)
        {
            "text": "What is the maximum allowed balance factor difference in an AVL tree before a rebalancing rotation is triggered?",
            "type": "mcq",
            "options": ["$BF \\in \\{-1, 0, +1\\}$", "$BF \\in \\{-2, +2\\}$", "$BF \\in \\{0, 1, 2\\}$", "$BF \\le \\log_2 N$"],
            "correct": "$BF \\in \\{-1, 0, +1\\}$",
            "model_ans": None, "rubric": None,
            "explanation": "An AVL tree maintains height balance such that the balance factor $|\\text{height}(L) - \\text{height}(R)| \\le 1$ for every node.",
            "diff": "easy", "marks": 2.0, "topic_idx": 0,
            "excerpt": "An AVL tree is a strictly height-balanced binary search tree where the balance factor $BF = \\text{height}(\\text{left}) - \\text{height}(\\text{right}) \\in \\{-1, 0, +1\\}$ for every node."
        },
        {
            "text": "What is the amortized time complexity of the `decrease-key` operation in a Fibonacci Heap?",
            "type": "mcq",
            "options": ["$\\mathcal{O}(1)$", "$\\mathcal{O}(\\log N)$", "$\\mathcal{O}(N)$", "$\\mathcal{O}(\\log \\log N)$"],
            "correct": "$\\mathcal{O}(1)$",
            "model_ans": None, "rubric": None,
            "explanation": "Using cascading cuts and potential functions, Fibonacci Heaps achieve amortized $\\mathcal{O}(1)$ for `decrease-key`.",
            "diff": "medium", "marks": 2.0, "topic_idx": 2,
            "excerpt": "Fibonacci Heaps achieve amortized $\\mathcal{O}(1)$ time for `insert`, `minimum`, `union`, and `decrease-key`, with `delete-min` taking amortized $\\mathcal{O}(\\log N)$."
        },
        {
            "text": "When Disjoint Set Union (DSU) employs both Union by Rank and Path Compression, what is the amortized time complexity per operation for $N$ elements?",
            "type": "mcq",
            "options": ["$\\mathcal{O}(\\alpha(N))$ where $\\alpha$ is the inverse Ackermann function", "$\\mathcal{O}(\\log N)$", "$\\mathcal{O}(1)$ worst-case", "$\\mathcal{O}(\\sqrt{N})$"],
            "correct": "$\\mathcal{O}(\\alpha(N))$ where $\\alpha$ is the inverse Ackermann function",
            "model_ans": None, "rubric": None,
            "explanation": "Path compression combined with union by rank guarantees nearly linear $\\mathcal{O}(\\alpha(N))$ time, where $\\alpha(N) \\le 4$ for all practical values.",
            "diff": "medium", "marks": 2.0, "topic_idx": 4,
            "excerpt": "Combining Union by Rank with Path Compression achieves an amortized operational time of $\\mathcal{O}(\\alpha(N))$, where $\\alpha$ is the inverse Ackermann function."
        },
        {
            "text": "What is the upper bound time complexity of the Edmonds-Karp algorithm for computing maximum network flow on graph $G = (V, E)$?",
            "type": "mcq",
            "options": ["$\\mathcal{O}(V \\cdot E^2)$", "$\\mathcal{O}(E \\log V)$", "$\\mathcal{O}(V^2 \\cdot E)$", "$\\mathcal{O}(V^3)$"],
            "correct": "$\\mathcal{O}(V \\cdot E^2)$",
            "model_ans": None, "rubric": None,
            "explanation": "Edmonds-Karp uses Breadth-First Search (BFS) to find the shortest augmenting path, yielding a polynomial runtime of $\\mathcal{O}(V \\cdot E^2)$.",
            "diff": "easy", "marks": 2.0, "topic_idx": 5,
            "excerpt": "The Edmonds-Karp algorithm implements the Ford-Fulkerson method by selecting the shortest augmenting path using Breadth-First Search (BFS), strictly bounding time complexity to $\\mathcal{O}(V \\cdot E^2)$."
        },
        {
            "text": "In the Knuth-Morris-Pratt (KMP) string matching algorithm, what does the prefix array $\\pi[i]$ represent?",
            "type": "mcq",
            "options": ["The length of the longest proper prefix of $P[0 \\dots i]$ that is also a suffix of $P[0 \\dots i]$", "The number of distinct characters in the pattern", "The hash value of the pattern prefix", "The index of the next vowel in the pattern"],
            "correct": "The length of the longest proper prefix of $P[0 \\dots i]$ that is also a suffix of $P[0 \\dots i]$",
            "model_ans": None, "rubric": None,
            "explanation": "The KMP $\\pi$ table stores the length of the longest proper prefix matching a suffix, allowing the algorithm to bypass re-examining characters.",
            "diff": "easy", "marks": 2.0, "topic_idx": 6,
            "excerpt": "The KMP algorithm performs linear-time string matching in $\\mathcal{O}(N + M)$ by preprocessing pattern string $P$ into a longest proper prefix which is also a suffix ($\\pi$ array)."
        },
        # 2 Short Answers (5M each = 10M)
        {
            "text": "State the five structural invariants of a Red-Black Tree and explain why these properties guarantee that the tree height is bounded by $2 \\log_2(N + 1)$.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "The five Red-Black tree invariants are:\n1. Every node is colored either red or black.\n2. The root node is black.\n3. Every leaf node (NIL) is black.\n4. If a node is red, both its children must be black (no adjacent red nodes).\n5. For each node, every simple path to descendant leaves contains the same number of black nodes (black-height $bh$).\n\nHeight bound proof: By induction, any subtree rooted at node $x$ contains at least $2^{bh(x)} - 1$ internal nodes. Since property 4 dictates that at most half of the nodes on any path can be red, the black-height $bh \\ge h/2$. Therefore, $N \\ge 2^{h/2} - 1$, which algebraically implies $h \\le 2 \\log_2(N + 1)$.",
            "rubric": [
                {"criterion": "Listing of all 5 red-black properties", "marks": 2.5},
                {"criterion": "Black-height inductive proof showing $N \\ge 2^{bh} - 1$", "marks": 1.5},
                {"criterion": "Derivation of $h \\le 2 \\log_2(N + 1)$", "marks": 1.0}
            ],
            "explanation": "Rigorous explanation of red-black tree color properties and logarithmic height proof.",
            "diff": "medium", "marks": 5.0, "topic_idx": 1,
            "excerpt": "A Red-Black tree is a self-balancing BST satisfying five properties: (1) Every node is red or black, (2) The root is black, (3) Every leaf (NIL) is black, (4) If a node is red, both its children are black, (5) Every simple path from a node to descendant leaves contains identical numbers of black nodes."
        },
        {
            "text": "State the Max-Flow Min-Cut Theorem and explain how an optimal minimum $s$-$t$ cut can be extracted from a residual network after the maximum flow algorithm terminates.",
            "type": "short_answer", "options": None, "correct": None,
            "model_ans": "The Max-Flow Min-Cut Theorem states that the maximum amount of flow from source $s$ to sink $t$ in a flow network is equal to the net capacity of the minimum capacity $s$-$t$ cut.\n\nExtracting the minimum cut:\n1. Run Ford-Fulkerson or Edmonds-Karp until no augmenting paths exist in residual graph $G_f$.\n2. Perform a graph traversal (BFS or DFS) starting from source node $s$ along edges with strictly positive residual capacity ($c_f(u, v) > 0$).\n3. Define set $S$ as all vertices reachable from $s$ in $G_f$, and set $T = V \\setminus S$ as all unreachable vertices.\n4. The cut $(S, T)$ forms the minimal capacity cut, whose capacity exactly matches the maximum flow value.",
            "rubric": [
                {"criterion": "Clear statement of Max-Flow Min-Cut equivalence", "marks": 2.0},
                {"criterion": "Residual graph reachability traversal from source $s$", "marks": 2.0},
                {"criterion": "Identification of saturated cross-boundary edges as min-cut", "marks": 1.0}
            ],
            "explanation": "Covers network flow duality and exact algorithmic procedure for identifying minimal cuts.",
            "diff": "medium", "marks": 5.0, "topic_idx": 5,
            "excerpt": "The Max-Flow Min-Cut Theorem proves that the maximum amount of flow passing from source $s$ to sink $t$ equals the minimum capacity among all $s$-$t$ cuts."
        },
        # 1 Long Answer (10M)
        {
            "text": "Analyze the potential method of amortized analysis as applied to Fibonacci Heaps. Prove why the cascading cut mechanism ensures that `decrease-key` runs in $\\mathcal{O}(1)$ amortized time while bounding maximum node degree.",
            "type": "long_answer", "options": None, "correct": None,
            "model_ans": "Amortized Analysis of Fibonacci Heaps using the Potential Method:\n\n1. Potential Function Definition:\nLet $t(H)$ denote the number of trees in the root list of heap $H$, and $m(H)$ denote the number of marked nodes (nodes that have lost a child since being made a child of their current parent). The potential function is:\n$$\\Phi(H) = t(H) + 2 m(H)$$\n\n2. Mechanics of `decrease-key`:\nWhen decreasing key of node $x$, if the min-heap property is violated with parent $y$, node $x$ is cut from $y$ and added to the root list. If parent $y$ was unmarked, it is marked ($m(H)$ increases by 1). If $y$ was already marked, a cascading cut is triggered: $y$ is cut and moved to root list, and its parent is checked recursively until reaching an unmarked ancestor or the root.\n\n3. Amortized Cost Calculation:\nSuppose a `decrease-key` operation causes $c$ cascading cuts. The actual work is $\\mathcal{O}(c)$. The new state has $t(H) + c$ trees and at most $m(H) - c + 1$ marked nodes (since $c$ nodes become unmarked root trees, and at most 1 ancestor becomes marked). The change in potential is:\n$$\\Delta \\Phi \\le (t(H) + c + 2(m(H) - c + 1)) - (t(H) + 2m(H)) = c - 2c + 2 = 2 - c$$\nAmortized cost $\\hat{c} = c_{actual} + \\Delta \\Phi = \\mathcal{O}(c) + (2 - c) = \\mathcal{O}(1)$.\n\n4. Bounding Node Degree:\nBecause a node loses at most one child before being cut, a subtree of degree $k$ has size at least $F_{k+2}$ (the $(k+2)$-th Fibonacci number). Since Fibonacci numbers grow exponentially ($F_k \\approx \\phi^k$), the maximum degree of any node with $N$ elements is strictly bounded by $\\mathcal{O}(\\log N)$, guaranteeing that subsequent `delete-min` operations run in $\\mathcal{O}(\\log N)$ amortized time.",
            "rubric": [
                {"criterion": "Potential function definition $\\Phi = t(H) + 2m(H)$", "marks": 2.5},
                {"criterion": "Cascading cut execution and marked node logic", "marks": 2.5},
                {"criterion": "Mathematical cancellation showing $\\Delta \\Phi = 2 - c$ yielding $\\mathcal{O}(1)$", "marks": 2.5},
                {"criterion": "Exponential Fibonacci subtree size and $\\mathcal{O}(\\log N)$ degree bound proof", "marks": 2.5}
            ],
            "explanation": "Rigorous mathematical proof of Fibonacci heap amortized bounds via potential functions and cascading cuts.",
            "diff": "hard", "marks": 10.0, "topic_idx": 2,
            "excerpt": "Cascading cuts prevent trees from becoming excessively deep: when a non-root node loses a second child, it is immediately cut from its parent and moved to the root list. This yields Dijkstra's shortest path time complexity of $\\mathcal{O}(E + V \\log V)$."
        }
    ]
}

# ==============================================================================
# READY-TO-PUBLISH DRAFT PAPERS CONFIGURATION (5 PAPERS)
# ==============================================================================

READY_TO_PUBLISH_PAPERS = [
    {
        "id": "paper_its401_cav_draft",
        "title": "ITS-401 Connected & Autonomous Mobility Final Paper (Ready to Publish)",
        "subject_id": "ITS-401",
        "duration_minutes": 60,
        "total_marks": 30.0,
        "instructions": "1. All questions are compulsory.\n2. Figures to the right indicate full marks.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        "blueprint_json": {
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        }
    },
    {
        "id": "paper_cs301_midterm_draft",
        "title": "CS-301 Distributed Systems Mid-Semester Exam (Ready to Publish)",
        "subject_id": "CS-301",
        "duration_minutes": 60,
        "total_marks": 30.0,
        "instructions": "1. All questions are compulsory.\n2. Write structured, mathematically grounded answers.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        "blueprint_json": {
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        }
    },
    {
        "id": "paper_ai402_quiz_draft",
        "title": "AI-402 Transformer Architectures & LLM Evaluation (Ready to Publish)",
        "subject_id": "AI-402",
        "duration_minutes": 60,
        "total_marks": 30.0,
        "instructions": "1. All questions are compulsory.\n2. State mathematical formulations where applicable.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        "blueprint_json": {
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        }
    },
    {
        "id": "paper_cy201_assessment_draft",
        "title": "CY-201 Cryptography & Network Security Assessment (Ready to Publish)",
        "subject_id": "CY-201",
        "duration_minutes": 60,
        "total_marks": 30.0,
        "instructions": "1. All questions are compulsory.\n2. Show cryptographic derivations and protocol flows.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        "blueprint_json": {
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        }
    },
    {
        "id": "paper_ds202_final_draft",
        "title": "DS-202 Advanced Data Structures & Algorithms Evaluation (Ready to Publish)",
        "subject_id": "DS-202",
        "duration_minutes": 60,
        "total_marks": 30.0,
        "instructions": "1. All questions are compulsory.\n2. State time complexities and amortized proofs.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        "blueprint_json": {
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        }
    }
]

# ==============================================================================
# SEED DATABASE MAIN FUNCTION
# ==============================================================================

def seed_database(db: Session, force: bool = False):
    """
    Deterministically seeds the database with 5 subjects, curriculum documents,
    approved questions, ready-to-publish draft papers, and sample student attempts.
    """
    seed_record = db.query(DemoSeedVersion).first()
    if seed_record and not force:
        return

    if force:
        db.query(Response).delete()
        db.query(AttemptItem).delete()
        db.query(Attempt).delete()
        db.query(PaperItem).delete()
        db.query(PaperSection).delete()
        db.query(Paper).delete()
        db.query(QuestionSetItem).delete()
        db.query(QuestionSet).delete()
        db.query(SourceEvidence).delete()
        db.query(QuestionRevision).delete()
        db.query(Question).delete()
        db.query(DocumentContent).delete()
        db.query(Document).delete()
        db.query(Topic).delete()
        db.query(Subject).delete()
        db.query(DemoUser).delete()
        db.query(Notification).delete()
        db.query(DemoSeedVersion).delete()
        db.commit()

    # 1. Demo Users
    prof = DemoUser(
        id="prof_sharma",
        name="Dr. R. Sharma",
        role="faculty",
        email="r.sharma@college.edu",
        department="Computer Science & Engineering",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    )
    student1 = DemoUser(
        id="student_aditi",
        name="Aditi Rao",
        role="student",
        email="aditi.cs21@college.edu",
        department="Computer Science & Engineering",
        avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150"
    )
    student2 = DemoUser(
        id="student_karthik",
        name="Karthik Nair",
        role="student",
        email="karthik.cs21@college.edu",
        department="Computer Science & Engineering",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    )
    db.add_all([prof, student1, student2])
    db.flush()

    # Maps to track created entities
    created_subjects: Dict[str, Subject] = {}
    created_topics_by_subject: Dict[str, List[Topic]] = {}
    created_docs_by_subject: Dict[str, Document] = {}
    saved_revisions_by_subject: Dict[str, List[QuestionRevision]] = {}

    # 2. Seed All 5 Subjects, Topics & Curriculum Documents
    for sub_conf in SUBJECTS_CONFIG:
        sub = Subject(
            id=sub_conf["id"],
            code=sub_conf["code"],
            name=sub_conf["name"],
            description=sub_conf["description"]
        )
        db.add(sub)
        db.flush()
        created_subjects[sub.id] = sub

        # Topics
        topics_list = []
        for u_num, u_name, t_name, desc in sub_conf["topics"]:
            t = Topic(
                subject_id=sub.id,
                unit_number=u_num,
                unit_name=u_name,
                topic_name=t_name,
                description=desc
            )
            db.add(t)
            topics_list.append(t)
        db.flush()
        created_topics_by_subject[sub.id] = topics_list

        # Document
        doc = Document(
            id=sub_conf["doc_id"],
            title=sub_conf["doc_title"],
            subject_id=sub.id,
            unit_number=1,
            original_filename=sub_conf["doc_file"],
            safe_filename=f"{sub_conf['id'].lower()}_lecture_notes_demo.pdf",
            file_type="pdf",
            file_size=len(sub_conf["doc_text"].encode("utf-8")),
            extraction_status="completed",
            detected_headings=sub_conf["headings"],
            is_demo_seed=True
        )
        db.add(doc)
        db.flush()
        created_docs_by_subject[sub.id] = doc

        doc_content = DocumentContent(
            document_id=doc.id,
            full_text=sub_conf["doc_text"],
            page_count=6,
            cleaned_text=sub_conf["doc_text"],
            topics_json=[t.topic_name for t in topics_list]
        )
        db.add(doc_content)
        db.flush()

    # 3. Seed Questions for Each Subject
    for sub_id, questions_data in SEED_QUESTIONS_BY_SUBJECT.items():
        doc = created_docs_by_subject[sub_id]
        topics = created_topics_by_subject[sub_id]
        saved_revs = []

        for idx, q_info in enumerate(questions_data):
            q_id = f"q_{sub_id.lower().replace('-', '_')}_{idx+1:02d}"
            q_obj = Question(
                id=q_id,
                subject_id=sub_id,
                status="approved",
                is_active=True,
                is_demo_seed=True
            )
            db.add(q_obj)
            db.flush()

            rev_id = f"{q_id}_v1"
            q_obj.current_revision_id = rev_id

            matched_topic = topics[q_info["topic_idx"]] if q_info["topic_idx"] < len(topics) else topics[0]

            rev = QuestionRevision(
                id=rev_id,
                question_id=q_id,
                revision_number=1,
                question_text=q_info["text"],
                question_type=q_info["type"],
                options_json=q_info.get("options"),
                correct_answer=q_info.get("correct"),
                model_answer=q_info.get("model_ans"),
                rubric_json=q_info.get("rubric"),
                explanation=q_info.get("explanation"),
                difficulty=q_info["diff"],
                marks=q_info["marks"],
                topic_id=matched_topic.id,
                topic_name=matched_topic.topic_name,
                unit_number=matched_topic.unit_number,
                source_document_id=doc.id,
                source_document_title=doc.title,
                supporting_excerpt=q_info["excerpt"],
                verified_grounding=True,
                approved_by=prof.id,
                approved_at=datetime.datetime.utcnow(),
                is_current=True
            )
            db.add(rev)
            db.flush()

            # Source evidence
            ev = SourceEvidence(
                revision_id=rev.id,
                document_id=doc.id,
                document_title=doc.title,
                excerpt=q_info["excerpt"],
                match_confidence=1.0,
                verified_grounding=True
            )
            db.add(ev)
            saved_revs.append(rev)

        saved_revisions_by_subject[sub_id] = saved_revs

    db.flush()

    # 4. Seeded Published Paper: ITS-401 Mid-Term Examination 2026
    its_revs = saved_revisions_by_subject["ITS-401"]
    published_paper = Paper(
        id="paper_its_midterm_2026",
        title="ITS-401 Mid-Term Examination 2026",
        subject_id="ITS-401",
        status="published",
        duration_minutes=60,
        total_marks=30.0,
        instructions="1. All questions are compulsory.\n2. Figures to the right indicate full marks.\n3. Section A carries 10 marks (5 MCQs x 2M).\n4. Section B carries 10 marks (2 Short Answers x 5M).\n5. Section C carries 10 marks (1 Long Answer x 10M).",
        blueprint_json={
            "target_marks": 30.0,
            "duration_minutes": 60,
            "difficulty_target": {"easy": 40, "medium": 40, "hard": 20},
            "type_target": {"mcq": 5, "short_answer": 2, "long_answer": 1},
            "required_units": [1, 2, 3, 4]
        },
        warnings_acknowledged=True,
        is_demo_seed=True,
        published_at=datetime.datetime.utcnow() - datetime.timedelta(days=2)
    )
    db.add(published_paper)
    db.flush()

    # Published Paper Sections
    p_sec_a = PaperSection(
        id="p_sec_a_midterm",
        paper_id=published_paper.id,
        name="Section A: Multiple Choice Questions",
        description="Answer all questions. Each carries 2 marks.",
        section_order=1,
        total_marks=10.0,
        instructions="Select the single correct alternative."
    )
    p_sec_b = PaperSection(
        id="p_sec_b_midterm",
        paper_id=published_paper.id,
        name="Section B: Short Answer Questions",
        description="Answer both questions concisely.",
        section_order=2,
        total_marks=10.0,
        instructions="Provide structured, technical answers."
    )
    p_sec_c = PaperSection(
        id="p_sec_c_midterm",
        paper_id=published_paper.id,
        name="Section C: Long Answer / System Analysis",
        description="Detailed analytical and architectural evaluation.",
        section_order=3,
        total_marks=10.0,
        instructions="Answer in depth with system architecture block diagrams."
    )
    db.add_all([p_sec_a, p_sec_b, p_sec_c])
    db.flush()

    # Allocated items for Published Paper
    mcq_revs = [r for r in its_revs if r.question_type == "mcq"][:5]
    for i, r in enumerate(mcq_revs):
        db.add(PaperItem(
            id=f"pi_midterm_a_{i+1}",
            paper_id=published_paper.id,
            section_id=p_sec_a.id,
            question_revision_id=r.id,
            item_order=i+1,
            marks=2.0
        ))

    short_revs = [r for r in its_revs if r.question_type == "short_answer"][:2]
    for i, r in enumerate(short_revs):
        db.add(PaperItem(
            id=f"pi_midterm_b_{i+1}",
            paper_id=published_paper.id,
            section_id=p_sec_b.id,
            question_revision_id=r.id,
            item_order=len(mcq_revs) + i + 1,
            marks=5.0
        ))

    long_revs = [r for r in its_revs if r.question_type == "long_answer"][:1]
    if long_revs:
        db.add(PaperItem(
            id="pi_midterm_c_1",
            paper_id=published_paper.id,
            section_id=p_sec_c.id,
            question_revision_id=long_revs[0].id,
            item_order=len(mcq_revs) + len(short_revs) + 1,
            marks=10.0
        ))
    db.flush()

    # 5. Seed 5 Ready-To-Publish Draft Papers Across All 5 Subjects
    for paper_conf in READY_TO_PUBLISH_PAPERS:
        sub_id = paper_conf["subject_id"]
        sub_revs = saved_revisions_by_subject[sub_id]

        draft_paper = Paper(
            id=paper_conf["id"],
            title=paper_conf["title"],
            subject_id=sub_id,
            status="draft",
            duration_minutes=paper_conf["duration_minutes"],
            total_marks=paper_conf["total_marks"],
            instructions=paper_conf["instructions"],
            blueprint_json=paper_conf["blueprint_json"],
            warnings_acknowledged=True, # Pre-acknowledged so paper is 100% publication-ready
            is_demo_seed=True
        )
        db.add(draft_paper)
        db.flush()

        # Create sections
        sec_a = PaperSection(
            id=f"sec_a_{paper_conf['id']}",
            paper_id=draft_paper.id,
            name="Section A: Multiple Choice Questions",
            description="Answer all questions. Each carries 2 marks.",
            section_order=1,
            total_marks=10.0,
            instructions="Select the single correct alternative."
        )
        sec_b = PaperSection(
            id=f"sec_b_{paper_conf['id']}",
            paper_id=draft_paper.id,
            name="Section B: Technical Analytical Questions",
            description="Answer concise descriptive questions.",
            section_order=2,
            total_marks=10.0,
            instructions="Provide concise explanations and mathematical formulations."
        )
        sec_c = PaperSection(
            id=f"sec_c_{paper_conf['id']}",
            paper_id=draft_paper.id,
            name="Section C: Comprehensive System Design",
            description="Detailed analytical and architectural problem.",
            section_order=3,
            total_marks=10.0,
            instructions="Provide in-depth architectural analysis and proof."
        )
        db.add_all([sec_a, sec_b, sec_c])
        db.flush()

        # Allocate 5 MCQs (10M)
        p_mcqs = [r for r in sub_revs if r.question_type == "mcq"][:5]
        for i, r in enumerate(p_mcqs):
            db.add(PaperItem(
                id=f"pi_{paper_conf['id']}_a_{i+1}",
                paper_id=draft_paper.id,
                section_id=sec_a.id,
                question_revision_id=r.id,
                item_order=i+1,
                marks=2.0
            ))

        # Allocate 2 Short Answers (10M)
        p_shorts = [r for r in sub_revs if r.question_type == "short_answer"][:2]
        for i, r in enumerate(p_shorts):
            db.add(PaperItem(
                id=f"pi_{paper_conf['id']}_b_{i+1}",
                paper_id=draft_paper.id,
                section_id=sec_b.id,
                question_revision_id=r.id,
                item_order=len(p_mcqs) + i + 1,
                marks=5.0
            ))

        # Allocate 1 Long Answer (10M)
        p_longs = [r for r in sub_revs if r.question_type == "long_answer"][:1]
        if p_longs:
            db.add(PaperItem(
                id=f"pi_{paper_conf['id']}_c_1",
                paper_id=draft_paper.id,
                section_id=sec_c.id,
                question_revision_id=p_longs[0].id,
                item_order=len(p_mcqs) + len(p_shorts) + 1,
                marks=10.0
            ))

    db.flush()

    # 6. Seed Student Attempts (Linked to Published Paper)
    # Attempt 1: Fully Graded (Student: Aditi Rao)
    att1 = Attempt(
        id="att_seed_aditi_graded",
        student_id=student1.id,
        paper_id=published_paper.id,
        title="ITS-401 Mid-Term Examination 2026",
        subject_id="ITS-401",
        mode="assessment",
        status="graded",
        started_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=3),
        deadline_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=2),
        submitted_at=datetime.datetime.utcnow() - datetime.timedelta(days=1, hours=2, minutes=10),
        graded_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5),
        total_possible_marks=30.0,
        objective_score=8.0,
        provisional_score=26.0,
        final_score=26.0,
        is_demo_seed=True
    )
    db.add(att1)
    db.flush()

    all_paper_items = db.query(PaperItem).filter(PaperItem.paper_id == published_paper.id).order_by(PaperItem.item_order).all()
    for item in all_paper_items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == item.question_revision_id).first()
        snapshot = {
            "question_text": rev.question_text,
            "question_type": rev.question_type,
            "options": rev.options_json,
            "marks": item.marks,
            "topic_name": rev.topic_name,
            "unit_number": rev.unit_number,
            "correct_answer": rev.correct_answer,
            "model_answer": rev.model_answer,
            "rubric_json": rev.rubric_json,
            "explanation": rev.explanation
        }
        db.add(AttemptItem(
            attempt_id=att1.id,
            question_revision_id=rev.id,
            order_index=item.item_order,
            marks_allocated=item.marks,
            question_snapshot_json=snapshot
        ))

        if rev.question_type == "mcq":
            is_corr = (item.item_order != 2)
            ans = rev.correct_answer if is_corr else "Microwave radar sensors"
            db.add(Response(
                id=f"resp_att1_{item.item_order}",
                attempt_id=att1.id,
                question_revision_id=rev.id,
                submitted_answer=ans,
                is_correct=is_corr,
                marks_awarded=2.0 if is_corr else 0.0,
                grading_status="auto_graded",
                graded_at=att1.submitted_at
            ))
        elif rev.question_type == "short_answer":
            db.add(Response(
                id=f"resp_att1_{item.item_order}",
                attempt_id=att1.id,
                question_revision_id=rev.id,
                submitted_answer="The national ITS architecture integrates physical sensors (loops, radars) communicating with TMCs via logical software pipelines. Telemetry allows algorithms to continuously adjust signals.",
                is_correct=True,
                marks_awarded=4.5,
                grading_status="manually_graded",
                faculty_feedback="Solid understanding of architecture layers and telemetry loops. Well explained.",
                grader_id=prof.id,
                graded_at=att1.graded_at
            ))
        elif rev.question_type == "long_answer":
            db.add(Response(
                id=f"resp_att1_{item.item_order}",
                attempt_id=att1.id,
                question_revision_id=rev.id,
                submitted_answer="Cooperative Adaptive Cruise Control (CACC) combines radar sensing with real-time V2V telemetry (acceleration, braking commands) to permit heavy vehicles to travel in tightly coupled platoons with sub-second following gaps, dramatically reducing aerodynamic drag and highway congestion.",
                is_correct=True,
                marks_awarded=9.0,
                grading_status="manually_graded",
                faculty_feedback="Excellent depth on string stability and longitudinal control algorithms.",
                grader_id=prof.id,
                graded_at=att1.graded_at
            ))

    # Attempt 2: Submitted & Awaiting Faculty Grading (Student: Karthik Nair)
    att2 = Attempt(
        id="att_seed_karthik_pending",
        student_id=student2.id,
        paper_id=published_paper.id,
        title="ITS-401 Mid-Term Examination 2026",
        subject_id="ITS-401",
        mode="assessment",
        status="awaiting_grading",
        started_at=datetime.datetime.utcnow() - datetime.timedelta(hours=4),
        deadline_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3),
        submitted_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3, minutes=15),
        total_possible_marks=30.0,
        objective_score=10.0,
        provisional_score=10.0,
        final_score=None,
        is_demo_seed=True
    )
    db.add(att2)
    db.flush()

    for item in all_paper_items:
        rev = db.query(QuestionRevision).filter(QuestionRevision.id == item.question_revision_id).first()
        snapshot = {
            "question_text": rev.question_text,
            "question_type": rev.question_type,
            "options": rev.options_json,
            "marks": item.marks,
            "topic_name": rev.topic_name,
            "unit_number": rev.unit_number,
            "correct_answer": rev.correct_answer,
            "model_answer": rev.model_answer,
            "rubric_json": rev.rubric_json,
            "explanation": rev.explanation
        }
        db.add(AttemptItem(
            attempt_id=att2.id,
            question_revision_id=rev.id,
            order_index=item.item_order,
            marks_allocated=item.marks,
            question_snapshot_json=snapshot
        ))

        if rev.question_type == "mcq":
            db.add(Response(
                id=f"resp_att2_{item.item_order}",
                attempt_id=att2.id,
                question_revision_id=rev.id,
                submitted_answer=rev.correct_answer,
                is_correct=True,
                marks_awarded=2.0,
                grading_status="auto_graded",
                graded_at=att2.submitted_at
            ))
        else:
            db.add(Response(
                id=f"resp_att2_{item.item_order}",
                attempt_id=att2.id,
                question_revision_id=rev.id,
                submitted_answer="DSRC uses IEEE 802.11p at 5.9GHz while C-V2X uses 3GPP cellular standard with PC5 direct sidelink.",
                is_correct=None,
                marks_awarded=None,
                grading_status="pending"
            ))

    # 7. Notifications
    db.add(Notification(
        role="faculty",
        title="Grading Queue: 1 Submission Pending",
        message="Karthik Nair has submitted 'ITS-401 Mid-Term Examination 2026' with 3 descriptive answers awaiting evaluation.",
        link=f"/faculty/grading/{att2.id}"
    ))
    db.add(Notification(
        user_id=student1.id,
        role="student",
        title="Mid-Term Results Published",
        message="Your submission for 'ITS-401 Mid-Term Examination 2026' has been graded. Total Score: 26 / 30.",
        link=f"/student/attempt/{att1.id}/results"
    ))

    # 8. Record Demo Seed Version
    db.add(DemoSeedVersion(
        version="2.0.0",
        description="Expanded seed with 5 subjects (ITS-401, CS-301, AI-402, CY-201, DS-202), comprehensive curriculum notes, 40 approved questions, 5 ready-to-publish draft papers, and sample student attempts."
    ))

    db.commit()

def reset_demo_workspace(db: Session):
    """
    Resets the demo workspace to its initial seeded state while preserving configuration.
    """
    seed_database(db, force=True)
