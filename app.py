from flask import Flask, request, jsonify, render_template #type:ignore
from flask_cors import CORS #type:ignore
from sentence_transformers import SentenceTransformer, util #type:ignore#type:ignore
import json
import os
import random
import torch #type:ignore

app = Flask(__name__)
CORS(app)

INTENTS_PATH = 'intents.json' 
EMBEDDINGS_PATH = 'embeddings.pt' 
model = SentenceTransformer('all-MiniLM-L6-v2')
SIMILARITY_THRESHOLD = 0.55 
try:
    data = torch.load(EMBEDDINGS_PATH)
    embeddings = data['embeddings']
    patterns = data['patterns']
    responses_map = data['responses_map']
    print(f"✅ Embeddings and data loaded successfully from {EMBEDDINGS_PATH}.")
except FileNotFoundError:
    print(f"FATAL ERROR: {EMBEDDINGS_PATH} not found. Please run 'python train.py' first.")
    embeddings = torch.tensor([])
    patterns = []
    responses_map = {}
except KeyError as e:
    print(f"FATAL ERROR: Missing key in {EMBEDDINGS_PATH}. This usually means the file was created with an older script. Please re-run 'python train.py'. Missing key: {e}")
    embeddings = torch.tensor([])
    patterns = []
    responses_map = {}
except Exception as e:
    print(f"FATAL ERROR: An unexpected error occurred while loading embeddings: {e}")
    embeddings = torch.tensor([])
    patterns = []
    responses_map = {}


def get_best_match(query):
    """
    Finds the best matching pattern from the loaded dataset for a given query.
    Returns the index of the best match and its similarity score.
    Returns -1, 0.0 if no patterns are loaded.
    """
    if not len(embeddings):
        return -1, 0.0

    query_embedding = model.encode(query, convert_to_tensor=True)
    scores = util.cos_sim(query_embedding, embeddings)[0]
    best_idx = torch.argmax(scores).item()
    best_score = scores[best_idx].item()
    return best_idx, best_score

@app.route("/")
def home():
    """Renders the main HTML page for the chatbot."""
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    """
    Receives user message and predicts response ONLY from the dataset.
    """
    user_data = request.get_json()
    message = user_data.get("message", "").strip()

    if not message:
        return jsonify({"answer": "Please enter a message.", "matched_pattern": "", "source": "system"})

    best_idx, best_score = get_best_match(message)

    if best_score >= SIMILARITY_THRESHOLD:
        matched_pattern = patterns[best_idx]
        answer = random.choice(responses_map.get(matched_pattern, ["I'm sorry, I don't have a specific answer for that right now. This response is from your dataset fallback."]))
        return jsonify({
            "answer": answer,
            "matched_pattern": matched_pattern, 
            "source": "dataset" 
        })
    else:
        print(f"Score ({best_score:.2f}) below threshold ({SIMILARITY_THRESHOLD}). No confident dataset match.")
        return jsonify({
            "answer": "I'm sorry, I don't have a specific answer for that right now. Please try asking about banking app features.",
            "matched_pattern": message,
            "source": "system_fallback" 
        })

@app.route("/retrain", methods=["POST"])
def retrain():
    """
    Endpoint to trigger a 'retrain' action.
    NOTE: In this setup, 'retrain' on app.py only reloads embeddings.
    To truly retrain (i.e., re-generate embeddings), you must run train.py.
    """
    print("Attempting to reload embeddings...")
    global data, embeddings, patterns, responses_map 
    try:
        data = torch.load(EMBEDDINGS_PATH)
        embeddings = data['embeddings']
        patterns = data['patterns']
        responses_map = data['responses_map']
        print("Embeddings reloaded successfully.")
        return jsonify({"status": "Embeddings reloaded."})
    except FileNotFoundError:
        return jsonify({"status": f"Error: {EMBEDDINGS_PATH} not found. Run 'python train.py' first."}), 500
    except Exception as e:
        print(f"Error reloading embeddings: {e}")
        return jsonify({"status": f"Error reloading embeddings: {e}. Check console for details."}), 500

if __name__ == "__main__":
    app.run(debug=True)

