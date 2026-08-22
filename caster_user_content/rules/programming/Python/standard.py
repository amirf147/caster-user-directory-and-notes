"""
Python Standard Symbol Specifications

Originally part of Caster (castervoice/rules/ccr/standard.py)
Copyright (c) 2015-2026 synkarius, Caster Contributors

Personal customizations:
Copyright (c) 2024-2026 Amir Farhadi
SPDX-License-Identifier: LGPL-3.0-or-later
"""


class SymbolSpecs(object):
    IF = "iffae"
    ELSE = "shells"

    SWITCH = "switch"
    CASE = "case of"
    BREAK = "breaker"
    DEFAULT = "default"

    DO_LOOP = "do loop"
    WHILE_LOOP = "while loop"
    FOR_LOOP = "for loop"
    FOR_EACH_LOOP = "for each"

    TO_INTEGER = "convert to integer"
    TO_FLOAT = "convert to floating point"
    TO_STRING = "convert to string"

    AND = "lodge and"
    OR = "lodge or"
    NOT = "lodge not"

    SYSOUT = "pi print"

    IMPORT = "import"

    FUNCTION = "function"
    CLASS = "class"

    COMMENT = "add comment"
    LONG_COMMENT = "long comment"

    NULL = "value not"

    RETURN = "return"

    TRUE = "value true"
    FALSE = "value false"

    # not part of the programming standard:
    CANCEL = "(terminate | escape | exit | cancel)"

    @staticmethod
    def set_cancel_word(spec):
        SymbolSpecs.CANCEL = spec
