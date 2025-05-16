def get_signed_logo_url(locality_id, client, BUCKET_NAME):
    possible_exts = ["png", "jpg", "jpeg"]
    for ext in possible_exts:
        filename = f"{locality_id}.{ext}"
        try:
            res = client.storage.from_(BUCKET_NAME).create_signed_url(
                filename, expires_in=3600  # 1 Stunde gültig
            ).json()
            if "signedURL" in res:
                return res["signedURL"]
        except:
            pass
    return None