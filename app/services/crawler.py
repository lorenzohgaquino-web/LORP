import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib
from app.database import SessionLocal
from app.models.models import Source, Entity, Evidence
from app.services.extractor import Extractor
import logging

ALLOWED_DOMAINS = {
    "ufrj.br",
    "coppe.ufrj.br",
    "poli.ufrj.br",
    "cos.ufrj.br",
    "nce.ufrj.br",
    "ic.ufrj.br"
}

class Crawler:
    def __init__(self, db):
        self.db = db
        self.visited = set()

    def is_allowed(self, url):
        domain = urlparse(url).netloc.lower()
        return any(domain == d or domain.endswith("." + d) for d in ALLOWED_DOMAINS)

    def crawl(self, seed_urls, max_depth=2):
        queue = [(url, 0) for url in seed_urls]

        while queue:
            url, depth = queue.pop(0)
            if url in self.visited or depth > max_depth:
                continue

            if not self.is_allowed(url):
                continue

            self.visited.add(url)
            print(f"Fetching: {url} at depth {depth}")

            try:
                response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
                if response.status_code != 200:
                    continue

                html_content = response.text
                html_hash = hashlib.md5(html_content.encode()).hexdigest()

                # Save or Update Source
                source = self.db.query(Source).filter(Source.url == url).first()
                if not source:
                    source = Source(
                        url=url,
                        domain=urlparse(url).netloc,
                        html_hash=html_hash,
                        status_code=response.status_code,
                        content_type=response.headers.get('Content-Type')
                    )
                    metadata = Extractor.extract_metadata(html_content)
                    source.title = metadata['title']
                    self.db.add(source)
                    self.db.commit()
                    self.db.refresh(source)
                else:
                    source.html_hash = html_hash
                    source.status_code = response.status_code
                    self.db.commit()

                # Extract Entities
                entities_data = Extractor.extract_entities(html_content, url)
                for ent_data in entities_data:
                    evidences = ent_data.pop('evidence', [])

                    # Deduplication: check if entity with same name and source already exists
                    existing_entity = self.db.query(Entity).filter(
                        Entity.name == ent_data['name'],
                        Entity.source_id == source.id
                    ).first()

                    if not existing_entity:
                        entity = Entity(
                            **ent_data,
                            source_id=source.id
                        )
                        self.db.add(entity)
                        self.db.commit()
                        self.db.refresh(entity)
                    else:
                        entity = existing_entity

                    # Add Evidence
                    for ev_data in evidences:
                        existing_ev = self.db.query(Evidence).filter(
                            Evidence.entity_id == entity.id,
                            Evidence.snippet == ev_data['snippet']
                        ).first()
                        if not existing_ev:
                            evidence = Evidence(
                                **ev_data,
                                entity_id=entity.id
                            )
                            self.db.add(evidence)

                self.db.commit()

                # Find more links if not at max depth
                if depth < max_depth:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    for a in soup.find_all('a', href=True):
                        link = urljoin(url, a['href'])
                        if self.is_allowed(link):
                            queue.append((link, depth + 1))

            except Exception as e:
                print(f"Error crawling {url}: {e}")
                self.db.rollback()

def run_crawl_job(seed_urls, max_depth=2):
    db = SessionLocal()
    try:
        crawler = Crawler(db)
        crawler.crawl(seed_urls, max_depth)
    finally:
        db.close()
