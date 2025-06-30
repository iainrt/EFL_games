import flet as ft
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")  # use anon key here
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
            status_text.value = "✅ Login successful!"
            status_text.color = ft.Colors.GREEN
            page.update()
            on_login_success(user_id)  # callback to enter app
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
