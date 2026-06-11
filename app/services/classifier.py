from app.models.models import RelevanceScore
import datetime

KEYWORDS = {
    "ai": ["inteligência artificial", "machine learning", "deep learning", "visão computacional", "ia", "artificial intelligence"],
    "automation": ["automação", "controle", "sistemas ciberfísicos", "iot", "embarcados", "automation", "control"],
    "simulation": ["simulação", "digital twin", "modelagem", "cae", "cad", "cam", "plm", "simulation", "modeling"],
    "industry4": ["indústria 4.0", "smart manufacturing", "manufatura avançada", "robótica", "industry 4.0", "robotics"],
    "scientific": ["hpc", "computação científica", "otimização", "pesquisa operacional", "scientific computing", "optimization"]
}

WEIGHTS = {
    "ai": 20,
    "automation": 20,
    "simulation": 20,
    "industry4": 15,
    "software_eng": 15,
    "scientific": 10
}

class Classifier:
    @staticmethod
    def classify_entity(entity, source_content):
        content = (entity.name + " " + (source_content or "")).lower()

        scores = {
            "ai": 0,
            "automation": 0,
            "simulation": 0,
            "industry4": 0,
            "software_eng": 0,
            "scientific": 0
        }

        for category, keywords in KEYWORDS.items():
            for kw in keywords:
                if kw in content:
                    scores[category] = WEIGHTS[category]
                    break

        # Software engineering specific keywords
        se_keywords = ["engenharia de software", "software engineering", "desenvolvimento de software", "mendix", "low-code"]
        for kw in se_keywords:
            if kw in content:
                scores["software_eng"] = WEIGHTS["software_eng"]
                break

        total_score = sum(scores.values())

        # Re-adjusting total score to be max 100 if it exceeds (though with these weights it's exactly 100)
        total_score = min(total_score, 100)

        relevance_level = "Baixa"
        if total_score >= 80:
            relevance_level = "Alta"
        elif total_score >= 50:
            relevance_level = "Média"
        elif total_score >= 25:
            relevance_level = "Potencial"

        explanation = f"Detected themes: {[cat for cat, s in scores.items() if s > 0]}"

        return RelevanceScore(
            entity_id=entity.id,
            score_total=total_score,
            score_ai=scores["ai"],
            score_automation=scores["automation"],
            score_simulation=scores["simulation"],
            score_industry4=scores["industry4"],
            score_software_eng=scores["software_eng"],
            relevance_level=relevance_level,
            explanation=explanation,
            evaluated_at=datetime.datetime.utcnow()
        )
