from tkinter import simpledialog, Tk
import sys
import os
from datetime import datetime

def save_to_text(content, save_path):
    root = Tk()
    root.withdraw()
    
    custom_name = simpledialog.askstring("Save Text", 
                                       "Enter a name for the file (leave blank for timestamp):")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{custom_name or timestamp}.txt"
    filepath = os.path.join(save_path, filename)
    
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf-8'))
        
    print(f"Successfully saved to: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Save path required")
        sys.exit(1)
        
    save_path = sys.argv[1]
    content = sys.stdin.read()
    save_to_text(content, save_path)