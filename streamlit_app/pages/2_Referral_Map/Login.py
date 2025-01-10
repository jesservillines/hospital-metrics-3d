import streamlit as st
import yaml
from pathlib import Path
import hashlib

def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    if not config_path.exists():
        # Create default config if it doesn't exist
        default_config = {
            'credentials': {
                'usernames': {
                    'admin': {
                        'name': 'Admin User',
                        'password': hashlib.sha256('admin'.encode()).hexdigest()
                    }
                }
            }
        }
        with open(config_path, 'w') as file:
            yaml.dump(default_config, file)
    
    with open(config_path) as file:
        config = yaml.safe_load(file)
    return config

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in config["credentials"]["usernames"]:
            user = config["credentials"]["usernames"][st.session_state["username"]]
            if hashlib.sha256(st.session_state["password"].encode()).hexdigest() == user["password"]:
                st.session_state["authentication_status"] = True
                st.session_state["name"] = user["name"]
            else:
                st.session_state["authentication_status"] = False
        else:
            st.session_state["authentication_status"] = False

    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None

    # First run, show inputs for username + password.
    if st.session_state["authentication_status"] != True:
        config = load_config()
        st.title("Login")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)

        if st.session_state["authentication_status"] == False:
            st.error("😕 User not known or password incorrect")
    
    return st.session_state["authentication_status"]

def main():
    if check_password():
        st.success(f'Welcome *{st.session_state["name"]}*')
        st.info('You can now access the other pages using the sidebar.')

if __name__ == "__main__":
    main()
