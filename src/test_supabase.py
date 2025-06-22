from supabase_client import supabase

def test_get_teams():
    response = supabase.table("teams")\
        .select("*")\
        .eq("league", "championship")\
        .eq("season", "2025/2026")\
        .order("sort_order")\
        .execute()

    # `response` is a Pydantic object with `.data` and `.model_dump()`
    teams = response.data

    if not teams:
        print("⚠️ No teams found or query failed.")
        return

    print(f"✅ Retrieved {len(teams)} teams:")
    for team in teams:
        print("-", team["name"])

if __name__ == "__main__":
    test_get_teams()

