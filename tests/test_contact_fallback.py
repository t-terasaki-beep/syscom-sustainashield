"""No-network checks for the contact page's truthful, non-collecting fallback."""
from pathlib import Path
import unittest

HTML = (Path(__file__).resolve().parents[1] / "contact.html").read_text(encoding="utf-8")
LINE_URL = "https://line.me/R/ti/p/@829oslez"


class ContactFallbackTests(unittest.TestCase):
    def test_unimplemented_form_cannot_collect_personal_data(self):
        self.assertNotRegex(HTML, r"<form\b")
        self.assertNotIn('type="submit"', HTML)
        self.assertNotIn("送信先のフォーム処理を実装してください", HTML)
        self.assertNotIn("この内容で送信する", HTML)

    def test_contact_copy_explains_fallback(self):
        self.assertIn("フォーム受付は現在準備中", HTML)
        self.assertIn("個人情報を入力させるフォームは表示していません", HTML)
        self.assertIn("住宅向け公式LINEで相談する", HTML)

    def test_official_line_links_are_consistent(self):
        self.assertEqual(HTML.count('href="' + LINE_URL + '"'), 4)
        self.assertNotIn("@631cqlgf", HTML)
        self.assertNotIn("LINE公式アカウントのURLをここに設定してください", HTML)

    def test_no_fake_qr_and_privacy_link_preserved(self):
        self.assertNotIn("QRコード<br>", HTML)
        self.assertNotIn("URL設定後に表示", HTML)
        self.assertIn('href="privacy.html"', HTML)


if __name__ == "__main__":
    unittest.main()
