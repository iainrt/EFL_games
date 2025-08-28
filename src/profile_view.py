import flet as ft
from supabase_client import supabase
from auth_helpers import get_current_user, apply_saved_token


def profile_view(page: ft.Page, refresh_nav=None):
    user = get_current_user()
    if not user:
        return ft.Text("⚠️ Not logged in", color=ft.Colors.RED)

    email = user.get("email", "")
    display_name = user.get("user_metadata", {}).get("display_name", "")

    display_name_input = ft.TextField(label="Display Name", value=display_name, width=300)
    status_text = ft.Text("", color=ft.Colors.RED)

    # --- Change password fields ---
    new_pw_input = ft.TextField(label="New Password", password=True, width=300)
    confirm_pw_input = ft.TextField(label="Confirm Password", password=True, width=300)
    pw_status = ft.Text("", color=ft.Colors.RED)

    def save_profile(e):
        try:
            new_name = display_name_input.value.strip()
            res = supabase.auth.update_user({"data": {"display_name": new_name}})

            if res and res.user:
                status_text.value = "✅ Profile updated!"
                status_text.color = ft.Colors.GREEN
                if refresh_nav:
                    refresh_nav()
            else:
                status_text.value = "❌ Failed to update profile"
                status_text.color = ft.Colors.RED
        except Exception as ex:
            status_text.value = f"❌ Error: {ex}"
            status_text.color = ft.Colors.RED
        page.update()

    def change_password(e):
        if new_pw_input.value != confirm_pw_input.value:
            pw_status.value = "❌ Passwords do not match"
            pw_status.color = ft.Colors.RED
            page.update()
            return

        try:
            res = supabase.auth.update_user({"password": new_pw_input.value})
            if res and res.user:
                pw_status.value = "✅ Password updated successfully"
                pw_status.color = ft.Colors.GREEN
            else:
                pw_status.value = "❌ Failed to update password"
                pw_status.color = ft.Colors.RED
        except Exception as ex:
            pw_status.value = f"❌ Error: {ex}"
            pw_status.color = ft.Colors.RED
        page.update()

    return ft.Column(
        [
            ft.Text("👤 Profile", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Email: {email}", size=16),

            ft.Divider(),
            ft.Text("Update Display Name", weight=ft.FontWeight.BOLD),
            display_name_input,
            ft.ElevatedButton("Save Profile", on_click=save_profile),
            status_text,

            ft.Divider(),
            ft.Text("Change Password", weight=ft.FontWeight.BOLD),
            new_pw_input,
            confirm_pw_input,
            ft.ElevatedButton("Change Password", on_click=change_password),
            pw_status,
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
