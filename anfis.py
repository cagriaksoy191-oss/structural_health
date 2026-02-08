import torch
import torch.nn as nn

class ANFIS(nn.Module):
    def __init__(self, n_inputs, n_rules):
        super(ANFIS, self).__init__()
        self.n_inputs = n_inputs
        self.n_rules = n_rules
        self.c = nn.Parameter(torch.randn(n_rules, n_inputs))
        self.sigma = nn.Parameter(torch.abs(torch.randn(n_rules, n_inputs)) + 0.1)
        self.consequent_weights = nn.Parameter(torch.randn(n_rules, n_inputs))
        self.consequent_bias = nn.Parameter(torch.randn(n_rules, 1))

    def forward(self, x):
        x_expanded = x.unsqueeze(1) 
        membership = torch.exp(-0.5 * ((x_expanded - self.c) / self.sigma) ** 2)
        w = torch.prod(membership, dim=2, keepdim=True)
        w_sum = torch.sum(w, dim=1, keepdim=True)
        w_norm = w / (w_sum + 1e-8)
        rule_output = (x_expanded * self.consequent_weights.unsqueeze(0)).sum(dim=2, keepdim=True) + self.consequent_bias.unsqueeze(0)
        weighted_output = w_norm * rule_output
        final_output = torch.sum(weighted_output, dim=1)
        return final_output
