import flet as ft
from supabase import create_client, Client
from supabase_client import supabase
import os
from dotenv import load_dotenv
from pathlib import Path
from auth_helpers import save_session_and_auth, clear_session
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # use anon key here
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def try_auto_login(on_success):
    session_file = Path(".session.json")
    if session_file.exists():
        try:
            saved = json.loads(session_file.read_text())

            res = supabase.auth.set_session(saved["access_token"], saved["refresh_token"])

            if res.user and res.session:
                user_id = res.user.id
                save_session_and_auth(res.session)

                print("✅ Auto-login: User ID:", user_id)
                print("✅ Auto-login: Access token applied:", res.session.access_token[:40])

                on_success(user_id)
                return True
            else:
                print("❌ Session or user missing")
                clear_session()
        except Exception as ex:
            print("❌ Auto-login error:", ex)
            clear_session()
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

            save_session_and_auth(res.session)

            status_text.value = "✅ Login successful!"
            status_text.color = ft.Colors.GREEN
            page.update()

            on_login_success(res.user.id)

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

            save_session_and_auth(res.session)

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
