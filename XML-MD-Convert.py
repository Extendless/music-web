import os
import plistlib
from pathlib import Path


def parse_apple_music_xml(xml_path):
  """Parses an Apple Music/iTunes XML library export file."""
  print(f"Parsing XML file: {xml_path}...")
  with open(xml_path, "rb") as f:
    data = plistlib.load(f)

  tracks = data.get("Tracks", {})
  library_data = {"artists": {}, "albums": {}, "genres": {}, "songs": {}}

  for track_id, track in tracks.items():
    name = track.get("Name")
    artist = track.get("Artist", "Unknown Artist")
    album = track.get("Album", "Unknown Album")
    genre = track.get("Genre", "Unknown Genre")
    url = track.get("URL", "")  # Apple Music web link or file path

    if not name:
      continue

    # Initialize collections
    if artist not in library_data["artists"]:
      library_data["artists"][artist] = set()
    if album not in library_data["albums"]:
      library_data["albums"][album] = {"artist": artist, "songs": set()}
    if genre not in library_data["genres"]:
      library_data["genres"][genre] = set()

    # Map relationships
    library_data["artists"][artist].add(album)
    library_data["artists"][artist].add(name)
    library_data["albums"][album]["songs"].add(name)
    library_data["genres"][genre].add(name)

    library_data["songs"][name] = {"artist": artist, "album": album, "url": url}

  return library_data


def sanitize_filename(name):
  """Removes characters unsafe for filenames while preserving readability."""
  return "".join(
      c for c in name if c.isalnum() or c in (" ", "-", "_", ".", "'")
  ).strip()


def generate_markdown_files(library_data, output_dir="apple_music_md"):
  """Generates Markdown files matching the requested hierarchical structure."""
  out_path = Path(output_dir)
  out_path.mkdir(parents=True, exist_ok=True)

  print(f"Generating Markdown files in '{output_dir}/'...")

  # 1. Generate Artists.md (File 1)
  artists_file = out_path / "Artists.md"
  all_artists_links = " ".join(
      [f"[[{artist}]]" for artist in sorted(library_data["artists"].keys())]
  )
  artists_file.write_text(f'"Artists" "{all_artists_links}"', encoding="utf-8")

  # 2. Generate individual Artist files (File 2)
  for artist, items in library_data["artists"].items():
    safe_name = sanitize_filename(artist)
    if not safe_name:
      continue
    artist_file = out_path / f"{safe_name}.md"
    items_links = " ".join([f"[[{item}]]" for item in sorted(items)])
    artist_file.write_text(f'"{artist}" "{items_links}"', encoding="utf-8")

  # 3. Generate Album files (File 3)
  for album, info in library_data["albums"].items():
    safe_name = sanitize_filename(album)
    if not safe_name:
      continue
    album_file = out_path / f"{safe_name}.md"
    songs_links = " ".join([f"[[{song}]]" for song in sorted(info["songs"])])
    album_file.write_text(f'"{album}" "{songs_links}"', encoding="utf-8")

  # 4. Generate Song files (File 4)
  for song, info in library_data["songs"].items():
    safe_name = sanitize_filename(song)
    if not safe_name:
      continue
    song_file = out_path / f"{safe_name}.md"

    # Use the extracted URL or fallback to placeholder
    url_value = info["url"] if info["url"] else "[Apple Music Link]"
    song_file.write_text(f'"{song}" "{url_value}"', encoding="utf-8")

  print("Conversion complete!")


if __name__ == "__main__":
  # Change this to the path of your exported Apple Music XML library file
  xml_file_path = "Library.xml"

  if os.path.exists(xml_file_path):
    lib_data = parse_apple_music_xml(xml_file_path)
    generate_markdown_files(lib_data)
  else:
    print(
        f"Error: Could not find '{xml_file_path}'. Please place your exported"
        " Apple Music XML file in the same directory or update"
        " 'xml_file_path'."
    )