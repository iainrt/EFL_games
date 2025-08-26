import flet as ft
from supabase_client import supabase
from auth_helpers import get_current_user


def profile_view(page: ft.Page, on_profile_updated):
    user = get_current_user()
    if not user:
        return ft.Text("❌ Not logged in")

    # Pre-fill display name from Supabase metadata if it exists
    display_name_input = ft.TextField(
        label="Display Name",
        value=user.user_metadata.get("display_name", "") if user.user_metadata else "",
        width=300,
    )

    email_display = ft.Text(f"📧 {user.email}", size=16)
    status_text = ft.Text("", color=ft.Colors.RED)

    def save_display_name(e):
        try:
            res = supabase.auth.update_user(
                {"data": {"display_name": display_name_input.value}}
            )

            if res and res.user:
                status_text.value = "✅ Display name updated!"
                status_text.color = ft.Colors.GREEN
                # 🔄 Immediately refresh nav bar
                on_profile_updated()
            else:
                status_text.value = "❌ Failed to update display name."
                status_text.color = ft.Colors.RED
        except Exception as ex:
            status_text.value = f"❌ Error: {ex}"
            status_text.color = ft.Colors.RED

        page.update()

    return ft.Column(
        [
            ft.Text("👤 User Profile", size=24, weight=ft.FontWeight.BOLD),
            email_display,
            display_name_input,
            ft.Row(
                [
                    ft.ElevatedButton("Save", on_click=save_display_name),
                ]
            ),
            status_text,
        ],
        spacing=20,
        horizontal_alignment=ft.CrossAxisAlignment.START,
    )
