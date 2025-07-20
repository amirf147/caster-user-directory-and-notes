# test_backend.py
from pyautogui_backend import IWindowBackend, PyAutoGUIBackend, create_window_backend
import time

def test_backend_creation():
    """Test that we can create a PyAutoGUI backend"""
    # Direct instantiation
    backend1 = PyAutoGUIBackend()
    assert isinstance(backend1, IWindowBackend)
    print("✓ Direct instantiation works")
    
    # Factory creation
    backend2 = create_window_backend("pyautogui")
    assert isinstance(backend2, IWindowBackend)
    print("✓ Factory creation works")

def test_window_operations():
    """Test basic window operations (requires at least one window open)"""
    backend = PyAutoGUIBackend()
    
    # Get all windows
    windows = backend.get_all_windows()
    print(f"✓ Found {len(windows)} windows")
    
    if windows:
        # Test getting window title
        first_window = windows[0]
        title = backend.get_window_title(first_window)
        print(f"✓ First window title: {title}")
        
        # Test finding window by title
        found = backend.find_window_by_title(title[:5], exact_match=False)
        assert found is not None