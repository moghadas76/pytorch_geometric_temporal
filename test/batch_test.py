import numpy as np
import networkx as nx

from torch_geometric_temporal.signal import temporal_signal_split

from torch_geometric_temporal.signal import StaticGraphTemporalSignalBatch
from torch_geometric_temporal.signal import DynamicGraphTemporalSignalBatch
from torch_geometric_temporal.signal import DynamicGraphStaticSignalBatch

def get_edge_array(node_count):
    return np.array([edge for edge in nx.gnp_random_graph(node_count, 0.1).edges()]).T

def generate_signal(snapshot_count, node_count, feature_count):
    edge_indices = [get_edge_array(node_count) for _ in range(snapshot_count)]
    edge_weights = [np.ones(edge_indices[t].shape[1]) for t in range(snapshot_count)]
    features = [np.random.uniform(0, 1, (node_count, feature_count)) for _ in range(snapshot_count)]
    return edge_indices, edge_weights, features
    
def generate_batch_data(node_count, snapshot_count, feature_count, batch_size):
    edges = []
    edge_weights = []
    features = []
    targets = []
    batch_index = []
    for _ in range(batch_size):
        x = 2

