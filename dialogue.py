"""
Dijalog sistem - AI debate između dva modela
"""

import ollama
import time
from config import MBTI_PERSONAS


def run_dialogue(model1, model2, initial_prompt, max_rounds=5):
    """Funkcija za dijalog između dva modela"""
    try:
        # Početna poruka
        messages = [{"role": "user", "content": initial_prompt}]
        dialogue_history = []

        for i in range(max_rounds):
            # Prvi model odgovara
            response1 = ollama.chat(model=model1, messages=messages, options={'num_ctx': 4096, 'temperature': 0.7})
            response1_text = response1['message']['content']

            dialogue_history.append({"model": model1, "response": response1_text})

            # Dodajemo odgovor prvog modela u istoriju poruka
            messages.append({"role": "assistant", "content": response1_text})

            # Drugi model odgovara na osnovu prethodne diskusije
            response2 = ollama.chat(model=model2, messages=messages, options={'num_ctx': 4096, 'temperature': 0.7})
            response2_text = response2['message']['content']

            dialogue_history.append({"model": model2, "response": response2_text})

            # Dodajemo odgovor drugog modela u istoriju poruka
            messages.append({"role": "assistant", "content": response2_text})

        return dialogue_history

    except Exception as e:
        return [{"error": f"Greška u dijalogu: {str(e)}"}]


def save_dialogue_to_file(history, topic):
    """Čuva dijalog u fajl"""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"dialogue_{timestamp}.txt"
        # Putanja ka bookcreator folderu ili home folderu
        save_path = f"~/bookcreator/{filename}"

        # Ako bookcreator ne postoji, probaj home
        save_path = f"/home/peterofovik/bookcreator/{filename}"
        try:
            os.makedirs("/home/peterofovik/bookcreator", exist_ok=True)
        except:
            save_path = f"/tmp/{filename}"

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(f"TEMA: {topic}\n")
            f.write(f"DATUM: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")

            for msg in history:
                role = msg.get("role", "unknown")
                model = msg.get("model_name", "Unknown")
                content = msg.get("content", "")
                f.write(f"[{role} - {model}]:\n{content}\n\n")
                f.write("-" * 30 + "\n\n")

        return save_path
    except Exception as e:
        return f"Error: {str(e)}"
