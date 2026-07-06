from dragonfly import MappingRule, Function
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
import traceback

def check_uia_status():
    print("--- Starting Direct UIA Test ---")
    
    try:
        # Move the import inside the function to prevent silent startup crashes
        print("[UIA Test] Attempting to import UIA module...")
        from dragonfly.accessibility import uia
        
        # 1. Instantiate the raw UIA backend controller directly
        os_controller = uia.Controller()
        os_controller.start()
        print("[UIA Test] Raw UIA thread started successfully.")
        
        # 2. Define the code to execute safely on the background thread
        def inspect_focus(context):
            focused_element = context.focused
            if not focused_element:
                return "[UIA Test] No focused element found by Windows UIA."
            
            if not focused_element.is_editable():
                return "[UIA Test] Focused element is not editable."
                
            text_node = focused_element.as_text()
            if not text_node:
                return "[UIA Test] Element does not expose a UIA Text Pattern."
                
            return (f"--- UIA Buffer Dump ---\n"
                    f"Current Cursor Index: {text_node.cursor}\n"
                    f"Full Text Extracted:\n{text_node.expanded_text}\n"
                    f"-----------------------")
        
        # 3. Call it through the raw backend thread runner
        result = os_controller.run_sync(inspect_focus)
        print(result)
        
        # 4. Clean up the background thread
        os_controller.stop()
        
    except Exception as e:
        print("[UIA Test] Direct UIA test failed. Error details:")
        traceback.print_exc()

class UiaDiagnosticRule(MappingRule):
    mapping = {
        "test bridge": Function(check_uia_status),
    }

def get_rule():
    details = RuleDetails(name="UIA Diagnostic")
    return UiaDiagnosticRule, details