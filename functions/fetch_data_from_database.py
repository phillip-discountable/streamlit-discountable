
import pandas as pd

def fetch_data_from_database(url_path, supabase):

    response = supabase.table('Locality').select("locality_id", "name", "email_from_osm", "email_from_website", "phone_number", "wheelchair_accessible").eq("hash_code", url_path).execute()

    locality_df = pd.DataFrame(response.data)

    locality_id = locality_df["locality_id"].values[0]

    response = supabase.table('LocalityDiscount').select("locality_id", "discount_id", "name_of_option", "degree_of_disability", "mark_ag", "mark_b", "mark_bl", "mark_h", "mark_gl", "mark_g", "mark_tb", "standard_price", "discounted_price", "companion_price").eq("locality_id", locality_id).execute()

    discount_df = pd.DataFrame(response.data)

    return locality_df, discount_df