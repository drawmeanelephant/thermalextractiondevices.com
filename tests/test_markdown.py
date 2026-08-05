"""Markdown-helper tests."""

from __future__ import annotations

import unittest

from scripts.ingest.markdown import (
    callout,
    escape_cell,
    frontmatter,
    h2,
    table,
    task_list,
    wikilink,
)


class MarkdownTestCase(unittest.TestCase):
    def test_frontmatter_quotes_and_escapes(self):
        text = frontmatter(title='He said "hi"', entity_id='x', parent='y',
                           tags=["a", "b"], relations=["z"])
        self.assertIn('title: "He said \\"hi\\""', text)
        self.assertIn('id: x', text)
        self.assertIn("relations: [relates_to=z]", text)
        self.assertNotIn("summary:", text)  # closed grammar: only allowed keys

    def test_table_escaping(self):
        rendered = table(["A", "B"], [["x|y", "a\nb"]])
        self.assertIn("x\\|y", rendered)
        self.assertIn("a b", rendered)  # newline collapsed

    def test_heading_ids(self):
        self.assertEqual(h2("Section", "sec-1"), "## Section {#sec-1}")

    def test_callout(self):
        rendered = callout("warning", "Careful")
        self.assertIn('<Aside kind="warning">', rendered)
        self.assertIn("Careful", rendered)

    def test_wikilink(self):
        self.assertEqual(wikilink("devices/TED-0001"), "[[devices/TED-0001]]")
        self.assertEqual(wikilink("devices/TED-0001", "The device"), "[[devices/TED-0001|The device]]")

    def test_task_list(self):
        rendered = task_list([(True, "done"), (False, "todo")])
        self.assertEqual(rendered, "- [x] done\n- [ ] todo")


if __name__ == "__main__":
    unittest.main()
