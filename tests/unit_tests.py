# prevent ModuleNotFoundError
import os
import sys

# Get the absolute path of the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add it to sys.path
sys.path.insert(0, project_root)

import re
import unittest

from dotenv import load_dotenv

from BestMtgDeck.BestMtgDeck.bestdeck import FORMAT_CONVERTER
from BestMtgDeck.BestMtgDeck.format_deck import format_deck
from BestMtgDeck.forms import DeckFormatterForm
from BestMtgDeck.start import create_app
from tests.formatter_examples import formatter_examples


class BaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        # load dotenv from parent folder irrespective of from where the test is run
        load_dotenv(os.path.join(project_root, "secrets.env"))
        self.app = create_app()
        self.app_context = self.app.test_request_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.app_context.pop()


class TestBestMtgDeck(BaseTestCase):
    def test_routes(self):
        urls = (
            "/",
            "/decklist_formatter",
            "/sign",
            "/value",
        )
        for url in urls:
            with self.client.get(url) as response:
                status_code = response.status_code
            self.assertEqual(
                status_code,
                200,
                f"Failed at {url}: Expected 200, got {status_code}",
            )

    def test_api(self):
        with self.client.get("/api/tooltip.js") as response:
            self.assertEqual(response.status_code, 302)
        with self.client.get("/static/js/tooltip.js") as response:
            self.assertEqual(response.status_code, 200)

    def test_deck_formatter_post(self):
        response = self.client.post(
            "/decklist_formatter",
            data=DeckFormatterForm(
                deck_list="decklist",
                deck_name="deck_name",
                player_name="player_name",
                event_name="event_name",
                player_role="Winner",
                note_redazione="note_redazione",
            ).data,
        )
        self.assertEqual(response.status_code, 200)

    def test_deck_formatter_examples(self):
        for k, v in formatter_examples.items():
            bbcode, html, cards_and_mistakes = format_deck(k, "", "", "", "", "")
            self.assertEqual(bbcode, v)

    def test_all_decks(self):
        for currency in ("$", "€"):
            for format_name in FORMAT_CONVERTER:
                format_url = f"/{format_name}/{currency}"
                with self.client.get(format_url) as resp:
                    response = resp
                self.assertEqual(
                    response.status_code,
                    200,
                    f"Failed at {format_url}: Expected 200, got {response.status_code}",
                )
                # Regular expression to find all href links starting with calc and including potentially $
                # Match paths that start with /calc
                # Handle both path-based formats like /calc/Standard/... and query parameter formats like /calc?format=Standard&...
                # Capture everything until the closing quote (single or double)
                # Support special characters and URL encoding in the query parameters
                links = re.findall(
                    r"(?:\'|\")\/calc(?:\/[^?'\"]*|\?[^'\"]*?)(?:\'|\")",
                    response.data.decode("utf-8"),
                )
                links = [link[1:-1] for link in links]  # remove quotes
                self.assertNotEqual(
                    len(links), 0, f"Failed at {format_url}: No calc links found"
                )
                for link in links:
                    with self.subTest(link=link):
                        with self.client.get(link) as response:
                            self.assertEqual(
                                response.status_code,
                                200,
                                f"Failed at {link}: Expected 200, got {response.status_code}",
                            )

    def test_404(self):
        urls = (
            "/gibberish",
            "/calc/gibberish",
            "/calc?format=gibberish",
            "/calc?format=Standard&deck=Grul%20Aggro&currency=€",
        )
        for url in urls:
            with self.client.get(url) as response:
                resp = response.data.decode("utf-8")
                self.assertTrue(
                    "The requested URL was not found on the server" in resp,
                    f"Failed at {url}: no The requested URL was not found on the server in {resp}",
                )
                self.assertEqual(
                    response.status_code,
                    404,
                    f"Failed at {url}: Expected 404 got {response.status_code}",
                )

    def test_paypal_link(self):
        for url in ("/", "/sign", "/value"):
            with self.client.get(url) as response:
                self.assertTrue(
                    self.app.config["PAYPAL_LINK"] in response.data.decode("utf-8"),
                    f"Failed at {url}: Paypal link found in page. Maybe not set in secrets.env",
                )


if __name__ == "__main__":
    unittest.main()
