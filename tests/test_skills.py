"""Tests for the skills system."""

import unittest
from jarvis.skills import (
    CodeExecutionSkill, NoteTakingSkill,
    SkillsManager, SkillResult
)


class TestCodeExecutionSkill(unittest.TestCase):
    """Test code execution skill."""

    def setUp(self):
        self.skill = CodeExecutionSkill()

    def test_can_handle(self):
        """Test skill detection."""
        self.assertTrue(self.skill.can_handle("run code 2+2"))
        self.assertTrue(self.skill.can_handle("calculate 10 * 5"))
        self.assertFalse(self.skill.can_handle("what is the weather"))

    def test_extract_code(self):
        """Test code extraction."""
        code = self.skill._extract_code("run code `2+2`")
        self.assertIsNotNone(code)


class TestNoteTakingSkill(unittest.TestCase):
    """Test note taking skill."""

    def setUp(self):
        self.skill = NoteTakingSkill()

    def test_add_note(self):
        """Test adding a note."""
        result = self.skill.execute("note Buy milk")
        self.assertTrue(result.success)
        self.assertEqual(len(self.skill.notes), 1)

    def test_list_notes(self):
        """Test listing notes."""
        self.skill.execute("note Remember the milk")
        result = self.skill.execute("what did I note")
        self.assertTrue(result.success)
        self.assertIn("milk", result.message)


class TestSkillsManager(unittest.TestCase):
    """Test skills manager."""

    def setUp(self):
        self.manager = SkillsManager()

    def test_find_skill(self):
        """Test finding skills."""
        skill = self.manager.find_skill("run code 2+2")
        self.assertIsNotNone(skill)
        self.assertEqual(skill.name, "code")

    def test_execute_skill(self):
        """Test skill execution."""
        result = self.manager.execute("note test note")
        self.assertIsNotNone(result)
        self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
