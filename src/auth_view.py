import flet as ft
from auth_helpers import save_session_and_auth, safe_sign_in, safe_sign_up
from supabase_client import supabase


def auth_view(page: ft.Page, on_login_success):
    email_input = ft.TextField(label="Email", width=300)
    password_input = ft.TextField(label="Password", password=True, width=300)
    status_text = ft.Text("", color=ft.Colors.RED)

    def do_login(e):
        res = safe_sign_in(email_input.value, password_input.value)
        if res and res.session and res.user:
            save_session_and_auth(res.session)
            status_text.value = "✅ Login successful!"
            status_text.color = ft.Colors.GREEN
            page.update()
            on_login_success(res.user.id)
        else:
            status_text.value = "❌ Login failed. Check credentials or try again."
            status_text.color = ft.Colors.RED
            page.update()

    def do_signup(e):
        res = safe_sign_up(email_input.value, password_input.value)
        if res and res.session:
            save_session_and_auth(res.session)
            status_text.value = (
                "✅ Signup successful! Please check your email to confirm your account."
            )
            status_text.color = ft.Colors.GREEN
        else:
            status_text.value = "❌ Signup failed. Email may already be in use."
            status_text.color = ft.Colors.RED
        page.update()

    def do_forgot_password(e):
        if not email_input.value:
            status_text.value = "⚠️ Please enter your email first."
            status_text.color = ft.Colors.RED
            page.update()
            return

        try:
            supabase.auth.reset_password_for_email(email_input.value)
            status_text.value = (
                f"📩 Password reset link sent to {email_input.value}. "
                "Check your email."
            )
            status_text.color = ft.Colors.GREEN
        except Exception as ex:
            status_text.value = f"❌ Failed to send reset link: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    return ft.Row(
        [
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "🔐 Log In or Sign Up",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            email_input,
                            password_input,
                            ft.Row(
                                [
                                    ft.ElevatedButton("Log In", on_click=do_login),
                                    ft.TextButton("Sign Up", on_click=do_signup),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.TextButton(
                                "Forgot Password?",
                                on_click=do_forgot_password,
                                style=ft.ButtonStyle(color=ft.Colors.BLUE),
                            ),
                            status_text,
                        ],
                        spacing=15,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=20,
                    width=400,
                ),
                elevation=4,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
    )
