from readme_standards import outline

headings = outline("example-package")
assert headings[0]["title"] == "example-package"
assert headings[1]["title"] == "Overview"
print(f"{headings[0]['title']}: {len(headings)} required headings")
