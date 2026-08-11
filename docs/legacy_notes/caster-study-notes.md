# Notes
As I learn to use this framework, I'll store some of my notes here.

## words.txt
I was wondering if I could put comments in the file. 

### Where is the file path used in the code
castervoice/lib/settings.py "paths"."GDEF_FILE" appears to store the words.txt file path

### Where is this file parsed
caster-master/castervoice/lib/merge/ccrmerging2/transformers/textreplacer/tr_parser.py

### Silly error I spent too much time on
I was wondering why this wasn't working in the words.txt file:
```
alphabet
    <<<ANY>>>
    novakeen -> november
```
It turns out that novakeen is actually uppercase.
It should be:
```
alphabet
    <<<ANY>>>
    Novakeen -> november
```