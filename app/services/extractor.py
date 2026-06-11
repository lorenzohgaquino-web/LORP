from bs4 import BeautifulSoup
import re

class Extractor:
    @staticmethod
    def extract_entities(html_content, source_url):
        soup = BeautifulSoup(html_content, 'html.parser')
        entities = []

        # Generic Extraction logic
        lab_keywords = ["Laboratório", "Lab", "Laboratory", "Grupo de Pesquisa", "Research Group"]

        for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
            text = header.get_text(strip=True)
            if any(kw.lower() in text.lower() for kw in lab_keywords) and len(text) < 200:
                snippet = header.parent.get_text(separator=' ', strip=True)[:500] if header.parent else text
                entities.append({
                    "entity_type": "laboratory",
                    "name": text,
                    "official_contact": Extractor.find_email(soup) or Extractor.find_email(header.parent),
                    "official_contact_type": "institutional_email" if Extractor.find_email(soup) else None,
                    "evidence": [{
                        "evidence_type": "official_page_mention",
                        "snippet": snippet,
                        "source_url": source_url,
                        "confidence": 0.8
                    }]
                })

        # 2. Look for Departments or Units
        unit_keywords = ["Escola", "Faculdade", "Instituto", "COPPE", "Poli", "PESC", "Programa", "Engenharia"]
        title = soup.title.string if soup.title else ""
        if any(kw.lower() in title.lower() for kw in unit_keywords):
             name = title.strip()
             entities.append({
                "entity_type": "unit",
                "name": name,
                "official_contact": Extractor.find_email(soup),
                "official_contact_type": "institutional_email" if Extractor.find_email(soup) else None,
                "evidence": [{
                    "evidence_type": "page_title",
                    "snippet": f"Found in page title: {name}",
                    "source_url": source_url,
                    "confidence": 0.9
                }]
            })

        # Deduplicate within the same page
        unique_entities = []
        seen_names = set()
        for e in entities:
            if e['name'] not in seen_names:
                unique_entities.append(e)
                seen_names.add(e['name'])

        return unique_entities

    @staticmethod
    def find_email(soup_element):
        if not soup_element:
            return None
        text = soup_element.get_text()
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        inst_emails = [e for e in emails if 'ufrj.br' in e]
        return inst_emails[0] if inst_emails else (emails[0] if emails else None)

    @staticmethod
    def extract_metadata(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return {
            "title": soup.title.string.strip() if soup.title else "No Title",
            "text_content": soup.get_text(separator=' ', strip=True)
        }
