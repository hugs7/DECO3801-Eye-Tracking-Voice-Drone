from typing import Any

import torchvision.transforms as T


def create_transform() -> Any:
    return T.ToTensor()
