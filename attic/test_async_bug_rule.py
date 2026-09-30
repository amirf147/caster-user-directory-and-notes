"""
Inspect Stack & Asynchronous Action Diagnostics Rule

Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: Apache-2.0
"""

from dragonfly import MappingRule, Function, ShortIntegerRef
from castervoice.lib.ctrl.mgr.rule_details import RuleDetails
from castervoice.lib.merge.state.actions import AsynchronousAction
from castervoice.lib.merge.state.short import R, L, S
from castervoice.lib import control

# Track IDs
TOTAL_COMMANDS_RECORDED = 0
ASYNC_LOOP_BIRTH_COUNT = None

# Monkey-patch stack.add once to track true lifetime commands
_orig_stack_add = None
def install_stack_tracker():
    global _orig_stack_add
    nexus = control.nexus()
    if not nexus or not getattr(nexus, "state", None):
        return False
    stack = nexus.state.stack
    if _orig_stack_add is None:
        _orig_stack_add = stack.add
        def tracked_add(item):
            global TOTAL_COMMANDS_RECORDED
            TOTAL_COMMANDS_RECORDED += 1
            # Stamp the item with its sequence ID
            item._push_id = TOTAL_COMMANDS_RECORDED
            return _orig_stack_add(item)
        stack.add = tracked_add
    return True

def background_tick():
    print("  >>> [ASYNC LOOP TICKING] <<<")
    return False

def on_start_loop():
    global ASYNC_LOOP_BIRTH_COUNT
    install_stack_tracker()
    ASYNC_LOOP_BIRTH_COUNT = TOTAL_COMMANDS_RECORDED + 1
    print("\n" + "="*70)
    print(f"  [LOOP STARTED] Registered as Command #{ASYNC_LOOP_BIRTH_COUNT}")
    print("="*70)

def print_stack_status():
    install_stack_tracker()
    nexus = control.nexus()
    if not nexus or not getattr(nexus, "state", None):
        print("Nexus not ready.")
        return
    stack = nexus.state.stack
    total_slots_used = len(stack.list)
    incomplete_items = stack.get_incomplete_seekers()
    
    # Locate where the loop is in the buffer
    loop_index = None
    loop_push_id = None
    for idx, item in enumerate(stack.list):
        if getattr(item, "type", None) == "continuer" and not item.complete:
            loop_index = idx
            loop_push_id = getattr(item, "_push_id", "Unknown")
            break

    commands_since_loop = (TOTAL_COMMANDS_RECORDED - ASYNC_LOOP_BIRTH_COUNT) if ASYNC_LOOP_BIRTH_COUNT else 0

    print("\n" + "="*75)
    print("                      CASTER CONTEXT-STACK INSPECTOR")
    print("="*75)
    print(f" Total Voice Commands Ever Spoken: {TOTAL_COMMANDS_RECORDED}")
    print(f" Current 30-Slot Buffer Fill     : {total_slots_used} / {stack.max_list_size} slots in use")
    print(f" Commands Spoken SINCE Loop      : {commands_since_loop} (Needs 30+ to test eviction)")
    
    if loop_index is not None:
        print(f" Loop Health                     : [ALIVE & TRACKED in Slot #{loop_index:02d} (Born as Cmd #{loop_push_id})]")
        if loop_index == 0:
            print(" Position Warning                : Loop is at SLOT 00! (The oldest slot).")
            print("                                   On master, the NEXT command will DELETE it.")
            print("                                   On PR #981, it will be PROTECTED.")
        else:
            print(f" Position Warning                : Safe for now. ({loop_index} older commands will be dropped before this loop reaches Slot 00).")
        print(" Cancel Ability                  : YES -> Saying 'cancel' will stop it.")
    else:
        print(" Loop Health                     : [LOST / EVICTED FROM THE BUFFER!]")
        print(" Cancel Ability                  : NO  -> Saying 'cancel' will do nothing.")
    
    print("-" * 75)
    print(" Current 30-Slot Window (Slot 00 = Oldest, Slot 29 = Newest):")
    for idx, item in enumerate(stack.list):
        item_type = getattr(item, "type", type(item).__name__)
        is_done = getattr(item, "complete", True)
        status_label = "[DONE]  " if is_done else "[ACTIVE]"
        cmd_id = getattr(item, "_push_id", "?")
        
        if item_type == "continuer" and not is_done:
            prefix = " -> SLOT "
            note = " <--- (THE ASYNC LOOP)"
        else:
            prefix = "    SLOT "
            note = ""
            
        print(f"{prefix}{idx:02d}: {status_label} [Cmd #{cmd_id:>3}] Type: {item_type:<10}{note}")
    print("="*75 + "\n")

def push_multiple_dummy_items(n=35):
    """Feeds completed actions into stack so you don't have to speak 35 times."""
    install_stack_tracker()
    from castervoice.lib.merge.state.actions2 import NullAction
    from castervoice.lib.merge.state.stackitems import StackItemRegisteredAction
    
    nexus = control.nexus()
    if not nexus or not getattr(nexus, "state", None):
        print("Nexus not ready.")
        return
    stack = nexus.state.stack
    count = int(n)
    print(f"\n[ACTION] Generating {count} completed commands...")
    for _ in range(count):
        dummy_action = NullAction()
        dummy_item = StackItemRegisteredAction(dummy_action, None)
        dummy_item.complete = True
        stack.add(dummy_item)
        
    print_stack_status()

class InspectStackRule(MappingRule):
    mapping = {
        "start infinite loop":
            R(Function(on_start_loop)) +
            R(AsynchronousAction(
                [L(S(["cancel"], background_tick))],
                repetitions=0,
                time_in_seconds=2.0,
                blocking=False
            )),
        "check stack":
            R(Function(print_stack_status)),
        "flood stack [<n>]":
            R(Function(push_multiple_dummy_items)),
    }
    extras = [
        ShortIntegerRef("n", 1, 100),
    ]
    defaults = {"n": 35}

def _deferred_install():
    if install_stack_tracker():
        if hasattr(_deferred_install, "timer") and _deferred_install.timer:
            _deferred_install.timer.stop()
            _deferred_install.timer = None

def get_rule():
    if not install_stack_tracker():
        try:
            from dragonfly import get_current_engine
            engine = get_current_engine()
            if engine:
                _deferred_install.timer = engine.create_timer(_deferred_install, 0.2)
        except Exception:
            pass
    return InspectStackRule, RuleDetails(name="inspect stack rule")