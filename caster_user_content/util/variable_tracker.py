# Currently just does the environment variables file
# TODO: Generalize to other files

import os
import json
import ast
from pathlib import Path
from caster_user_content import environment_variables as ev

class VariableTracker:
    def __init__(self, env_file_path):
        self.env_file_path = Path(env_file_path)
        self.var_positions = {}
        self._load_or_scan()
    
    def _load_or_scan(self):
        """Load positions from cache or scan the file"""
        cache_file = self.env_file_path.parent / '.var_positions.json'
        if cache_file.exists() and cache_file.stat().st_mtime > self.env_file_path.stat().st_mtime:
            with open(cache_file, 'r') as f:
                self.var_positions = json.load(f)
        else:
            self.scan_file()
    
    def scan_file(self):
        """Scan the file and update variable positions"""
        self.var_positions = {}
        with open(self.env_file_path, 'r') as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    var_name = line.split('=')[0].strip()
                    if var_name and var_name.isupper() and all(c.isalnum() or c == '_' for c in var_name):
                        self.var_positions[var_name] = i
        
        # Save to cache
        cache_file = self.env_file_path.parent / '.var_positions.json'
        with open(cache_file, 'w') as f:
            json.dump(self.var_positions, f)
    
    def get_line_number(self, var_name):
        """Get line number for a variable"""
        return self.var_positions.get(var_name)

# Initialize with your environment variables file
var_tracker = VariableTracker(ev.ENVIRONMENT_FILE)