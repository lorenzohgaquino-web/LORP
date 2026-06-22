import json
import os

class EventCollector:
    def __init__(self, filepath='events_data.json'):
        self.filepath = filepath
        self.events = self.load_events()

    def load_events(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_events(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)

    def add_event(self, event_data):
        # Basic validation of fields
        required_fields = [
            "Nome do Evento", "Tipo", "Data / Período", "Local",
            "Vertical / Tema principal", "Soluções DSW com aderência",
            "Público-alvo", "Organização responsável", "Site / URL",
            "Nível de relevância", "Oportunidade de atuação"
        ]
        for field in required_fields:
            if field not in event_data:
                print(f"Warning: Missing field {field}")

        self.events.append(event_data)
        self.save_events()
        print(f"Event '{event_data.get('Nome do Evento')}' added successfully.")

    def get_count(self):
        return len(self.events)

if __name__ == "__main__":
    import sys
    # This can be used as a simple CLI if needed
    pass
