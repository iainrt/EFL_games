import flet as ft
from auth_helpers import try_auto_login, logout_user, get_current_user
from auth_view import auth_view
from efl_1_to_24s import efl_1_to_24s_view
from profile_view import profile_view


def main(page: ft.Page):
    page.title = "EFL Prediction Games"
    page.padding = 30
    page.scroll = "auto"
    page.theme_mode = ft.ThemeMode.LIGHT

    # Store user_id in session
    page.session.set("user_id", None)

    # --- AppBar Navigation ---
    def build_appbar():
        """Build dynamic navigation bar inside an AppBar with Material buttons."""
        user = get_current_user()

        actions = [ft.ElevatedButton("Home", on_click=lambda e: page.go("/"))]

        if user:
            display_name = user["user_metadata"].get("display_name") or user["email"]
            actions.append(
                ft.ElevatedButton(display_name, on_click=lambda e: page.go("/profile"))
            )
            actions.append(ft.ElevatedButton("1to24s", on_click=lambda e: page.go("/1to24s")))
            actions.append(ft.ElevatedButton("Logout", on_click=lambda e: handle_logout()))
        else:
            actions.append(ft.ElevatedButton("Login", on_click=lambda e: page.go("/login")))

        return ft.AppBar(
            title=ft.Text("EFL Prediction Games", size=20, weight=ft.FontWeight.BOLD),
            center_title=False,
            bgcolor=ft.Colors.BLUE_100,
            actions=actions,
        )

    def handle_logout():
        logout_user()
        page.session.set("user_id", None)
        page.go("/")

    # --- Routing ---
    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()

        if page.route == "/":
            # Home page
            games = [
                {"title": "EFL 1 to 24s", "route": "/login", "coming_soon": False},
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
                                    ft.Text(
                                        "COMING SOON" if game.get("coming_soon") else "",
                                        italic=True,
                                        color=ft.Colors.GREY,
                                    ),
                                    ft.ElevatedButton(
                                        "View",
                                        on_click=lambda _, r=game.get("route"): page.go(r) if r else None,
                                        disabled=game.get("coming_soon", True),
                                    ),
                                ],
                                spacing=10,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            padding=20,
                            width=250,
                        ),
                        elevation=4,
                    )
                )

            page.views.append(
                ft.View(
                    "/",
                    controls=[
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text("Choose a game mode below", size=18, weight=ft.FontWeight.BOLD),
                                            ft.ResponsiveRow(tiles, alignment=ft.MainAxisAlignment.CENTER),
                                        ],
                                        spacing=20,
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    padding=30,
                                    expand=True,
                                ),
                                elevation=8,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        )
                    ],
                    appbar=build_appbar(),
                )
            )

        elif page.route == "/login":
            # Login page
            def on_login_success(user_id):
                page.session.set("user_id", user_id)
                page.go("/1to24s")

            page.views.append(
                ft.View(
                    "/login",
                    controls=[
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=auth_view(page, on_login_success=on_login_success),
                                    padding=30,
                                ),
                                elevation=8,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        )
                    ],
                    appbar=build_appbar(),
                )
            )

        elif page.route == "/1to24s":
            # Protect route
            user_id = page.session.get("user_id")
            if not user_id:
                page.go("/login")
                return

            content_view = efl_1_to_24s_view(page, user_id=user_id, on_logout=handle_logout)

            page.views.append(
                ft.View(
                    "/1to24s",
                    controls=[
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(content=content_view, padding=30),
                                elevation=8,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        )
                    ],
                    appbar=build_appbar(),
                )
            )

        elif page.route == "/profile":
            page.views.append(
                ft.View(
                    "/profile",
                    controls=[
                        ft.Container(
                            content=ft.Card(
                                content=ft.Container(
                                    content=profile_view(page, refresh_nav=lambda: page.go(page.route)),
                                    padding=30,
                                ),
                                elevation=8,
                            ),
                            alignment=ft.alignment.center,
                            expand=True,
                        )
                    ],
                    appbar=build_appbar(),
                )
            )

        page.update()

    page.on_route_change = route_change

    # Auto-login redirect
    if try_auto_login(lambda user_id: page.session.set("user_id", user_id)):
        page.go("/1to24s")

    # Start at current route
    page.go(page.route)


ft.app(target=main, view=ft.WEB_BROWSER, route_url_strategy="hash")
