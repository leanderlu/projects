import streamlit as st
from finalbackend import (create_user, validate_user, get_parks, get_park_details, add_review, get_reviews, update_average_ratings, get_parks_state, get_park_name, get_bio, edit_bio, delete_user, delete_reviews)
from cbbackend import (extract_activities, add_activities_to_couchbase)

# ---------------------------
# Section 1: Signup / Signin Page
# ---------------------------

def display_auth_page():
    st.title('US National Parks')
    st.write('Discover the great outdoors with our intuitive park-finder app! Sign up, search, and dive into a world of parks, each with detailed reviews and ratings. Whether you\'re a hiker, camper, or just love nature, our app guides you to your next adventure with ease. Join our community, share your experiences, and find your perfect park getaway. Your next outdoor adventure starts here!')
    st.title("Authentication")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Sign Up"):
        if create_user(username, password):
            st.success("User created successfully.")
        else:
            st.error("Username already exists. Try another.")

    if st.button("Sign In"):
        if validate_user(username, password):
            st.session_state['logged_in'] = True  # Update logged_in state
            st.session_state['username'] = username
            st.session_state['current_page'] = 'parks'  # Direct to parks page
        else:
            st.error("Invalid username or password. Try again.")


# ---------------------------
# Section 2: Parks List Page
# ---------------------------

def display_parks_page():
    user = st.session_state['username']
    st.title(f'Welcome {user}')
    bios = get_bio(user)
    user_bio = bios.one().bio if bios else None
    st.write(user_bio)


    # Add a Sign Out button at the top
    newBio = st.text_input("Bio", key='new_bio_input')
    if st.button('Edit Bio'):
        edit_bio(user, newBio)
        st.experimental_rerun()

    col1, col2 = st.columns([1,1])
    with col1:
        if st.button('Delete User'):
            delete_reviews(user)
            delete_user(user)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['current_page'] = 'auth'  # Redirect to auth page
            st.experimental_rerun()

    with col2:
        if st.button('Sign Out'):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['current_page'] = 'auth'  # Redirect to auth page
            st.experimental_rerun()
    states_list = ["Alaska", "Alabama", "Arkansas", "American Samoa", "Arizona", "California", "Colorado", "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Virginia", "Virgin Islands", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]
    selected_state = st.selectbox('Select states:', states_list)

    if st.button('Show Parks'):
        if selected_state:
            parks = get_parks_state(selected_state)
    else:
        parks = get_parks()
    st.title("Parks")

    for park in parks:
        # Define columns with spacers for dividers
        col1, spacer1, col2, spacer2, col3, spacer3, col4 = st.columns([2, 0.1, 1, 0.1, 4, 0.1, 2])
        
        with col1:
            st.subheader(park[3])  # Name of the park

        with col2:
            st.write(park[2])  # Location of the park

        with col3:
            # Ratings
            st.write(f"Overall: {str(park[6])[0:4]}/5   Hiking: {str(park[5])[0:4]}/5   Camping: {str(park[4])[0:4]}/5")
        
        with col4:
            if st.button("View", key=str(park[0])):
                st.session_state['current_page'] = 'single_park'
                st.session_state['selected_park_id'] = park[0]

        # Optionally, you can add a horizontal line after each park's info
        st.markdown("---")

        
        
        # if st.button("View", key=park['park_id']):
        #     display_park_page(park['park_id'])

# ---------------------------
# Section 3: Single Park Page
# ---------------------------

def display_park_page(park_id):
    # Add a 'Back to Parks List' button at the top
    back_button_key = f'back_to_list_{park_id}'
    if st.button('Back to Parks List', key=back_button_key):
        st.session_state['current_page'] = 'parks'  # Update current_page to 'parks'
        st.experimental_rerun()
        
    # Fetch park details and display them
    park_details = get_park_details(park_id)
    st.title(park_details[3])  # Park name
    st.write(f"Overall: {str(park_details[6])[0:4]}/5   Hiking: {str(park_details[5])[0:4]}/5   Camping: {str(park_details[4])[0:4]}/5")
    st.write("Location:", park_details[2])  # Park location
    st.write("Description:", park_details[1])  # Park description
    

    # Display reviews for the park
    st.subheader("Reviews")
    
    reviews = get_reviews(park_id)
    name = get_park_name(park_id)

    for index, review in enumerate(reviews):
        # Generate a unique key for each text area
        review_text = review.get('review', '')
        activities = extract_activities(review_text)
        add_activities_to_couchbase(activities, name)
        review_key = f"review_{park_id}_{index}"
        st.text_area("Review", review['review'], disabled=True, key=review_key)
        st.caption(f"Rating: {review['rating_overall']} Overall, {review['rating_hiking']} Hiking, {review['rating_camping']} Camping")
        activities_str = ', '.join(activities)
        st.caption(f"Activities: {activities_str}")

    # reviews = get_reviews(park_id)  # Assuming get_park_reviews fetches reviews for a park
    # for review in reviews:
    #     st.text_area("Review", review['review'], disabled=True)

    # Add review functionality
    st.subheader("Add Your Review")
    user_review = st.text_area("Your Review")
    rating_overall = st.slider("Overall Rating", 0, 5, 1)
    rating_hiking = st.slider("Hiking Rating", 0, 5, 1)
    rating_camping = st.slider("Camping Rating", 0, 5, 1)
    submit_button_key = f'submit_review_{park_id}'
    if st.button("Submit Review", key=submit_button_key):
        add_review(st.session_state['username'], park_id, rating_camping, rating_hiking, rating_overall, user_review)
        update_average_ratings(park_id)

        st.success("Review added successfully!")        
        st.experimental_rerun()

        
    


# ---------------------------
# Section A: MAIN
# ---------------------------

def main():
    # Initialize current_page in session_state
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 'auth'

    # Display the appropriate page based on current_page
    if st.session_state['current_page'] == 'auth':
        display_auth_page()
    elif st.session_state['current_page'] == 'parks':
        display_parks_page()
    elif st.session_state['current_page'] == 'single_park':
        display_park_page(st.session_state['selected_park_id'])


if __name__ == "__main__":
    main()