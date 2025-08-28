import flet as ft
from supabase_client import supabase
from auth_helpers import get_current_user


def profile_view(page: ft.Page, refresh_nav):
    user = get_current_user()
    if not user:
        return ft.Text("❌ No user logged in")

    email = user["email"]
    display_name = user["user_metadata"].get("display_name", "")

    name_input = ft.TextField(label="Display Name", value=display_name, width=300)

    def save_profile(e):
        new_name = name_input.value.strip()
        res = supabase.auth.update_user({"data": {"display_name": new_name}})
        if res and getattr(res, "user", None):
            page.snack_bar = ft.SnackBar(ft.Text("✅ Profile updated"))
            page.snack_bar.open = True
            page.update()
            refresh_nav()  # ✅ immediately refresh navbar
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Failed to update profile"))
            page.snack_bar.open = True
            page.update()

    return ft.Column(
        [
            ft.Text("👤 User Profile", size=24, weight=ft.FontWeight.BOLD),
            ft.Text(f"Email: {email}", size=16),
            name_input,
            ft.ElevatedButton("Save", on_click=save_profile),
        ],
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
