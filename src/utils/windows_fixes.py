import os
import sys
import ctypes
import winreg

def fix_win32_unicode():
    """Fix Unicode handling in Windows console"""
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
        os.environ["PYTHONIOENCODING"] = "utf-8"

def enable_long_paths():
    """Enable long path support (>260 chars) on Windows"""
    if sys.platform != 'win32':
        return
    
    
    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\FileSystem",
            0, winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, "LongPathsEnabled", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)
    except Exception as e:
        print(f"Couldn't enable long paths: {str(e)}")
    
    
    if hasattr(ctypes, 'windll'):
        ctypes.windll.kernel32.SetDllDirectoryW(None)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        if hasattr(kernel32, 'SetFileApisToOEM'):
            kernel32.SetFileApisToOEM()