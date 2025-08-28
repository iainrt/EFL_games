import json
import traceback
from pathlib import Path
from supabase_client import supabase

SESSION_FILE = Path(".session.json")


def try_auto_login(on_success):
    """
    Attempt to restore session from saved token.
    Calls on_success(user_id) if valid, returns True.
    Returns False otherwise.
    """
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

    # Instead of passing None or "", manually clear the Authorization header
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
    """Log out current user and clear session."""
    try:
        supabase.auth.sign_out()
    except Exception as ex:
        print("⚠️ Error during supabase sign_out:", ex)

    clear_session()
    print("👋 User logged out successfully")


# --- Authentication helpers ---
def safe_sign_in(email: str, password: str):
    try:
        return supabase.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as ex:
        print(f"❌ safe_sign_in failed for {email}:", ex)
        traceback.print_exc()
        return None


def safe_sign_up(email: str, password: str):
    try:
        return supabase.auth.sign_up({"email": email, "password": password})
    except Exception as ex:
        print(f"❌ safe_sign_up failed for {email}:", ex)
        traceback.print_exc()
        return None
    
# --- Password reset ---
def safe_reset_password(email: str):
    """Send a password reset email safely."""
    try:
        return supabase.auth.reset_password_for_email(email)
    except Exception as ex:
        print(f"❌ safe_reset_password failed for {email}:", ex)
        traceback.print_exc()
        return None


# --- User info ---
def get_current_user() -> dict | None:
    """
    Returns a dict like:
    {
        "id": "...",
        "email": "...",
        "user_metadata": {...}
    }
    or None if not logged in.
    """
    try:
        # Ensure token is applied / refreshed if needed
        apply_saved_token()

        res = supabase.auth.get_user()
        u = getattr(res, "user", None) if res else None
        if not u:
            return None

        # Try to access as object, then as dict; normalize to dict
        try:
            meta = dict(u.user_metadata or {})
            uid = getattr(u, "id", None)
            email = getattr(u, "email", None)
        except Exception:
            # Fallback if u is already a dict-like
            u = dict(u)
            meta = dict(u.get("user_metadata") or {})
            uid = u.get("id")
            email = u.get("email")

        return {"id": uid, "email": email, "user_metadata": meta}
    except Exception as ex:
        print("⚠️ get_current_user failed:", ex)
        return None

