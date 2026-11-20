from readme_standards.document import parse

headings, separators = parse("# example-package\n\n---\n\n## Overview\n")
assert [h.title for h in headings] == ["example-package", "Overview"]
assert len(separators) == 1
print("Parsed package title, Overview, and one group separator.")
