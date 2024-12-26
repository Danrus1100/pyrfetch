import timeit
import unittest
import sys
from functools import lru_cache
import subprocess
import platform
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pyrfetch import SystemInfo

get_cpu_info_original = SystemInfo().get_cpu_info

@lru_cache(maxsize=1)  # Cache the result since CPU info rarely changes
def get_cpu_info():
    """Get CPU information with optimized reading and proper error handling."""
    
    # System-specific optimized paths
    if platform.system() == "Darwin":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=1  # Add timeout
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass

    # Linux path - optimized file reading
    try:
        with open("/proc/cpuinfo", "r") as f:
            # Read only until we find what we need
            for line in f:
                if line.startswith("model name"):
                    return line.split(":", 1)[1].strip()
            
            # If we get here, we didn't find the model name
            return "Unknown CPU"
                
    except (IOError, OSError):
        return "Unknown CPU"

    return "Unknown CPU"
    

class TestCPUInfo(unittest.TestCase):
    def test_performance(self):
        orig_time = timeit.timeit(lambda: get_cpu_info_original(), number=1000)
        opt_time = timeit.timeit(lambda: get_cpu_info(), number=1000)
        
        print(f"Original version: {orig_time:.4f} seconds")
        print(f"Optimized version: {opt_time:.4f} seconds")
        print(f"Improvement: {((orig_time - opt_time) / orig_time) * 100:.2f}%")
        
        self.assertLess(opt_time, orig_time)

if __name__ == '__main__':
    unittest.main()