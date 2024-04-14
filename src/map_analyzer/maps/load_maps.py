import requests
from pathlib import Path
import os

from tqdm import tqdm
from gerrychain import Graph


state_ids = {
    "AL": "01",
    "AK": "02",
    "AZ": "04",
    "AR": "05",
    "CA": "06",
    "CO": "08",
    "CT": "09",
    "DE": "10",
    "FL": "12",
    "GA": "13",
    "HI": "15",
    "ID": "16",
    "IL": "17",
    "IN": "18",
    "IA": "19",
    "KS": "20",
    "KY": "21",
    "LA": "22",
    "ME": "23",
    "MD": "24",
    "MA": "25",
    "MI": "26",
    "MN": "27",
    "MS": "28",
    "MO": "29",
    "MT": "30",
    "NE": "31",
    "NV": "32",
    "NH": "33",
    "NJ": "34",
    "NM": "35",
    "NY": "36",
    "NC": "37",
    "ND": "38",
    "OH": "39",
    "OK": "40",
    "OR": "41",
    "PA": "42",
    "RI": "44",
    "SC": "45",
    "SD": "46",
    "TN": "47",
    "TX": "48",
    "UT": "49",
    "VT": "50",
    "VA": "51",
    "WA": "53",
    "WV": "54",
    "WI": "55",
    "WY": "56",
}

# NOTE: You must re-enable the big map formats for them to be downloaded and loaded together with the other maps
MAP_TYPES = [
    "BLOCK",
    "BG",
    "TRACT",
    "COUSUB",
    "COUNTY",
]

ALL_STATE_CODES = list(state_ids.keys())


def get_map_link(state_code: str, map_type: str):
    state_id = state_ids[state_code]
    map_link = (
        f"https://people.csail.mit.edu/ddeford/{map_type}/{map_type}_{state_id}.json"
    )
    return map_link


def download_file_with_progress(url: str, destination_path: Path):
    response = requests.get(url, stream=True)

    # Sizes in bytes.
    total_size = int(response.headers.get("content-length", 0))
    block_size = 1024

    temp_download_path = (
        destination_path.parent / f"{destination_path.stem}.json.download"
    )

    with tqdm(total=total_size, unit="B", unit_scale=True) as progress_bar:
        with open(temp_download_path, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)

    if total_size != 0 and progress_bar.n != total_size:
        raise RuntimeError("Could not download file")

    os.rename(temp_download_path, destination_path)


def download_map(state_code: str, map_type: str, cache_dir: Path) -> Path:
    cache_file_path = cache_dir / f"{map_type}_{state_code}.json"
    if cache_file_path.is_file():
        return cache_file_path
    map_link = get_map_link(state_code, map_type)
    print(f"Downloading {map_type} map for {state_code}")
    download_file_with_progress(map_link, cache_file_path)
    return cache_file_path


def load_map(state_code: str, map_type: str, cache_dir: Path) -> Graph:
    file_path = download_map(state_code, map_type, cache_dir)
    return Graph.from_json(str(file_path))


def load_all_maps(cache_dir: Path) -> dict[str, dict[str, Graph]]:
    result = dict()
    for map_type in MAP_TYPES:
        result[map_type] = dict()
        for state_code in ALL_STATE_CODES:
            result[map_type][state_code] = load_map(state_code, map_type, cache_dir)
    return result
