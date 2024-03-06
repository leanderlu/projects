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
    session.execute("INSERT INTO users (username, password, bio) VALUES (%s, %s, 'empty bio')", [username, password])

    return True

def validate_user(username, password):
    user = session.execute("SELECT * FROM users WHERE username=%s AND password=%s ALLOW FILTERING", [username, password])
    if user.one():
        return True
    else:
        return False


# ---------------------------
# Section 2: Gets and adds for users
# ---------------------------
def get_bio(user):
    query = f"SELECT bio FROM users WHERE username = '{user}' ALLOW FILTERING;"
    bios = session.execute(query)
    return bios

def edit_bio(user, newBio):
    query = f"UPDATE users SET bio = '{newBio}' WHERE username = '{user}';"
    session.execute(query)
    return True

def delete_user(user):
    query = f"DELETE FROM users WHERE username = '{user}';"
    session.execute(query)
    return True

def delete_reviews(user):
    select_query = f"SELECT review_id FROM destinations_visited WHERE username = '{user}' ALLOW FILTERING;"
    review_ids = session.execute(select_query)
    for row in review_ids:
        delete_query = f"DELETE FROM destinations_visited WHERE review_id = {row.review_id};"
        session.execute(delete_query)

    return True

def get_parks():
    parks = list(session.execute("SELECT * FROM parks"))
    return parks

def get_parks_state(state):
    # Execute the query with the formatted state
    query = f"SELECT * FROM parks WHERE location = '{state}' ALLOW FILTERING;"
    parks = session.execute(query)
    return parks

def get_park_details(park_id):
    return session.execute("SELECT * FROM parks WHERE park_id=%s", [park_id]).one()

def get_park_name(park_id):
    return session.execute("SELECT name FROM parks WHERE park_id=%s", [park_id]).one()

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
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, [review_id, username, park_id, review, rating_overall, rating_camping, rating_hiking])
    # Update average ratings in the parks table after adding the review (additional logic needed here)
    # search for activities in the review
    # add these activities to new database
    
def update_average_ratings(park_id):
    # Retrieve all reviews for the given park
    reviews = session.execute("SELECT rating_overall, rating_hiking, rating_camping FROM destinations_visited WHERE park_ID=%s ALLOW FILTERING", [park_id]).all()

    # Calculate the average ratings
    avg_rating_overall = sum([review.rating_overall for review in reviews]) / len(reviews)
    avg_rating_hiking = sum([review.rating_hiking for review in reviews]) / len(reviews)
    avg_rating_camping = sum([review.rating_camping for review in reviews]) / len(reviews)

    # Update the park's average ratings in the parks table
    session.execute("UPDATE park.parks SET rating_overall=%s, rating_hiking=%s, rating_camping=%s WHERE park_ID=%s",
                    [avg_rating_overall, avg_rating_hiking, avg_rating_camping, park_id])

