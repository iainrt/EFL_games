import flet as ft
from supabase_client import supabase
from datetime import datetime, timezone

user_id = "7b52ade0-b667-4b15-a15d-9665c851c9f2"

def get_teams(league: str, season: str = "2025/2026"):
    response = supabase.table("teams")\
        .select("*")\
        .eq("league", league)\
        .eq("season", season)\
        .order("sort_order")\
        .execute()
    return response.data

def efl_1_to_24s_view(page: ft.Page):
    page.title = "EFL 1 to 24s"
    page.scroll = "auto"
    page.padding = 20

    team_list = []  # Stores team data in current order

    list_view = ft.ReorderableListView(
        on_reorder=lambda e: handle_reorder(e),
        expand=True,
    )

    save_button = ft.ElevatedButton(
        text="Save Prediction",
        on_click=lambda e: save_prediction(),
        icon=ft.Icons.SAVE
    )    
    
    def handle_reorder(e):
        item = team_list.pop(e.old_index)
        team_list.insert(e.new_index, item)

        # Rebuild the list view
        list_view.controls.clear()
        for index, team in enumerate(team_list):
            list_view.controls.append(team_container(team, index + 1))
        page.update()

    def save_prediction():
        league = tabs.tabs[tabs.selected_index].text.lower().replace(" ", "_")
        season = "2025/2026"
        rankings = [team["id"] for team in team_list]
        now = datetime.now(timezone.utc).isoformat()

        response = supabase.table("predictions").upsert({
            "user_id": user_id,
            "league": league,
            "season": season,
            "rankings": rankings,
            "updated_at": now
        }, on_conflict="user_id, league, season").execute()

        if response.data:
            page.snack_bar = ft.SnackBar(ft.Text("✅ Prediction saved!"))
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Failed to save prediction."))
        page.snack_bar.open = True
        page.update()

    def team_container(team, position):
        return ft.Container(
            key=str(team["id"]),
            content=ft.Row(
                controls=[
                    ft.Text(f"{position}.", width=30),
                    ft.Text(team["name"]),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=10,
            margin=ft.margin.only(bottom=6),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=6,
            alignment=ft.alignment.center_left,
            expand=False,       # 👈 prevent full-width stretch
            width=350           # 👈 optional: limit width to pull handle in
        )

    def load_teams(league):
        nonlocal team_list
        season = "2025/2026"

        # Try to fetch saved prediction
        prediction_res = supabase.table("predictions")\
            .select("rankings")\
            .eq("user_id", user_id)\
            .eq("league", league)\
            .eq("season", season)\
            .maybe_single()\
            .execute()

        if prediction_res.data and prediction_res.data["rankings"]:
            saved_order_ids = prediction_res.data["rankings"]

            # Fetch full team info for those IDs (keep order)
            team_list = []
            for team_id in saved_order_ids:
                res = supabase.table("teams")\
                    .select("*")\
                    .eq("id", team_id)\
                    .maybe_single()\
                    .execute()
                if res.data:
                    team_list.append(res.data)
        else:
            # No saved prediction — load default team order
            team_list = supabase.table("teams")\
                .select("*")\
                .eq("league", league)\
                .eq("season", season)\
                .order("sort_order")\
                .execute().data

        # Rebuild list view
        list_view.controls.clear()
        for i, team in enumerate(team_list):
            list_view.controls.append(team_container(team, i + 1))
        page.update()


    def on_tab_change(e):
        selected_league = e.control.tabs[e.control.selected_index].text.lower().replace(" ", "_")
        load_teams(selected_league)

    tabs = ft.Tabs(
        selected_index=0,
        on_change=on_tab_change,
        tabs=[
            ft.Tab(text="Championship"),
            ft.Tab(text="League One"),
            ft.Tab(text="League Two")
        ]
    )

    page.add(
        ft.Column([
            ft.Text("Predict the finishing order", size=24, weight=ft.FontWeight.BOLD),
            tabs,
            ft.Container(content=list_view, padding=10, expand=True),
            save_button
        ])
    )

    # Initial load
    load_teams("championship")

ft.app(target=efl_1_to_24s_view)
