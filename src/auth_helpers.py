import json
from pathlib import Path
from supabase_client import supabase
import traceback

def apply_saved_token() -> str | None:
    """
    Loads the saved access_token from .session.json and applies it to PostgREST.
    Returns the user ID if successful, else None.
    """
    session_file = Path(".session.json")
    if session_file.exists():
        try:
            saved = json.loads(session_file.read_text())
            access_token = saved.get("access_token")
            refresh_token = saved.get("refresh_token")

            # Update both auth and PostgREST
            session = supabase.auth.set_session(access_token, refresh_token)
            if session and session.session and session.user:
                supabase.postgrest.auth(session.session.access_token)
                return session.user.id
            else:
                print("⚠️ Invalid session returned from set_session")
        except Exception as ex:
            print("❌ Failed to apply saved token:", ex)
            session_file.unlink(missing_ok=True)
    return None

def save_session_and_auth(session):
    """
    Saves session to .session.json and applies access_token to PostgREST.
    """
    Path(".session.json").write_text(session.model_dump_json())
    supabase.postgrest.auth(session.access_token)

def clear_session():
    Path(".session.json").unlink(missing_ok=True)

def safe_sign_in(email: str, password: str):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as ex:
        print("❌ Sign-in failed:")
        traceback.print_exc()
        return None

def safe_sign_up(email: str, password: str):
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as ex:
        print("❌ Sign-up failed:")
        traceback.print_exc()
        return None

