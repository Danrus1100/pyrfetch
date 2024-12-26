import unittest
import time
import timeit
from typing import Tuple
from pathlib import Path
import sys
import platform

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pyrfetch import SystemInfo

class TestOSDetection(unittest.TestCase):
    def setUp(self):
        self.sysinfo = SystemInfo()
        self.iterations = 1000
    
    def test_os_name_accuracy(self):
        """Test if get_os_name returns valid distribution name"""
        os_name = self.sysinfo.get_os_name()
        valid_distros = [
            "Arch", "Gentoo", "Ubuntu", "Fedora", "Kali", "macOS",
            "Debian", "Mint", "Pop", "Manjaro", "Endeavour", 
            "OpenSUSE", "RedHat", "Zorin", "Default"
        ]
        self.assertIn(os_name, valid_distros)

    def test_os_detection_performance(self):
        """Compare performance of os-release reading vs platform"""
        # Time the current implementation
        os_release_time = timeit.timeit(
            lambda: self.sysinfo.get_os_name(),
            number=self.iterations
        )

        # Time alternative platform-based implementation 
        platform_time = timeit.timeit(
            lambda: "macOS" if platform.system() == "Darwin" else "Default",
            number=self.iterations
        )

        print(f"\nPerformance over {self.iterations} iterations:")
        print(f"os-release method: {os_release_time:.4f} seconds")
        print(f"platform method: {platform_time:.4f} seconds")
        print(f"Improvement: {((os_release_time - platform_time) / os_release_time) * 100:.2f}%")
        
        # Store results for comparison
        self.assertIsInstance(os_release_time, float)
        self.assertIsInstance(platform_time, float)

    def test_os_name_consistency(self):
        """Test if get_os_name returns consistent results"""
        first_result = self.sysinfo.get_os_name()
        for _ in range(5):
            self.assertEqual(
                self.sysinfo.get_os_name(),
                first_result,
                "OS detection should return consistent results"
            )

if __name__ == '__main__':
    unittest.main(verbosity=2)