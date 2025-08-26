import json
import traceback
from pathlib import Path
from supabase_client import supabase

SESSION_FILE = Path(".session.json")


def try_auto_login(on_success):
    """Attempt to restore session from saved token."""
    user_id = apply_saved_token()
    if user_id:
        print(f"✅ Auto-login succeeded: {user_id}")
        on_success(user_id)
        return True
    return False


def save_session_and_auth(session):
    """Save session to disk and apply PostgREST auth header."""
    SESSION_FILE.write_text(session.model_dump_json())
    supabase.postgrest.auth(session.access_token)


def clear_session():
    """Remove local session file and reset PostgREST auth header."""
    SESSION_FILE.unlink(missing_ok=True)

    # Manually clear PostgREST token
    if "Authorization" in supabase.postgrest.headers:
        del supabase.postgrest.headers["Authorization"]


def apply_saved_token() -> str | None:
    """
    Ensures PostgREST has a valid token.
    If access_token is expired, it tries to refresh with refresh_token.
    Returns the user ID if successful, else None.
    """
    if SESSION_FILE.exists():
        try:
            saved = json.loads(SESSION_FILE.read_text())
            access_token = saved.get("access_token")
            refresh_token = saved.get("refresh_token")

            res = supabase.auth.set_session(access_token, refresh_token)

            if res and res.session and res.user:
                save_session_and_auth(res.session)
                return res.user.id
            else:
                clear_session()
        except Exception as ex:
            print("❌ apply_saved_token failed:", ex)
            traceback.print_exc()
            clear_session()
    return None


def logout_user():
    """Logs out the current user and clears local session."""
    try:
        supabase.auth.sign_out()
    except Exception as ex:
        print("⚠️ Error during supabase sign_out:", ex)
    clear_session()
    print("👋 User logged out successfully")


# --- Authentication helpers ---
def safe_sign_in(email: str, password: str):
    """Safely attempt sign-in, return result or None on failure."""
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as ex:
        print(f"❌ safe_sign_in failed for {email}:", ex)
        traceback.print_exc()
        return None


def safe_sign_up(email: str, password: str):
    """Safely attempt sign-up, return result or None on failure."""
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as ex:
        print(f"❌ safe_sign_up failed for {email}:", ex)
        traceback.print_exc()
        return None


def get_current_user():
    """
    Always return the freshest authenticated user from Supabase.
    Returns a User object or None.
    """
    try:
        user = supabase.auth.get_user()
        if user and user.user:
            return user.user
    except Exception as ex:
        print("❌ get_current_user failed:", ex)
        traceback.print_exc()
    return None
