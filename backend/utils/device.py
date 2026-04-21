import torch


def get_device() -> torch.device:
    """Detect the best available compute device: CUDA → MPS (Apple Silicon) → CPU."""
    if torch.cuda.is_available():
        return torch.device("cuda")
    # MPS requires PyTorch 1.12+ and macOS 12.3+
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


DEVICE: torch.device = get_device()
