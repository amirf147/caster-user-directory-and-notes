# Notes
As I learn to use this framework, I'll store some of my notes here.

## words.txt
I was wondering if I could put comments in the file. 

### Where is the file path used in the code
castervoice/lib/settings.py "paths"."GDEF_FILE" appears to store the words.txt file path

### Where is this file parsed
caster-master/castervoice/lib/merge/ccrmerging2/transformers/textreplacer/tr_parser.py

This is the part of the code I was looking for:
```
        def _parse_lines(self, lines):
        """
        :param lines: list of str; lines from words.txt
        - these lines indicate either mode changes or transformations
        - this method parses the lines and returns a data structure which
          informs the transformer of how to behave
        :return: TRDefinitions
        """
        all_modes = frozenset([TRParseMode.ANY,
                               TRParseMode.SPEC,
                               TRParseMode.EXTRA,
                               TRParseMode.DEFAULT,
                               TRParseMode.NOT_SPECS])
        specs = {}
        extras = {}
        defaults = {}
        mode = TRParseMode.ANY

        for line in lines:
            line = line.strip()
            # ignore comments and empty lines
            if line.startswith("#") or line.isspace():
                continue
            # handle mode changes
            if line in all_modes:
                mode = line
                continue
            # ignore invalid lines (not a mode, not a transformation)
            if "->" not in line:
                continue

            # extract source and target
            source_and_target = line.split("->")
            source = source_and_target[0].strip()
            # allow for inline comments on the right side of the line
            target = "#".join(source_and_target[1].split("#")[:1])
            target = target.strip()

```