import flet as ft
from supabase_client import supabase
from datetime import datetime, timezone, timedelta
import time
import asyncio
from pathlib import Path
from constants import deadline
import json
from auth_helpers import apply_saved_token
from supabase_helpers import safe_execute

#user_id = "7b52ade0-b667-4b15-a15d-9665c851c9f2"

def get_teams(league: str, season: str = "2025/2026"):
    response = supabase.table("teams")\
        .select("*")\
        .eq("league", league)\
        .eq("season", season)\
        .order("sort_order")\
        .execute()
    return response.data

def efl_1_to_24s_view(page: ft.Page, user_id: str, on_logout):
    #print(f"🔐 Entered efl_1_to_24s_view for user: {user_id}")
    page.title = "EFL 1 to 24s"
    page.scroll = "auto"
    page.padding = 20

    team_list = []  # Stores team data in current order
    last_saved_ids = []  # store saved order of team UUIDs

    list_view = ft.ReorderableListView(
        on_reorder=lambda e: handle_reorder(e),
        expand=True,
    )

    countdown_text = ft.Text(
        value="⏳ Deadline in: ...",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.RED,
    )

    async def update_countdown():
        #print("⏳ Countdown started")

        while True:
            now = datetime.now(timezone.utc)
            if now >= deadline:
                countdown_text.value = "🚫 Deadline passed – predictions locked!"
                countdown_text.color = ft.Colors.GREY
                save_button.disabled = True        # ⛔ Disable the save button
                page.update()
                break

            remaining = deadline - now
            total_seconds = int(remaining.total_seconds())
            days, remainder = divmod(total_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            countdown_text.value = f"⏳ Time left: {days}d {hours:02}h {minutes:02}m {seconds:02}s"
            page.update()
            await asyncio.sleep(1)

    async def save_prediction(e):
        league = tabs.tabs[tabs.selected_index].text.lower().replace(" ", "_")
        season = "2025/2026"
        rankings = [team["id"] for team in team_list]
        now = datetime.now(timezone.utc)

        # 🔐 Ensure PostgREST has the correct token
        apply_saved_token()

        # ✅ Block saving if deadline passed
        if now > deadline:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Deadline passed – predictions locked!"))
            page.snack_bar.open = True
            page.update()
            return

        response = supabase.table("predictions").upsert({
            "user_id": user_id,
            "league": league,
            "season": season,
            "rankings": rankings,
            "updated_at": now.isoformat()
        }, on_conflict="user_id,league,season").execute()

        if response.data:
            page.snack_bar = ft.SnackBar(ft.Text("✅ Prediction saved!"))
            last_saved_ids.clear()
            last_saved_ids.extend(rankings)
            save_button.disabled = True
            save_status_icon.visible = True
            page.update()

            await asyncio.sleep(2)
            save_status_icon.visible = False
            page.update()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("❌ Failed to save prediction."))
            page.snack_bar.open = True
            page.update()


    save_button = ft.ElevatedButton(
        text="Save Prediction",
        on_click=save_prediction,
        icon=ft.Icons.SAVE,
        disabled=True
    )

    logout_btn = ft.TextButton("Logout", on_click=lambda e: logout(e), icon=ft.Icons.LOGOUT)

    save_status_icon = ft.Icon(
        name=ft.Icons.CHECK_CIRCLE,
        color=ft.Colors.GREEN,
        visible=False
    )
    
    def handle_reorder(e):
        item = team_list.pop(e.old_index)
        team_list.insert(e.new_index, item)

        list_view.controls.clear()
        for i, team in enumerate(team_list):
            list_view.controls.append(team_container(team, i + 1))

        current_ids = [team["id"] for team in team_list]
        save_button.disabled = (current_ids == last_saved_ids)

        # Hide saved icon on any change
        save_status_icon.visible = False

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

        # 🔐 Ensure PostgREST has the correct token
        apply_saved_token()

        season = "2025/2026"
        league = league.lower().replace(" ", "_")

        #print(f"Loading teams for: {league}")
        # Try to fetch saved prediction

        print("📥 Fetching predictions for:", user_id, league, season)
        print("🔍 SELECT user_id:", user_id)
        print("🔍 Current PostgREST token:", supabase.postgrest.headers.get("Authorization"))


        prediction_res = supabase.table("predictions")\
            .select("rankings")\
            .eq("user_id", user_id)\
            .eq("league", league)\
            .eq("season", season)\
            .execute()
        
        print("🟩 Prediction result:", prediction_res.data)

        print("🔐 PostgREST token:", supabase.postgrest.headers.get("Authorization"))

        records = prediction_res.data
        if records and records[0]["rankings"]:
            #print("✅ Loading saved prediction order")
            saved_order_ids = records[0]["rankings"]

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
            #print("📄 No saved prediction, loading default order")
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
        
        #print("📦 List view built with", len(list_view.controls), "teams")
        page.update()

        # Save the current state of team IDs as the last saved
        last_saved_ids.clear()
        last_saved_ids.extend([team["id"] for team in team_list])


    def on_tab_change(e):
        selected_league = e.control.tabs[e.control.selected_index].text
        load_teams(selected_league)

    def logout(e):
        supabase.auth.sign_out()
        Path(".session.json").unlink(missing_ok=True)
        on_logout()


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
        ft.Column(
            controls=[
                countdown_text,
                ft.Row([
                    ft.Text("EFL 1 to 24s", size=24, weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),  # Spacer
                    logout_btn,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Middle: Tabs + Team List
                tabs,
                ft.Container(content=list_view, padding=10, expand=True),

                # Bottom: Save + Icon
                ft.Row([save_button, save_status_icon], spacing=10),
            ],
            spacing=20,
            expand=True,
        )
    )

    def start_view():
        #print("🚀 Init started")
        load_teams("championship")
        page.run_task(update_countdown)

    return start_view


