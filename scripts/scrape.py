"""Scraper for kink.com shoot pages.

Extracts metadata from kink.com shoot pages including title, performers,
director, description, upload date, categories, and channel.

Example usage:

python3 scripts/scrape.py \
    --start-shoot-id 0 \
    --end-shoot-id 48000 \
    --output-path data/kink_shoots.json

The script supports resuming from previous runs - it tracks scraped IDs and
non-existent IDs in the output file and skips them on subsequent runs.
"""

import argparse
import html
import json
from pathlib import Path
from typing import Any

import cloudscraper
from bs4 import BeautifulSoup
from tqdm import tqdm


class ShootNotFoundError(Exception):
    """Raised when a shoot ID does not exist."""

    pass


def get_shoot_info(shoot_id: int, scraper: cloudscraper.CloudScraper) -> dict[str, Any]:
    """Extract information from a kink.com shoot page.

    Args:
        shoot_id: The shoot ID to scrape.
        scraper: CloudScraper instance to use for requests.

    Returns:
        Dictionary containing shoot information including performers.

    Raises:
        ShootNotFoundError: If the shoot does not exist.
        Exception: If the page fails to load.
    """
    url = f"https://www.kink.com/shoot/{shoot_id}"
    response = scraper.get(url)

    if response.status_code != 200:
        raise Exception(f"HTTP {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    # Check if this is a valid shoot page by looking for VideoObject JSON-LD
    has_video_object = False
    result = {
        "shoot_id": shoot_id,
        "title": None,
        "performers": [],
        "director": None,
        "description": None,
        "upload_date": None,
        "categories": [],
        "channel": None,
    }

    # Extract data from JSON-LD structured data
    scripts = soup.find_all("script", type="application/ld+json")
    for script in scripts:
        try:
            data = json.loads(script.string)

            # Handle VideoObject schema
            if data.get("@type") == "VideoObject":
                has_video_object = True
                result["title"] = data.get("name")
                result["description"] = data.get("description")
                result["upload_date"] = data.get("uploadDate")

                # Extract performers from actor array
                actors = data.get("actor", [])
                for actor in actors:
                    if isinstance(actor, dict) and actor.get("@type") == "Person":
                        name = actor.get("name")
                        if name:
                            result["performers"].append(name)

                # Extract director
                director = data.get("director")
                if isinstance(director, dict) and director.get("@type") == "Person":
                    result["director"] = director.get("name")

        except (json.JSONDecodeError, TypeError):
            pass

    # If no VideoObject found, this shoot doesn't exist
    if not has_video_object:
        raise ShootNotFoundError(f"Shoot {shoot_id} does not exist")

    # Extract categories and channel from video player data-setup attribute
    video_container = soup.find("div", class_="kvjs-container")
    if video_container and video_container.get("data-setup"):
        try:
            # Decode HTML entities and parse JSON
            data_setup = html.unescape(video_container["data-setup"])
            player_data = json.loads(data_setup)

            # Extract channel
            result["channel"] = player_data.get("channelName")

            # Extract categories from trackingData.tagIds
            tracking_data = player_data.get("trackingData", {})
            tag_ids = tracking_data.get("tagIds", [])
            result["categories"] = tag_ids

        except (json.JSONDecodeError, TypeError):
            pass

    return result


def load_existing_data(output_path: Path) -> dict[str, Any]:
    """Load existing scraped data from output file.

    Args:
        output_path: Path to the output JSON file.

    Returns:
        Dictionary with 'shoots' list and metadata.
    """
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"shoots": [], "scraped_ids": [], "not_found_ids": []}


def get_highest_processed_id(output_path: Path) -> int | None:
    """Get the highest processed ID from existing output file.

    Args:
        output_path: Path to the output JSON file.

    Returns:
        The highest ID that was processed (scraped or not found), or None if
        no data exists.
    """
    if not output_path.exists():
        return None

    data = load_existing_data(output_path)
    scraped_ids = data.get("scraped_ids", [])
    not_found_ids = data.get("not_found_ids", [])

    all_ids = scraped_ids + not_found_ids
    if not all_ids:
        return None

    return max(all_ids)


def save_data(output_path: Path, data: dict[str, Any]) -> None:
    """Save scraped data to output file.

    Args:
        output_path: Path to the output JSON file.
        data: Dictionary with shoots data to save.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def scrape_shoots(
    start_id: int, end_id: int, output_path: Path
) -> tuple[int, int, int]:
    """Scrape multiple shoots and save to JSON.

    Args:
        start_id: Starting shoot ID (inclusive).
        end_id: Ending shoot ID (inclusive).
        output_path: Path to save the JSON output.

    Returns:
        Tuple of (success_count, not_found_count, error_count).
    """
    # Load existing data to resume from previous runs
    data = load_existing_data(output_path)
    scraped_ids = set(data.get("scraped_ids", []))
    not_found_ids = set(data.get("not_found_ids", []))

    # Create scraper instance (reuse for all requests)
    scraper = cloudscraper.create_scraper(
        browser={"browser": "chrome", "platform": "windows", "mobile": False}
    )

    success_count = 0
    not_found_count = 0
    error_count = 0

    # Create progress bar
    shoot_ids = range(start_id, end_id + 1)
    pbar = tqdm(shoot_ids, desc="Scraping", unit="shoot")

    for shoot_id in pbar:
        # Skip already processed IDs
        if shoot_id in scraped_ids:
            success_count += 1
            pbar.set_postfix(
                ok=success_count, notfound=not_found_count, err=error_count
            )
            continue
        if shoot_id in not_found_ids:
            not_found_count += 1
            pbar.set_postfix(
                ok=success_count, notfound=not_found_count, err=error_count
            )
            continue

        try:
            shoot_info = get_shoot_info(shoot_id, scraper)
            data["shoots"].append(shoot_info)
            data["scraped_ids"].append(shoot_id)
            scraped_ids.add(shoot_id)
            success_count += 1
        except ShootNotFoundError:
            # Shoot doesn't exist - record it so we don't retry
            data["not_found_ids"].append(shoot_id)
            not_found_ids.add(shoot_id)
            not_found_count += 1
        except Exception as e:
            error_count += 1
            tqdm.write(f"Error on shoot {shoot_id}: {e}")

        # Update progress bar
        pbar.set_postfix(ok=success_count, notfound=not_found_count, err=error_count)

        # Save after each shoot
        save_data(output_path, data)

    return success_count, not_found_count, error_count


def main() -> None:
    """Main entry point for the scraper."""
    parser = argparse.ArgumentParser(
        description="Scrape kink.com shoot pages for metadata."
    )
    parser.add_argument(
        "--start-shoot-id",
        type=int,
        default=None,
        help="Starting shoot ID (inclusive). If not provided and output file "
        "exists, resumes from highest processed ID + 1.",
    )
    parser.add_argument(
        "--end-shoot-id",
        type=int,
        required=True,
        help="Ending shoot ID (inclusive)",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        required=True,
        help="Path to save the JSON output",
    )

    args = parser.parse_args()

    # Determine start ID
    start_id = args.start_shoot_id
    if start_id is None:
        highest_id = get_highest_processed_id(args.output_path)
        if highest_id is not None:
            start_id = highest_id + 1
            print(f"Resuming from ID {start_id} (highest processed: {highest_id})")
        else:
            start_id = 0
            print("No existing data found, starting from ID 0")

    print(f"Scraping shoots {start_id} to {args.end_shoot_id}")
    print(f"Output: {args.output_path}")

    success, not_found, errors = scrape_shoots(
        start_id, args.end_shoot_id, args.output_path
    )

    print(f"\nCompleted: {success} found, {not_found} not found, {errors} errors")


if __name__ == "__main__":
    main()
