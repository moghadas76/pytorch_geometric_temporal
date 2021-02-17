import torch
from torch_geometric.nn import GCNConv


class TGCN(torch.nn.Module):
    r"""An implementation of the Temporal Graph Convolutional Gated Recurrent Cell.
    For details see this paper: `"Structured Sequence Modeling with Graph
    Convolutional Recurrent Networks." <https://arxiv.org/abs/1612.07659>`_

    Args:
        in_channels (int): Number of input features.
        out_channels (int): Number of output features.
    """
    def __init__(self, in_channels: int, out_channels: int):
        super(TGCN, self).__init__()

        self.in_channels = in_channels
        self.out_channels = out_channels
        self._create_parameters_and_layers()


    def _create_update_gate_parameters_and_layers(self):

        self.conv_z = GCNConv(in_channels=self.in_channels,
                              out_channels=self.out_channels)
                                        
        self.linear_z = torch.nn.linear(in_channels=2*self.out_channels,
                                        out_channels=self.out_channels)


    def _create_reset_gate_parameters_and_layers(self):

        self.conv_r = GCNConv(in_channels=self.in_channels,
                              out_channels=self.out_channels)
                                        
        self.linear_r = torch.nn.linear(in_channels=2*self.out_channels,
                                        out_channels=self.out_channels)

    def _create_candidate_state_parameters_and_layers(self):

        self.conv_h = GCNConv(in_channels=self.in_channels,
                              out_channels=self.out_channels)
                                        
        self.linear_h = torch.nn.linear(in_channels=2*self.out_channels,
                                        out_channels=self.out_channels)


    def _create_parameters_and_layers(self):
        self._create_update_gate_parameters_and_layers()
        self._create_reset_gate_parameters_and_layers()
        self._create_candidate_state_parameters_and_layers()


    def _set_hidden_state(self, X, H):
        if H is None:
            H = torch.zeros(X.shape[0], self.out_channels).to(X.device)
        return H


    def _calculate_update_gate(self, X, edge_index, edge_weight, H):
        Z = torch.cat([self.conv_z(X, edge_index, edge_weight), H],axis=1)
        Z = self.linear_z(Z)
        Z = torch.sigmoid(Z)
        return Z


    def _calculate_reset_gate(self, X, edge_index, edge_weight, H):
        R = torch.cat([self.conv_r(X, edge_index, edge_weight), H],axis=1)
        R = self.linear_r(R)
        R = torch.sigmoid(R)
        return R


    def _calculate_candidate_state(self, X, edge_index, edge_weight, H, R):
        H_tilde = torch.cat([self.conv_h(X, edge_index, edge_weight), H*R],axis=1)
        H_tilde = self.linear_h(H_tilde)
        H_tilde = torch.tanh(H_tilde)
        return H_tilde


    def _calculate_hidden_state(self, Z, H, H_tilde):
        H = Z*H + (1-Z)*H_tilde
        return H


    def forward(self, X: torch.FloatTensor, edge_index: torch.LongTensor,
                edge_weight: torch.FloatTensor=None, H: torch.FloatTensor=None) -> torch.FloatTensor:
        """
        Making a forward pass. If edge weights are not present the forward pass
        defaults to an unweighted graph. If the hidden state matrix is not present
        when the forward pass is called it is initialized with zeros.

        Arg types:
            * **X** *(PyTorch Float Tensor)* - Node features.
            * **edge_index** *(PyTorch Long Tensor)* - Graph edge indices.
            * **edge_weight** *(PyTorch Long Tensor, optional)* - Edge weight vector.
            * **H** *(PyTorch Float Tensor, optional)* - Hidden state matrix for all nodes.

        Return types:
            * **H** *(PyTorch Float Tensor)* - Hidden state matrix for all nodes.
        """
        H = self._set_hidden_state(X, H)
        Z = self._calculate_update_gate(X, edge_index, edge_weight, H)
        R = self._calculate_reset_gate(X, edge_index, edge_weight, H)
        H_tilde = self._calculate_candidate_state(X, edge_index, edge_weight, H, R)
        H = self._calculate_hidden_state(Z, H, H_tilde)
        return H
