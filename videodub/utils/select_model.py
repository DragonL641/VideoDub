import platform
import psutil
import torch

def select_optimal_model():
    """
    自动选择最优的Whisper模型。
    返回: 模型名称字符串，如 'small', 'medium'
    """
    system = platform.system().lower()
    memory_gb = psutil.virtual_memory().total / (1024.**3) # 内存总量(GB)
    
    # 检测Apple Silicon (macOS)
    if system == "darwin" and platform.processor() == "arm":
        # M系列芯片性能足够，通常推荐small或medium模型以平衡速度与精度
        return "small" if memory_gb < 8 else "medium"
    
    # 检测GPU (NVIDIA)
    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024.**3)
        # 根据显存决定模型
        if vram_gb > 10:
            return "large-v3"       # 高精度专业场景
        elif vram_gb > 5:
            return "medium"        # 平衡精度与速度
        else:
            return "small"         # 兼顾速度与可用性
    
    # CPU和内存检测 (Windows & macOS Intel)
    if memory_gb >= 8:
        return "small"    # 内存充足可用small模型
    else:
        return "base"     # 内存有限则用更轻量模型

# 获取推荐模型
recommended_model = select_optimal_model()
print(f"为您推荐的模型是: {recommended_model}")