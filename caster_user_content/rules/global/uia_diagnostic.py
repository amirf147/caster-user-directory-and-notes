from dragonfly import MappingRule, Function, Dictation, Integer
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
    if not os_controller:
        return

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
    if not os_controller:
        return

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
    if not os_controller:
        return

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
    if not os_controller:
        return

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


def put_cursor_before(text):
    """Moves the caret to the start of the first match of the dictated text."""
    search_str = str(text).lower().strip()
    print(f"--- Testing: Put Cursor Before '{search_str}' ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            full_buffer_lower = text_node.expanded_text.lower()
            start_idx = full_buffer_lower.find(search_str)
            if start_idx != -1:
                text_node.set_cursor(start_idx)
                return f"[UIA Success] Placed cursor before '{search_str}' at index {start_idx}."
            return f"[UIA Warning] '{search_str}' not found in active buffer."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def put_cursor_after(text):
    """Moves the caret to the end of the first match of the dictated text."""
    search_str = str(text).lower().strip()
    print(f"--- Testing: Put Cursor After '{search_str}' ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            full_buffer_lower = text_node.expanded_text.lower()
            start_idx = full_buffer_lower.find(search_str)
            if start_idx != -1:
                end_idx = start_idx + len(search_str)
                text_node.set_cursor(end_idx)
                return f"[UIA Success] Placed cursor after '{search_str}' at index {end_idx}."
            return f"[UIA Warning] '{search_str}' not found in active buffer."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def get_char_at_cursor():
    """Prints the character at the current caret offset, with surrounding context."""
    print("--- Testing: Character at Caret ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            pos = text_node.cursor
            buffer = text_node.expanded_text
            length = len(buffer)

            char_at = buffer[pos] if 0 <= pos < length else "<EOF>"

            # Context window (up to 5 characters before and after)
            start = max(0, pos - 5)
            end = min(length, pos + 5)
            context_str = buffer[start:end]

            # Create a visual indicator showing where the caret is in the context
            rel_pos = pos - start
            visual_indicator = context_str[:rel_pos] + "|" + context_str[rel_pos:]

            return (
                f"[UIA Success] Caret index: {pos}\n"
                f"Character at index: {repr(char_at)}\n"
                f"Surrounding context: '{visual_indicator}'"
            )
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def set_cursor_at_index(n):
    """Moves the caret to the specified character offset."""
    idx = int(n)
    print(f"--- Testing: Set Cursor to Index {idx} ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            text_node.set_cursor(idx)
            return f"[UIA Success] Caret moved to offset {idx} (verified: {text_node.cursor})."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def select_range_indices(n_start, n_end):
    """Selects a text range based on start and end character offsets."""
    start = int(n_start)
    end = int(n_end)
    print(f"--- Testing: Select Indices ({start}, {end}) ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            text_node.select_range(start, end)
            return f"[UIA Success] Selected range ({start}, {end})."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def show_bounding_box_at_cursor():
    """Prints the bounding box coordinates of the character at the caret position."""
    print("--- Testing: Bounding Box at Cursor ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            pos = text_node.cursor
            try:
                box = text_node.get_bounding_box(pos)
                return f"[UIA Success] Caret bounding box at index {pos}: {box}"
            except Exception as e:
                return f"[UIA Error] Failed to get bounding box at index {pos}: {e}"
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def show_bounding_box_of_word(text):
    """Prints the bounding box coordinates of the specified word."""
    search_str = str(text).lower().strip()
    print(f"--- Testing: Bounding Box of '{search_str}' ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            full_buffer_lower = text_node.expanded_text.lower()
            start_idx = full_buffer_lower.find(search_str)
            if start_idx != -1:
                try:
                    box = text_node.get_bounding_box(start_idx)
                    return f"[UIA Success] Bounding box of '{search_str}' (start index {start_idx}): {box}"
                except Exception as e:
                    return f"[UIA Error] Failed to get bounding box: {e}"
            return f"[UIA Warning] '{search_str}' not found in active buffer."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def check_editable():
    """Tests if the current focused element is editable under UIA."""
    print("--- Testing: Is Focus Editable ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        focused = context.focused
        if focused:
            editable = focused.is_editable()
            control_type = getattr(focused._element, "CurrentControlType", None)
            return f"[UIA Success] Focused element: editable={editable}, control_type={control_type}"
        return "[UIA Failure] No element is currently focused."

    print(os_controller.run_sync(action))


# ==========================================
# GRAMMAR AND MAPPING CONFIGURATION
# ==========================================


class UiaDiagnosticRule(MappingRule):
    mapping = {
        "buffer read": Function(read_buffer),
        "caret read": Function(show_caret_position),
        "select <text>": Function(select_word_match),
        "select <start_text> to <end_text>": Function(select_word_range),
        "[put] cursor before <text>": Function(put_cursor_before),
        "[put] cursor after <text>": Function(put_cursor_after),
        "[put] cursor [at | to] <n>": Function(set_cursor_at_index),
        "select <n_start> [to | through] <n_end>": Function(select_range_indices),
        "caret character": Function(get_char_at_cursor),
        "caret bounds": Function(show_bounding_box_at_cursor),
        "bounds <text>": Function(show_bounding_box_of_word),
        "is editable": Function(check_editable),
    }
    extras = [
        Dictation("text"),
        Dictation("start_text"),
        Dictation("end_text"),
        Integer("n", 0, 100000),
        Integer("n_start", 0, 100000),
        Integer("n_end", 0, 100000),
    ]


def get_rule():
    details = RuleDetails(name="UIA Complete Diagnostic")
    get_stable_controller()
    return UiaDiagnosticRule, details
