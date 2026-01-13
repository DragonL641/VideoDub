"""Model selection logic for optimal Whisper model."""

import platform
import psutil
import torch


def select_optimal_model() -> str:
    """
    Automatically select the optimal Whisper model based on system resources.
    
    Returns:
        Model name string (e.g., 'small', 'medium')
    """
    system = platform.system().lower()
    memory_gb = psutil.virtual_memory().total / (1024.0**3)
    
    # Detect Apple Silicon (macOS)
    if system == "darwin" and platform.processor() == "arm":
        # M-series chips performance is sufficient, recommend small or medium
        return "small" if memory_gb < 8 else "medium"
    
    # Detect GPU (NVIDIA)
    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024.0**3)
        # Decide model based on VRAM
        if vram_gb > 10:
            return "large-v3"  # High precision for professional scenarios
        elif vram_gb > 5:
            return "medium"  # Balance precision and speed
        else:
            return "small"  # Speed and availability consideration
    
    # CPU and memory detection (Windows & macOS Intel)
    if memory_gb >= 8:
        return "small"  # Small model available with sufficient memory
    else:
        return "base"  # Lightweight model for limited memory


# Get recommended model
recommended_model = select_optimal_model()
print(f"Recommended model: {recommended_model}")