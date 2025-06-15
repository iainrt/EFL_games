import flet as ft

def main(page: ft.Page):
    page.title = "EFL Prediction Games"
    page.padding = 30
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    games = [
        {"title": "EFL 1 to 24s", "file": "efl_1_to_24s.py"},
        {"title": "Last Man Standing", "file": "last_man_standing.py"},
        {"title": "Season Prediction", "file": "season_prediction.py"},
        {"title": "Snakes and Ladders", "file": "snakes_and_ladders.py"},
    ]

    tiles = []
    for game in games:
        tiles.append(
            ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(game["title"], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text("COMING SOON", italic=True, color=ft.Colors.GREY),
                            ft.ElevatedButton("View", disabled=True),  # Future navigation
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
