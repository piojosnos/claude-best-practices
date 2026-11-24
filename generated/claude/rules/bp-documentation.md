<!-- GENERATED from rules/bp-documentation.md; edit that file and regenerate -->

# Documentation

Applies whenever you write or edit a doc.

- **Match the existing documentation.** Before editing or adding docs, read the neighbours and follow their voice, structure, and formatting. New content should be indistinguishable from what is already there.
- **Simple, clear, to the point.** Short sentences, plain words, one idea per line or paragraph. Cut anything that does not help the reader understand the thing. No filler, no throat-clearing, no restating the obvious.
- **Easy to read.** Write for a non-expert maintainer. Prefer the concrete term over the abstract one; name the class, token, or file rather than gesturing at it.
- **Schematic when possible.** Reach for a table, a labelled list, or a small code or ASCII diagram whenever it carries the structure better than a paragraph. The project's best existing concept docs are the reference example: target-state, skimmable, class and token oriented.
- **Docs follow code.** When a doc and the code disagree, the code is ground truth unless the doc is an explicit target-state spec; fix the doc to match.
- **Log drift, then fix it soon.** While writing a target-state doc, write down every place the code differs from it (naming, location, structure) on a tracked list, instead of smoothing it over in prose. Schedule those fixes soon; the list is not a parking lot.
