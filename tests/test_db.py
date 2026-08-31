import unittest
import tempfile
import os
import shutil
from hub.db import init_db, get_db

class TestDB(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, "test_hub.db")
        init_db(self.test_db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_init_db_creates_tables(self):
        with get_db(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = {row["name"] for row in cursor.fetchall()}
            self.assertTrue({"agenda", "notes", "user_profile"}.issubset(tables))

    def test_agenda_crud(self):
        with get_db(self.test_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO agenda (title, event_date, event_time, category) VALUES (?, ?, ?, ?)",
                ("Doctor Appointment", "2026-09-01", "14:00", "health")
            )
            cursor.execute("SELECT * FROM agenda WHERE title = ?", ("Doctor Appointment",))
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row["event_date"], "2026-09-01")
            self.assertEqual(row["completed"], 0)

            cursor.execute("UPDATE agenda SET completed = 1 WHERE id = ?", (row["id"],))
            cursor.execute("SELECT completed FROM agenda WHERE id = ?", (row["id"],))
            self.assertEqual(cursor.fetchone()["completed"], 1)

if __name__ == "__main__":
    unittest.main()
