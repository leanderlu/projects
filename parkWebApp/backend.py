from cassandra.cluster import Cluster
from uuid import uuid4

# Initialize Cassandra connection
cluster = Cluster(['127.0.0.1'])
session = cluster.connect('park')

# ---------------------------
# Section 1: Sign Up / Sign In
# ---------------------------

def create_user(username, password):
    existing_user = session.execute("SELECT * FROM users WHERE username=%s", [username]).one()
    if existing_user:
        return False
    session.execute("INSERT INTO users (username, password) VALUES (%s, %s)", [username, password])
    return True

def validate_user(username, password):
    user = session.execute("SELECT * FROM users WHERE username=%s AND password=%s ALLOW FILTERING", [username, password])
    if user.one():
        return True
    else:
        return False

def is_admin(username):
    # Assuming admin check is based on a predefined username
    return username == "admin"

# ---------------------------
# Section 2: Parks List
# ---------------------------

def get_parks():
    parks = list(session.execute("SELECT * FROM parks"))
    print(parks[0])
    return parks

def get_parks_state(state):
    # Execute the query with the formatted state
    query = f"SELECT * FROM parks WHERE location = '{state}' ALLOW FILTERING;"
    parks = session.execute(query)
    return parks
# ---------------------------
# Section 3: Single Park Page
# ---------------------------

def get_park_details(park_id):
    return session.execute("SELECT * FROM parks WHERE park_id=%s", [park_id]).one()

def get_park_name(park_id):
    return session.execute("SELECT name FROM parks WHERE park_id=%s", [park_id]).one()

# ---------------------------
# Section 4: Admin Operations
# ---------------------------

def add_park(name, location, description, rating_overall, rating_hiking, rating_camping):
    park_id = uuid4()
    session.execute("""
    INSERT INTO parks (park_id, name, location, description, rating_overall, rating_hiking, rating_camping)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [park_id, name, location, description, rating_overall, rating_hiking, rating_camping])

def delete_park(park_id):
    session.execute("DELETE FROM parks WHERE park_id=%s", [park_id])

def modify_park(park_id, name, location, description, rating_overall, rating_hiking, rating_camping):
    session.execute("""
    UPDATE parks SET name=%s, location=%s, description=%s, rating_overall=%s, rating_hiking=%s, rating_camping=%s
    WHERE park_id=%s
    """, [name, location, description, rating_overall, rating_hiking, rating_camping, park_id])

def delete_user(username):
    session.execute("DELETE FROM users WHERE username=%s", [username])

def delete_review(username, park_id):
    session.execute("DELETE FROM destinations_visited WHERE username=%s AND park_id=%s", [username, park_id])

# Additional helper functions and logic for updating ratings, etc., can be added as needed

# ---------------------------
# Section 3: Get Reviews
# ---------------------------

def get_reviews(park_id):
    query = "SELECT * FROM destinations_visited WHERE park_ID=%s ALLOW FILTERING"
    rows = session.execute(query, [park_id])

    reviews = []
    for row in rows:
        review = {
            'username': row.username,
            'review': row.review,
            'rating_overall': row.rating_overall,
            'rating_camping': row.rating_camping,
            'rating_hiking': row.rating_hiking
        }
        reviews.append(review)
    
    return reviews

def add_review(username, park_id, review, rating_overall, rating_camping, rating_hiking):
    review_id = uuid4()
    session.execute("""
    INSERT INTO destinations_visited (review_id, username, park_id, rating_camping, rating_hiking, rating_overall, review)
    VALUES (%s, %s, %s, %s, %s, %s)
    """, [username, park_id, review, rating_overall, rating_camping, rating_hiking])
    # Update average ratings in the parks table after adding the review (additional logic needed here)
    # search for activities in the review
    # add these activities to new database
    

