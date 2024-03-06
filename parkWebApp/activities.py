import spacy

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def extract_activities(text):
    # List of activity-related verbs to look for
    activity_verbs = ["hike", "kayak", "stroll", "walk", "run", "swim", "cycle", "climb", "paddle", "explore", "ski", "sail", "fish", "camp", "canoe", "trek"]

    # Process the text
    doc = nlp(text)

    activities = []

    # Iterate over sentences
    for sentence in doc.sents:
        # Iterate over each token
        for token in sentence:
            # Check if the token is a verb and if it is in our list of activity verbs
            if token.lemma_ in activity_verbs:
                activities.append(token.text)

    return activities

# Need to get text from review
text = "Isle Royale National Park is an unparalleled escape into nature, and my day there was nothing short of magical. Starting with a serene sunrise kayak along the rugged coastline, I was mesmerized by the pristine waters and the symphony of wildlife. Hiking through the dense forests in the afternoon, I encountered fascinating flora and glimpses of moose and foxes. The Greenstone Ridge Trail offered breathtaking vistas that were a photographer's dream. Unwinding at Rock Harbor with a peaceful evening stroll, I felt a profound connection with the untouched wilderness. Isle Royale is a true gem, perfect for adventurers seeking solitude and natural beauty."

# Extract activities and send activities to couchbase db
activities = extract_activities(text)
print("Extracted Activities:", activities)