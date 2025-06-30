import flet as ft
from auth_view import auth_view, try_auto_login
from efl_1_to_24s import efl_1_to_24s_view

def main(page: ft.Page):
    page.title = "EFL Prediction Games"
    page.padding = 30
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    def launch_efl_1_to_24s():
        page.clean()
        auth_view(page, on_login_success=efl_1_to_24s_entry)

    def efl_1_to_24s_entry(user_id):
        page.clean()
        efl_1_to_24s_view(page, user_id=user_id)

    # 🔁 Try auto-login and enter app immediately
    if try_auto_login(efl_1_to_24s_entry):
        return

    games = [
        {"title": "EFL 1 to 24s", "launch": launch_efl_1_to_24s, "coming_soon": False},
        {"title": "Last Man Standing", "coming_soon": True},
        {"title": "Season Prediction", "coming_soon": True},
        {"title": "Snakes and Ladders", "coming_soon": True},
    ]

    tiles = []
    for game in games:
        tiles.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(game["title"], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("COMING SOON" if game.get("coming_soon") else "", italic=True, color=ft.Colors.GREY),
                            ft.ElevatedButton(
                                "View",
                                on_click=lambda e, f=game.get("launch"): f() if f else None,
                                disabled=game.get("coming_soon", True)
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=20,
                    width=300,
                ),
                elevation=4,
            )
        )

    page.add(
        ft.Column(
            [
                ft.Text("EFL Prediction Games", size=30, weight=ft.FontWeight.BOLD),
                ft.Text("Choose a game mode below", size=16),
                ft.ResponsiveRow(tiles, alignment=ft.MainAxisAlignment.CENTER),
            ],
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    )

ft.app(target=main)
