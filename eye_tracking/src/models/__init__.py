import importlib

import torch
from omegaconf import DictConfig

from .resnet_preact import Model


def create_model(config: DictConfig) -> torch.nn.Module:
    model = Model(config)

    device = torch.device(config.device)
    model.to(device)
    return model
