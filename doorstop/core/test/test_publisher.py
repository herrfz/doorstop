"""Unit tests for the doorstop.core.publisher module."""

import unittest
from unittest.mock import patch, MagicMock

import os

from doorstop.common import DoorstopError
from doorstop.core import publisher

from doorstop.core.test import FILES, EMPTY, MockDataMixIn


class TestModule(MockDataMixIn, unittest.TestCase):  # pylint: disable=R0904

    """Unit tests for the doorstop.core.publisher module."""  # pylint: disable=C0103

    @patch('os.makedirs')
    @patch('builtins.open')
    @patch('doorstop.core.publisher.lines')
    def test_publish_html(self, mock_lines, mock_open, mock_makedirs):
        """Verify a (mock) HTML file can be created."""
        dirpath = os.path.join('mock', 'directory')
        path = os.path.join(dirpath, 'published.html')
        # Act
        publisher.publish(self.document, path, '.html')
        # Assert
        mock_makedirs.assert_called_once_with(dirpath)
        mock_open.assert_called_once_with(path, 'w')
        mock_lines.assert_called_once_with(self.document, '.html')

    def test_publish_unknown(self):
        """Verify an exception is raised when publishing unknown formats."""
        self.assertRaises(DoorstopError,
                          publisher.publish, self.document, 'a.a')
        self.assertRaises(DoorstopError,
                          publisher.publish, self.document, 'a.txt', '.a')

    @patch('os.makedirs')
    @patch('builtins.open')
    def test_publish_document(self, mock_open, mock_makedirs):
        """Verify a document can be published."""
        dirpath = os.path.join('mock', 'directory')
        path = os.path.join(dirpath, 'published.html')
        mock_document = MagicMock(spec=['items'])
        mock_document.items = []
        # Act
        publisher.publish(mock_document, path)
        # Assert
        mock_makedirs.assert_called_once_with(dirpath)
        mock_open.assert_called_once_with(path, 'w')

    @patch('doorstop.core.publisher.index')
    @patch('os.makedirs')
    @patch('builtins.open')
    def test_publish_tree(self, mock_open, mock_makedirs, mock_index):
        """Verify a tree can be published."""
        dirpath = os.path.join('mock', 'directory')
        mock_document = MagicMock()
        mock_document.items = []
        mock_tree = MagicMock()
        mock_tree.documents = [mock_document]
        # Act
        publisher.publish(mock_tree, dirpath)
        # Assert
        self.assertEqual(1, mock_makedirs.call_count)
        self.assertEqual(2, mock_open.call_count)
        mock_index.assert_called_once_with(dirpath)

    @patch('doorstop.core.publisher.index')
    @patch('os.makedirs')
    @patch('builtins.open')
    def test_publish_tree_no_index(self, mock_open, mock_makedirs, mock_index):
        """Verify a tree can be published."""
        dirpath = os.path.join('mock', 'directory')
        mock_document = MagicMock()
        mock_document.items = []
        mock_tree = MagicMock()
        mock_tree.documents = [mock_document]
        # Act
        publisher.publish(mock_tree, dirpath, create_index=False)
        # Assert
        self.assertEqual(1, mock_makedirs.call_count)
        self.assertEqual(2, mock_open.call_count)
        self.assertEqual(0, mock_index.call_count)

    def test_index(self):
        """Verify an HTML index can be created."""
        # Arrange
        path = os.path.join(FILES, 'index.html')
        # Act
        publisher.index(FILES)
        # Assert
        self.assertTrue(os.path.isfile(path))

    def test_index_no_files(self):
        """Verify an HTML index is only created when files exist."""
        path = os.path.join(EMPTY, 'index.html')
        # Act
        publisher.index(EMPTY)
        # Assert
        self.assertFalse(os.path.isfile(path))

    def test_lines_text_item_heading(self):
        """Verify text can be published from an item (heading)."""
        expected = "1.1     Heading\n\n"
        lines = publisher.lines(self.item, '.txt')
        # Act
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertEqual(expected, text)

    def test_lines_text_item_normative(self):
        """Verify text can be published from an item (normative)."""
        expected = ("1.2     req4" + '\n\n'
                    "        This shall..." + '\n\n'
                    "        Reference: Doorstop.sublime-project (line None)"
                    + '\n\n'
                    "        Links: sys4" + '\n\n')
        lines = publisher.lines(self.item3, '.txt')
        # Act
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertEqual(expected, text)

    @patch('doorstop.settings.CHECK_REF', False)
    def test_lines_text_item_no_ref(self):
        """Verify text can be published without checking references."""
        self.item.ref = 'abc123'
        self.item.heading = False
        # Act
        lines = publisher.lines(self.item, '.txt')
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertIn("Reference: 'abc123'", text)

    @patch('doorstop.settings.PUBLISH_CHILD_LINKS', True)
    def test_lines_text_item_with_child_links(self):
        """Verify text can be published with child links."""
        # Act
        lines = publisher.lines(self.item2, '.txt')
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertIn("Child links: tst1", text)

    def test_lines_markdown_item_heading(self):
        """Verify Markdown can be published from an item (heading)."""
        expected = "## 1.1 Heading {: #req3 }\n\n"
        # Act
        lines = publisher.lines(self.item, '.md', linkify=True)
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertEqual(expected, text)

    @patch('doorstop.settings.PUBLISH_CHILD_LINKS', True)
    def test_lines_markdown_item_with_child_links(self):
        """Verify Markdown can be published from an item (heading)."""
        # Act
        lines = publisher.lines(self.item2, '.md')
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertIn("Child links: tst1", text)

    def test_lines_markdown_item_normative(self):
        """Verify Markdown can be published from an item (normative)."""
        expected = ("## 1.2 req4" + '\n\n'
                    "This shall..." + '\n\n'
                    "Reference: Doorstop.sublime-project (line None)" + '\n\n'
                    "*Links: sys4*" + '\n\n')
        # Act
        lines = publisher.lines(self.item3, '.md', linkify=False)
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertEqual(expected, text)

    def test_lines_html_item(self):
        """Verify HTML can be published from an item."""
        expected = '<h2 id="req3">1.1 Heading</h2>\n'
        # Act
        lines = publisher.lines(self.item, '.html')
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertEqual(expected, text)

    @patch('doorstop.settings.PUBLISH_CHILD_LINKS', True)
    def test_lines_html_item_with_child_links(self):
        """Verify HTML can be published from an item w/ child links."""
        # Act
        lines = publisher.lines(self.item2, '.html')
        text = ''.join(line + '\n' for line in lines)
        # Assert
        self.assertIn("Child links:", text)
        self.assertIn(">tst1</a>", text)

    def test_lines_unknown(self):
        """Verify an exception is raised when iterating an unknown format."""
        # Act
        gen = publisher.lines(self.document, '.a')
        # Assert
        self.assertRaises(DoorstopError, list, gen)
