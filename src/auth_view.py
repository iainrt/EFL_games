import flet as ft
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json
from pathlib import Path

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # use anon key here
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def try_auto_login(on_success):
    session_file = Path(".session.json")
    if session_file.exists():
        try:
            saved = json.loads(session_file.read_text())

            # Restore session from saved tokens
            res = supabase.auth.set_session(saved["access_token"], saved["refresh_token"])

            if res.user and res.session:
                user_id = res.user.id
                access_token = res.session.access_token

                print("✅ Auto-login: User ID:", user_id)
                print("✅ Auto-login: Access token applied:", access_token[:40])

                # ✅ Authorize PostgREST client for RLS to work
                supabase.postgrest.auth(access_token)

                on_success(user_id)
                return True
            else:
                print("❌ Session or user missing")
                session_file.unlink(missing_ok=True)
        except Exception as ex:
            print("❌ Auto-login error:", ex)
            session_file.unlink(missing_ok=True)
    return False

def auth_view(page: ft.Page, on_login_success):
    email_input = ft.TextField(label="Email", width=300)
    password_input = ft.TextField(label="Password", password=True, width=300)
    status_text = ft.Text("", color=ft.Colors.RED)

    def do_login(e):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email_input.value,
                "password": password_input.value
            })
            user_id = res.user.id

            # ✅ Ensure authenticated requests work
            supabase.postgrest.auth(res.session.access_token)

            # Save session to disk
            session_file = Path(".session.json")
            session_file.write_text(res.session.model_dump_json())

            status_text.value = "✅ Login successful!"
            status_text.color = ft.Colors.GREEN
            page.update()

            on_login_success(user_id)

        except Exception as ex:
            status_text.value = f"❌ Login failed: {ex}"
            status_text.color = ft.Colors.RED
            page.update()

    def do_signup(e):
        try:
            res = supabase.auth.sign_up({
                "email": email_input.value,
                "password": password_input.value
            })

            # Save session to disk
            session_file = Path(".session.json")
            session_file.write_text(res.session.model_dump_json())

            # ✅ Set postgrest auth token for RLS to work
            supabase.postgrest.auth(res.session.access_token)
            
            status_text.value = "✅ Signup successful! Please log in."
            status_text.color = ft.Colors.GREEN
            page.update()
        except Exception as ex:
            status_text.value = f"❌ Signup failed: {ex}"
            status_text.color = ft.Colors.RED
            page.update()

    page.add(
        ft.Column([
            ft.Text("🔐 Log In or Sign Up", size=24, weight=ft.FontWeight.BOLD),
            email_input,
            password_input,
            ft.Row([
                ft.ElevatedButton("Log In", on_click=do_login),
                ft.TextButton("Sign Up", on_click=do_signup),
            ]),
            status_text
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )
