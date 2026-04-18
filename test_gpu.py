import sys
import time
import importlib

def test_gpu():
    print("=" * 50)
    print("[ HARDWARE ACCELERATION DIAGNOSTIC ]")
    print("=" * 50)
    
    # Check PyTorch (powers YOLOv11)
    try:
        import torch
        print(f"\n[PyTorch - YOLOv11 Engine]")
        print(f"Version installed: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"[*] CUDA Acceleration: ONLINE")
            print(f"[*] Active GPU: {torch.cuda.get_device_name(0)}")
            
            # Run a small tensor math test
            start = time.time()
            x = torch.rand(10000, 10000).cuda()
            y = torch.rand(10000, 10000).cuda()
            z = torch.matmul(x, y)
            end = time.time()
            print(f"[*] 100 Million Tensor Mults completed in: {(end-start)*1000:.2f}ms")
        else:
            print(f"[!] CUDA Acceleration: OFFLINE (Running on CPU)")
    except ImportError:
        print("\n[PyTorch - YOLOv11 Engine] - Not Installed")

    # Check TensorFlow (powers DeepFace)
    try:
        import tensorflow as tf
        print(f"\n[TensorFlow - DeepFace Engine]")
        print(f"Version installed: {tf.__version__}")
        
        gpus = tf.config.list_physical_devices('GPU')
        if gpus:
            print(f"[*] GPU Acceleration: ONLINE")
            for gpu in gpus:
                print(f"   - {gpu.name}")
        else:
            print(f"[!] GPU Acceleration: OFFLINE (Running on CPU)")
            print("   Note: TF 2.11+ dropped native Windows GPU support without WSL2.")
    except ImportError:
        print("\n[TensorFlow - DeepFace Engine] - Not Installed")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_gpu()
