# save_manager.py
import json
import os

SAVE_FILE = "savegame.json"


def save_game(game):
    province_owners = {}
    for prov in game.all_provinces:
        province_owners[prov.name] = [prov.color[0], prov.color[1], prov.color[2]]

    with open(f"provinces{game.year}.json", "r", encoding="utf-8") as f:
        prov_data = json.load(f)
        province_levels = {name: prov_data[name]["level"] for name in prov_data}

    with open(f"countries{game.year}.json", "r", encoding="utf-8") as f:
        country_data = json.load(f)
        country_resources = {}
        for name in country_data:
            country_resources[name] = {
                "wheat": country_data[name]["wheat"],
                "metal": country_data[name]["metal"],
                "wood": country_data[name]["wood"],
                "coal": country_data[name]["coal"],
                "oil": country_data[name]["oil"]
            }

    army_positions_str = {str(pos): moved for pos, moved in game.army_positions.items()}

    save_data = {
        "year": game.year,
        "country": game.country,
        "turn": game.turn,
        "army_positions": army_positions_str,
        "province_owners": province_owners,
        "province_levels": province_levels,
        "country_resources": country_resources
    }

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)

    print(f"[SAVE] Игра сохранена: ход {game.turn}, страна {game.country}")


def load_game():
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[LOAD ERROR] {e}")
        return None


def has_save():
    return os.path.exists(SAVE_FILE)


def apply_save_to_game(game, save_data):
    game.turn = save_data["turn"]

    game.army_positions = {}
    for pos_str, moved in save_data["army_positions"].items():
        clean = pos_str.strip("()[]").replace(" ", "")
        parts = clean.split(",")
        if len(parts) == 2:
            x = float(parts[0])
            y = float(parts[1])
            game.army_positions[(x, y)] = moved

    for prov in game.all_provinces:
        if prov.name in save_data["province_owners"]:
            r, g, b = save_data["province_owners"][prov.name]
            prov.color = (int(r), int(g), int(b))

    with open(f"provinces{game.year}.json", "r", encoding="utf-8") as f:
        prov_data = json.load(f)
    for name in prov_data:
        if name in save_data["province_levels"]:
            prov_data[name]["level"] = save_data["province_levels"][name]
    with open(f"provinces{game.year}.json", "w", encoding="utf-8") as f:
        json.dump(prov_data, f, ensure_ascii=False, indent=2)

    with open(f"countries{game.year}.json", "r", encoding="utf-8") as f:
        country_data = json.load(f)
    for name in country_data:
        if name in save_data["country_resources"]:
            res = save_data["country_resources"][name]
            country_data[name]["wheat"] = res["wheat"]
            country_data[name]["metal"] = res["metal"]
            country_data[name]["wood"] = res["wood"]
            country_data[name]["coal"] = res["coal"]
            country_data[name]["oil"] = res["oil"]
    with open(f"countries{game.year}.json", "w", encoding="utf-8") as f:
        json.dump(country_data, f, ensure_ascii=False, indent=2)
