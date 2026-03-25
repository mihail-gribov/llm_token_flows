#!/usr/bin/env python3
"""Build a single PDF from all markdown files and images."""

import markdown
import weasyprint
from pathlib import Path

ROOT = Path(__file__).parent

# Order: README first, then individual examples
FILES = [
    "README.md",
    "capital_japan.md",
    "ulysses_author.md",
    "closest_planet.md",
    "lightest_element.md",
    "mona_lisa.md",
]

def md_to_html(md_path: Path, strip_license: bool = False) -> str:
    text = md_path.read_text(encoding="utf-8")
    # Strip PDF version and License sections from README for PDF output
    if strip_license:
        text = text.split("\n## PDF version")[0]
        text = text.split("\n## License")[0]
    import re
    # Strip per-file copyright lines (e.g. "© 2026 mihailgribov")
    text = re.sub(r'\n---\n©.*$', '', text, flags=re.DOTALL)
    # Strip "Flow diagram" and "Probability trace" subheadings — images are self-explanatory
    text = re.sub(r'^## Flow diagram\n+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^## Probability trace\n+', '', text, flags=re.MULTILINE)
    # Convert relative image paths to absolute file:// URIs
    images_dir = (ROOT / "images").resolve()
    text = text.replace("images/", f"file://{images_dir}/")
    return markdown.markdown(text, extensions=["tables"])

sections = []
for fname in FILES:
    path = ROOT / fname
    if path.exists():
        sections.append(md_to_html(path, strip_license=(fname == "README.md")))

license_html = markdown.markdown(
    "## License\n\n"
    "This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).\n\n"
    "Source: [github.com/mihail-gribov/llm_token_flows](https://github.com/mihail-gribov/llm_token_flows)\n\n"
    "Contact: [mihail.gribov.rs@gmail.com](mailto:mihail.gribov.rs@gmail.com) · "
    "[LinkedIn](https://www.linkedin.com/in/mihail-gribov-676b5836a/)"
)

body = "\n<hr>\n".join(sections) + "\n" + license_html

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: A4;
    margin: 2cm;
  }}
  body {{
    font-family: sans-serif;
    font-size: 11pt;
    line-height: 1.5;
    color: #222;
  }}
  h1 {{
    font-size: 20pt;
    margin-top: 1.5em;
    page-break-before: auto;
  }}
  h2 {{
    font-size: 15pt;
    margin-top: 1.2em;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 12pt;
    margin-top: 1em;
    page-break-after: avoid;
  }}
  img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    font-size: 9pt;
    margin: 1em 0;
  }}
  th, td {{
    border: 1px solid #ccc;
    padding: 6px 8px;
    text-align: left;
  }}
  th {{
    background: #f0f0f0;
  }}
  hr {{
    border: none;
    border-top: 2px solid #ccc;
    margin: 2em 0;
    page-break-after: always;
  }}
  code {{
    background: #f5f5f5;
    padding: 1px 4px;
    border-radius: 3px;
    font-size: 10pt;
  }}
  a {{
    color: #0066cc;
    text-decoration: none;
  }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

output = ROOT / "llm_token_flow.pdf"
weasyprint.HTML(string=html, base_url=str(ROOT)).write_pdf(str(output))
print(f"PDF saved to {output}")
