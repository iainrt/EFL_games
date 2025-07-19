import traceback
def safe_execute(query, description=""):
    try:
        result = query.execute()
        return result
    except Exception as ex:
        print(f"❌ Supabase execute failed during: {description}")
        traceback.print_exc()
        return None
