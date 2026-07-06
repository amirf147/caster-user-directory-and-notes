from dragonfly import MappingRule, Function, Dictation
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
import traceback

_GLOBAL_UIA_CONTROLLER = None

def get_stable_controller():
    """Lazily manages the single global UIA thread required by this branch layout."""
    global _GLOBAL_UIA_CONTROLLER
    if _GLOBAL_UIA_CONTROLLER is None:
        try:
            from dragonfly.accessibility import uia
            _GLOBAL_UIA_CONTROLLER = uia.Controller()
            _GLOBAL_UIA_CONTROLLER.start()
            print("[UIA System] Background thread initialized.")
        except Exception:
            traceback.print_exc()
    return _GLOBAL_UIA_CONTROLLER

def get_text_node(context):
    """Helper method to safely extract the text node interface from current focus context."""
    focused = context.focused
    if focused and focused.is_editable():
        return focused.as_text()
    return None

# ==========================================
# DIAGNOSTIC TESTING FUNCTIONS
# ==========================================

def read_buffer():
    """Tests if UIA can natively read the text buffer without clipboard scraping."""
    print("--- Testing: Read Entire Buffer ---")
    os_controller = get_stable_controller()
    if not os_controller: return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            return f"[UIA Success] Buffer Text:\n{text_node.expanded_text}"
        return "[UIA Failure] Active field is not an editable UIA text node."
    print(os_controller.run_sync(action))

def show_caret_position():
    """Tests if UIA can track the real-time character index of the text cursor."""
    print("--- Testing: Caret Index Tracking ---")
    os_controller = get_stable_controller()
    if not os_controller: return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            # Using the exact discovered property 'cursor'
            pos = text_node.cursor
            return f"[UIA Success] Caret Position (Character Index): {pos}"
        return "[UIA Failure] Active field is not an editable UIA text node."
    print(os_controller.run_sync(action))

def select_word_match(text):
    """Tests selecting a single instance of a dictated string."""
    search_str = str(text).lower().strip()
    print(f"--- Testing: Select Word Match '{search_str}' ---")
    os_controller = get_stable_controller()
    if not os_controller: return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            full_buffer_lower = text_node.expanded_text.lower()
            start_idx = full_buffer_lower.find(search_str)
            if start_idx != -1:
                text_node.select_range(start_idx, start_idx + len(search_str))
                return f"[UIA Success] Selected '{search_str}' at range ({start_idx}, {start_idx + len(search_str)})."
            return f"[UIA Warning] '{search_str}' not found in active buffer."
        return "[UIA Failure] Target unavailable."
    print(os_controller.run_sync(action))

def select_word_range(start_text, end_text):
    """Tests selecting a multi-word sequence between two anchor points."""
    start_str = str(start_text).lower().strip()
    end_str = str(end_text).lower().strip()
    print(f"--- Testing: Select Range '{start_str}' to '{end_str}' ---")
    os_controller = get_stable_controller()
    if not os_controller: return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            full_buffer_lower = text_node.expanded_text.lower()
            start_idx = full_buffer_lower.find(start_str)
            end_word_pos = full_buffer_lower.find(end_str, start_idx)
            
            if start_idx != -1 and end_word_pos != -1:
                end_idx = end_word_pos + len(end_str)
                text_node.select_range(start_idx, end_idx)
                return f"[UIA Success] Range highlighted across indices ({start_idx}, {end_idx})."
            return "[UIA Warning] Target text boundary anchors mismatch."
        return "[UIA Failure] Target unavailable."
    print(os_controller.run_sync(action))


# ==========================================
# GRAMMAR AND MAPPING CONFIGURATION
# ==========================================

class UiaDiagnosticRule(MappingRule):
    mapping = {
        "test read buffer": Function(read_buffer),
        "test caret position": Function(show_caret_position),
        "test select <text>": Function(select_word_match),
        "test select <start_text> to <end_text>": Function(select_word_range),
    }
    extras = [
        Dictation("text"),
        Dictation("start_text"),
        Dictation("end_text"),
    ]

def get_rule():
    details = RuleDetails(name="UIA Complete Diagnostic")
    get_stable_controller()
    return UiaDiagnosticRule, details