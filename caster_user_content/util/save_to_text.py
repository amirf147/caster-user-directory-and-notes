from tkinter import simpledialog, Tk
import sys
import os
from datetime import datetime
import tkinter as tk
import argparse

def create_window(always_on_top=False):
    root = tk.Tk()
    root.title("Save Job Posting")
    if always_on_top:
        root.attributes('-topmost', True)  # This makes the window stay on top
    root.withdraw()
    
    custom_name = simpledialog.askstring("Save Text", 
                                       "Enter a name for the file (leave blank for timestamp):")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{custom_name or timestamp}.txt"
    filepath = os.path.join(save_path, filename)
    
    with open(filepath, 'wb') as f:
        f.write(content.encode('utf-8'))
        
    print(f"Successfully saved to: {filename}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('save_path', help='Path to save the text file')
    parser.add_argument('--always-on-top', action='store_true', help='Keep window always on top')
    args = parser.parse_args()
    
    create_window(always_on_top=args.always_on_top)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Save path required")
        sys.exit(1)
        
    save_path = sys.argv[1]
    content = sys.stdin.read()
    main()