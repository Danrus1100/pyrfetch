import unittest
from unittest.mock import patch, MagicMock
import subprocess
import shutil 
from functools import lru_cache
import timeit

@lru_cache(maxsize=1)
def get_gpu_info() -> str:
    """Get GPU information with optimized detection and error handling."""
    if shutil.which("nvidia-smi"):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                stdout=subprocess.PIPE,
                text=True,
                check=True,
                timeout=2
            )
            if result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            pass

    try:
        result = subprocess.run(
            ["lspci"],
            stdout=subprocess.PIPE,
            text=True,
            check=True,
            timeout=2
        )
        
        gpu_identifiers = ["VGA compatible controller", "3D controller"]
        
        for line in result.stdout.splitlines():
            if any(identifier in line for identifier in gpu_identifiers):
                parts = line.split(":", 2)
                if len(parts) >= 3:
                    return parts[2].strip()
                
        return "Integrated Graphics"
        
    except (subprocess.SubprocessError, subprocess.TimeoutExpired):
        return "N/A"

class TestGPUInfo(unittest.TestCase):
    def setUp(self):
        # Clear cache before each test
        get_gpu_info.cache_clear()

    @patch('subprocess.run')
    @patch('shutil.which')
    def test_nvidia_gpu_detection(self, mock_which, mock_run):
        # Configure mocks
        mock_which.return_value = True
        mock_process = MagicMock()
        mock_process.stdout = "NVIDIA GeForce RTX 3080\n"
        mock_process.returncode = 0
        mock_run.return_value = mock_process

        # Test
        result = get_gpu_info()
        
        # Verify
        self.assertEqual(result, "NVIDIA GeForce RTX 3080")
        mock_which.assert_called_once_with("nvidia-smi")
        mock_run.assert_called_once()

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_nvidia_gpu_detection(self, mock_run, mock_which):
        mock_which.return_value = True
        mock_run.return_value = MagicMock(stdout="NVIDIA GeForce RTX 3080\n", returncode=0)
        self.assertEqual(get_gpu_info(), "NVIDIA GeForce RTX 3080")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_lspci_fallback(self, mock_run, mock_which):
        mock_which.return_value = False
        mock_run.return_value = MagicMock(
            stdout="00:02.0 VGA compatible controller: Intel Corporation UHD Graphics 630\n",
            returncode=0
        )
        self.assertEqual(get_gpu_info(), "Intel Corporation UHD Graphics 630")

    @patch('shutil.which')
    @patch('subprocess.run')
    def test_error_handling(self, mock_run, mock_which):
        mock_which.return_value = True
        mock_run.side_effect = subprocess.SubprocessError()
        self.assertEqual(get_gpu_info(), "N/A")

    def test_performance(self):
        get_gpu_info.cache_clear()
        
        start_time = timeit.default_timer()
        first_call = get_gpu_info()
        first_time = timeit.default_timer() - start_time
        
        start_time = timeit.default_timer()
        second_call = get_gpu_info()
        second_time = timeit.default_timer() - start_time
        
        print(f"First call time: {first_time:.4f}s")
        print(f"Cached call time: {second_time:.4f}s")
        
        self.assertLess(second_time, first_time)
        self.assertEqual(first_call, second_call)

if __name__ == '__main__':
    # Run the function
    print(f"Detected GPU: {get_gpu_info()}")
    
    # Run tests
    unittest.main(argv=[''], exit=False)