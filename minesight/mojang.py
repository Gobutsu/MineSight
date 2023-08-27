import httpx

def uuid_from_username(username):
    r = httpx.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
    if r.status_code == 200:
        return r.json()['id']
    else:
        return None
    
def username_from_uuid(uuid):
    r = httpx.get(f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}")
    if r.status_code == 200:
        return r.json()['name']
    else:
        return None
    
def dash_uuid(uuid):
    return uuid[0:8] + "-" + uuid[8:12] + "-" + uuid[12:16] + "-" + uuid[16:20] + "-" + uuid[20:32]