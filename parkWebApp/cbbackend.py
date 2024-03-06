from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
import spacy

cluster = Cluster('couchbase://127.0.0.1', ClusterOptions(PasswordAuthenticator('leanderlu', '123456')))
bucket = cluster.bucket('activities')
collection = bucket.default_collection()

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

def add_activities_to_couchbase(activities, park_name):
    # Create a document structure
    document = {
        "park_name": park_name,
        "activitiy_type": activities
    }
    # Generate a unique document ID
    document_id = f"park_activities_{park_name}"
    # Insert document into Couchbase bucket
    collection.upsert(document_id, document)

