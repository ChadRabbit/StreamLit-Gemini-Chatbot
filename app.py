import streamlit as st
import requests

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'session_cookies' not in st.session_state:
    st.session_state['session_cookies'] = None
if 'mode' not in st.session_state:
    st.session_state['mode'] = 'login'  # Default to login mode

def login(username, password):
    response = requests.post('http://127.0.0.1:8000/login', data={'username': username, 'password': password})

    if response.status_code == 200:
        try:
            response_data = response.json()
            if 'error_message' in response_data and response_data['error_message']:
                st.error("Invalid credentials. Please try again.")
            else:
                st.session_state['logged_in'] = True
                st.session_state['username'] = response_data['username']
                st.session_state['session_cookies'] = response.cookies
                st.session_state['mode'] = 'chat'

        except requests.exceptions.JSONDecodeError:
            st.error("Error: Server response was not valid JSON.")
    else:
        st.error(f"Error: Received unexpected status code {response.status_code}")

def register(username, password, email):
    response = requests.post('http://127.0.0.1:8000/register', data={'username': username, 'password1': password, 'email': email, 'password2': password})

    if response.status_code == 200:
        try:
            response_data = response.json()
            if 'error_message' in response_data and response_data['error_message']:
                st.error("Registration failed. Please try again.")
            else:
                st.session_state['logged_in'] = True
                st.session_state['username'] = response_data['username']
                st.session_state['session_cookies'] = response.cookies
                st.session_state['mode'] = 'chat'

        except requests.exceptions.JSONDecodeError:
            st.error("Error: Server response was not valid JSON.")
    else:
        st.error(f"Error: Received unexpected status code {response.status_code}")

def get_chats(message=""):
    response = requests.post('http://127.0.0.1:8000/chats', data={'user': st.session_state.get('username'), 'message': message}, cookies=st.session_state.get('session_cookies'))

    if response.status_code == 200:
        try:
            chats = response.json()
            return chats.get('chats', [])
        except requests.exceptions.JSONDecodeError:
            st.error("Error: Could not retrieve chat data.")
    else:
        st.error(f"Error: Received unexpected status code {response.status_code}")

# Main content based on user authentication state
if not st.session_state['logged_in']:
    # Mode selector outside the form
    st.session_state['mode'] = st.radio(
        "Select mode",
        ('login', 'register'),
        index=0 if st.session_state['mode'] == 'login' else 1
    )

    if st.session_state['mode'] == 'login':
        with st.form(key='login_form'):
            st.markdown("#### Login")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            if submit:
                login(username, password)

    elif st.session_state['mode'] == 'register':
        with st.form(key='register_form'):
            st.markdown("#### Register")
            username = st.text_input("Username", key="reg_username")
            email = st.text_input("Email Address", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            submit = st.form_submit_button("Register")
            if submit:
                register(username, password, email)
else:
    st.markdown(f"### Welcome, {st.session_state['username']}!")

    chats = get_chats()

    if chats:
        st.markdown("#### Chat History:")
        for chat in chats:
            with st.chat_message("user"):
                st.write(chat['message'])
            with st.chat_message("assistant"):
                st.write(chat['response'])
    else:
        with st.chat_message("assistant"):
            st.write("How can I help you today?")

    prompt = st.chat_input("Say something")
    if prompt:
        new_chat = get_chats(message=prompt)
        if new_chat:
            with st.chat_message("user"):
                st.write(new_chat[-1]['message'])
            with st.chat_message("assistant"):
                st.write(new_chat[-1]['response'])
