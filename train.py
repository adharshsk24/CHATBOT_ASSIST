from sentence_transformers import SentenceTransformer, util # type: ignore
import json
import os
import torch # type: ignore

INTENTS_PATH = 'intents.json'
EMBEDDINGS_PATH = 'embeddings.pt'

# Load the SentenceTransformer model for embedding generation
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_intents():
    """Loads intents from the JSON file."""
    try:
        with open(INTENTS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {INTENTS_PATH} not found. Please ensure it exists in the same directory as train.py.")
        return {"intents": []}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {INTENTS_PATH}: {e}. Please check your JSON syntax.")
        return {"intents": []}

def prepare_embeddings():
    """
    Prepares and saves sentence embeddings for intent matching.
    This assumes 'patterns' and 'responses' are direct lists within each intent.
    """
    print("Loading intents from intents.json...")
    intents_data = load_intents()
    corpus = []
    responses_map = {} 
    
    if not intents_data or not intents_data.get('intents'):
        print("Warning: No intents found in intents.json or it's empty. Using a default pattern for embeddings.")
        corpus.append("default banking query")
        responses_map["default banking query"] = ["I am a banking assistant. Please provide more training data in your intents.json to improve my responses."]
    else:
        for intent in intents_data['intents']:
            # Assuming patterns and responses are direct lists for each intent
            for pattern in intent['patterns']:
                corpus.append(pattern)
                responses_map[pattern] = intent['responses'] 
    
    if not corpus:
        print("Error: No patterns found to create embeddings. Ensure your intents.json has patterns.")
        return

    print("Encoding patterns to generate embeddings (this may take a moment)...")
    embeddings = model.encode(corpus, convert_to_tensor=True)
    
    torch.save({
        'embeddings': embeddings,
        'patterns': corpus,
        'responses_map': responses_map
    }, EMBEDDINGS_PATH)
    print(f"✅ Embeddings prepared and saved to {EMBEDDINGS_PATH}.")

if __name__ == "__main__":
    prepare_embeddings() 
