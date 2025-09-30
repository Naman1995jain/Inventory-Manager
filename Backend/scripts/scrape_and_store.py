#!/usr/bin/env python3
"""
Simple scraper for books.toscrape.com that stores results into the database table `scrapdata`.
Respects robots.txt and converts price strings to Decimal.
"""
import sys
import os
from pathlib import Path
import logging
import time
from decimal import Decimal, InvalidOperation

sys.path.append(str(Path(__file__).parent.parent))

from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

from app.core.database import SessionLocal, create_tables
from app.models.models import ScrapData

BASE_URL = "https://books.toscrape.com/"
USER_AGENT = "Inventory-Manager-Scraper/1.0 (+https://example.com)"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_by_robots(base_url):
    try:
        robots_url = urljoin(base_url, "robots.txt")
        resp = requests.get(robots_url, timeout=10)
        if resp.status_code != 200:
            # If no robots.txt exists (404) or other error, assume it's allowed
            return True
        content = resp.text.lower()
        # Simple check: if Disallow: / is present, avoid scraping
        return "disallow: /" not in content
    except Exception as e:
        # Log the error but allow scraping if robots.txt can't be fetched
        logger.warning(f"Error checking robots.txt: {e}")
        return True


def parse_price(text: str) -> Decimal | None:
    if not text:
        return None
    # Remove currency symbols and whitespace
    cleaned = text.strip().replace("Â", "")
    # Example format: '£53.74'
    cleaned = cleaned.replace("£", "").replace("$", "").replace(",", "")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def scrape_books():
    if not allowed_by_robots(BASE_URL):
        logger.error("Scraping disallowed by robots.txt; aborting")
        return False

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    page_url = BASE_URL
    page_limit = int(os.getenv("SCRAPE_PAGE_LIMIT", "50"))
    pages_fetched = 0
    results = []

    while page_url and (page_limit <= 0 or pages_fetched < page_limit):
        logger.info(f"Fetching page: {page_url}")
        resp = session.get(page_url, timeout=15)
        if resp.status_code != 200:
            logger.error(f"Failed to fetch {page_url}: {resp.status_code}")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        articles = soup.select("article.product_pod")
        for article in articles:
            link = article.select_one("h3 a")
            href = link.get("href")
            product_page = urljoin(page_url, href)

            # Fetch product detail page
            try:
                p = session.get(product_page, timeout=15)
                if p.status_code != 200:
                    logger.warning(f"Failed to fetch product page {product_page}")
                    continue
                psoup = BeautifulSoup(p.text, "html.parser")
                name = psoup.select_one("div.product_main h1").get_text(strip=True)
                price = psoup.select_one("p.price_color").get_text(strip=True)
                description_tag = psoup.select_one("#product_description ~ p")
                description = description_tag.get_text(strip=True) if description_tag else None
                category_tag = psoup.select_one("ul.breadcrumb li:nth-of-type(3) a")
                category = category_tag.get_text(strip=True) if category_tag else None
                rating_tag = psoup.select_one("p.star-rating")
                rating = None
                if rating_tag:
                    classes = rating_tag.get("class", [])
                    for cls in classes:
                        if cls != "star-rating":
                            rating = cls
                image_tag = psoup.select_one("div.carousel-inner img, div.item.active img, div.thumbnail img")
                image_src = image_tag.get("src") if image_tag else None
                image_url = urljoin(product_page, image_src) if image_src else None

                results.append({
                    "product_name": name,
                    "product_description": description,
                    "category": category,
                    "price": parse_price(price),
                    "rating": rating,
                    "image_url": image_url,
                    "product_page_url": product_page,
                })

                # Be polite
                time.sleep(0.5)

            except Exception as e:
                logger.exception(f"Error scraping product page {product_page}: {e}")
                continue
        pages_fetched += 1

        # Next page link
        next_link = soup.select_one("li.next a")
        if next_link and next_link.get("href"):
            page_url = urljoin(page_url, next_link.get("href"))
            time.sleep(0.5)
        else:
            page_url = None

    # Ensure tables exist (in case setup_database.py wasn't run)
    try:
        # Ensure all tables exist
        create_tables()
    except Exception:
        logger.exception("Failed to ensure tables exist; proceeding may fail")

    # Ensure the scrapdata table schema matches the ORM model; if an old table exists with
    # different columns, drop and recreate it to match the current model. This is intended
    # for initial setup; avoid in production migrations.
    try:
        from app.core.database import engine
        # Drop scrapdata table if exists then create it to ensure correct columns
        ScrapData.__table__.drop(bind=engine, checkfirst=True)
        ScrapData.__table__.create(bind=engine, checkfirst=True)
        logger.info("Recreated scrapdata table to match ORM model")
    except Exception:
        logger.exception("Failed to recreate scrapdata table; continuing anyway")

    # Store into DB
    if results:
        db = SessionLocal()
        try:
            for item in results:
                # Avoid duplicates based on product_page_url
                exists = db.query(ScrapData).filter(ScrapData.product_page_url == item["product_page_url"]).first()
                if exists:
                    logger.info(f"Skipping existing product: {item['product_name']}")
                    continue

                sd = ScrapData(
                    product_name=item["product_name"],
                    product_description=item.get("product_description"),
                    category=item.get("category"),
                    price=item.get("price"),
                    rating=item.get("rating"),
                    image_url=item.get("image_url"),
                    product_page_url=item.get("product_page_url")
                )
                db.add(sd)
            db.commit()
            logger.info(f"Stored {len(results)} scraped items (duplicates skipped)")
        except Exception as e:
            db.rollback()
            logger.exception(f"Failed to store scraped data: {e}")
            return False
        finally:
            db.close()

    return True


def main():
    print("Starting book scraping process...")
    ok = scrape_books()
    if not ok:
        print("Scraping failed!")
        sys.exit(1)
    
    print("Scraping completed successfully!")
    
    # Setup recommendation system after scraping
    print("\nSetting up recommendation system...")
    try:
        from setup_recommendations import setup_recommendation_system
        setup_success = setup_recommendation_system()
        
        if setup_success:
            print("Recommendation system setup completed!")
        else:
            print("Warning: Recommendation system setup failed, but scraping was successful.")
            print("You can run 'python scripts/setup_recommendations.py' manually later.")
    except ImportError as e:
        print(f"Could not import recommendation setup: {e}")
        print("You can run 'python scripts/setup_recommendations.py' manually later.")
    except Exception as e:
        print(f"Error setting up recommendations: {e}")
        print("You can run 'python scripts/setup_recommendations.py' manually later.")


if __name__ == "__main__":
    main()
