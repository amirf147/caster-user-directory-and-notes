from dragonfly import MappingRule, Function, Dictation, Integer, Choice, Repetition
from castervoice.lib.actions import Text
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
import traceback

try:  # Try first loading from caster user directory
    import alphabet_support
except ImportError:
    from castervoice.rules.core.alphabet_rules import alphabet_support


def get_transformed_alphabet():
    """Builds the alphabet mapping by taking caster_alphabet() and applying any
    word transformers defined in words.txt (from TRParser)."""
    alphabet = alphabet_support.caster_alphabet().copy()
    try:
        from castervoice.lib.merge.ccrmerging2.transformers.text_replacer.tr_parser import TRParser

        parser = TRParser()
        defs = parser.create_definitions()
        if defs and defs.extras:
            transformed = {}
            for spoken_key, char_val in alphabet.items():
                new_key = spoken_key
                for old_term, new_term in defs.extras.items():
                    if old_term in new_key:
                        new_key = new_key.replace(old_term, new_term)
                transformed[new_key] = char_val
            return transformed
    except Exception:
        pass
    return alphabet


def get_transformed_alphabet_choice(spec=None):
    return Choice(spec, get_transformed_alphabet())


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
# DIAGNOSTIC & TEXT EDITING FUNCTIONS
# ==========================================


def read_buffer():
    """Reads the text buffer without clipboard scraping."""
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
    """Tracks the real-time character index of the text cursor."""
    print("--- Testing: Caret Index Tracking ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            pos = text_node.cursor
            return f"[UIA Success] Caret Position (Character Index): {pos}"
        return "[UIA Failure] Active field is not an editable UIA text node."

    print(os_controller.run_sync(action))


def select_word_match(text):
    """Selects a single instance of a dictated string."""
    search_str = str(text).lower().strip()
    print(f"--- Text Editing: Select Word Match '{search_str}' ---")
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
    """Selects a multi-word sequence between two anchor points."""
    start_str = str(start_text).lower().strip()
    end_str = str(end_text).lower().strip()
    print(f"--- Text Editing: Select Range '{start_str}' to '{end_str}' ---")
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


def select_letters_match(letters):
    """Selects a sequence of spelled letters matched against active buffer."""
    search_str = "".join(letters).lower().strip()
    print(f"--- Text Editing: Select Letters Match '{search_str}' ---")
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
            return f"[UIA Warning] Spelled string '{search_str}' not found in active buffer."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def select_letters_range(letters1, letters2):
    """Selects a text range between two spelled letter sequences."""
    start_str = "".join(letters1).lower().strip()
    end_str = "".join(letters2).lower().strip()
    print(f"--- Text Editing: Select Spelled Range '{start_str}' to '{end_str}' ---")
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
            return "[UIA Warning] Spelled target boundary anchors mismatch."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def put_cursor_before(text):
    """Moves the caret to the start of the first match of the dictated text."""
    search_str = str(text).lower().strip()
    print(f"--- Text Editing: Put Cursor Before '{search_str}' ---")
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
    print(f"--- Text Editing: Put Cursor After '{search_str}' ---")
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
    print("--- Text Editing: Character at Caret ---")
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

            start = max(0, pos - 5)
            end = min(length, pos + 5)
            context_str = buffer[start:end]

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
    print(f"--- Text Editing: Set Cursor to Index {idx} ---")
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
    print(f"--- Text Editing: Select Indices ({start}, {end}) ---")
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
    print("--- Text Editing: Bounding Box at Cursor ---")
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
    print(f"--- Text Editing: Bounding Box of '{search_str}' ---")
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
    print("--- Text Editing: Is Focus Editable ---")
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


def capitalize_selection():
    """Capitalizes the currently selected text in the active UIA text control."""
    print("--- Text Editing: Capitalize Selection ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            selection = text_node._text_pattern.GetSelection()
            if selection and selection.Length > 0:
                selected_range = selection.GetElement(0)
                selected_text = selected_range.GetText(-1)
                if selected_text:
                    cap_text = selected_text[0].upper() + selected_text[1:]
                    Text(cap_text).execute()
                    return f"[UIA Success] Capitalized selection: '{selected_text}' -> '{cap_text}'"
                return "[UIA Warning] Selection is empty."
            return "[UIA Warning] No text selection currently active."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


def capitalize_word(text):
    """Finds the specified word/text in active buffer, selects it, and capitalizes it."""
    search_str = str(text).lower().strip()
    print(f"--- Text Editing: Capitalize Word '{search_str}' ---")
    os_controller = get_stable_controller()
    if not os_controller:
        return

    def action(context):
        text_node = get_text_node(context)
        if text_node:
            full_buffer = text_node.expanded_text
            full_buffer_lower = full_buffer.lower()
            start_idx = full_buffer_lower.find(search_str)
            if start_idx != -1:
                matched_str = full_buffer[start_idx : start_idx + len(search_str)]
                cap_str = matched_str[0].upper() + matched_str[1:]
                text_node.select_range(start_idx, start_idx + len(search_str))
                Text(cap_str).execute()
                return f"[UIA Success] Capitalized '{matched_str}' to '{cap_str}' at index {start_idx}."
            return f"[UIA Warning] '{search_str}' not found in active buffer."
        return "[UIA Failure] Target unavailable."

    print(os_controller.run_sync(action))


# ==========================================
# GRAMMAR AND MAPPING CONFIGURATION
# ==========================================


class TextEditingRule(MappingRule):
    mapping = {
        "buffer read": Function(read_buffer),
        "caret read": Function(show_caret_position),
        "select <text>": Function(select_word_match),
        "select <start_text> to <end_text>": Function(select_word_range),
        "select <letters>": Function(select_letters_match),
        "select <letters1> to <letters2>": Function(select_letters_range),
        "[put] cursor before <text>": Function(put_cursor_before),
        "[put] cursor after <text>": Function(put_cursor_after),
        "[put] cursor [at | to] <n>": Function(set_cursor_at_index),
        "select <n_start> [to | through] <n_end>": Function(select_range_indices),
        "caret character": Function(get_char_at_cursor),
        "caret bounds": Function(show_bounding_box_at_cursor),
        "bounds <text>": Function(show_bounding_box_of_word),
        "is editable": Function(check_editable),
        "capitalize that": Function(capitalize_selection),
        "capitalize <text>": Function(capitalize_word),
    }
    extras = [
        Dictation("text"),
        Dictation("start_text"),
        Dictation("end_text"),
        Integer("n", 0, 100000),
        Integer("n_start", 0, 100000),
        Integer("n_end", 0, 100000),
        Repetition(get_transformed_alphabet_choice(), min=1, max=10, name="letters"),
        Repetition(get_transformed_alphabet_choice(), min=1, max=10, name="letters1"),
        Repetition(get_transformed_alphabet_choice(), min=1, max=10, name="letters2"),
    ]


def get_rule():
    details = RuleDetails(name="Text Editing")
    get_stable_controller()
    return TextEditingRule, details
