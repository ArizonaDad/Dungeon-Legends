"""
Dungeon Legends - One-command build & deploy.
Bumps version, packs sounds, compiles client, generates manifest, uploads to server.

Usage:
    python build_and_deploy.py                     # Bump patch (1.0.0 -> 1.0.1)
    python build_and_deploy.py --minor             # Bump minor (1.0.0 -> 1.1.0)
    python build_and_deploy.py --major             # Bump major (1.0.0 -> 2.0.0)
    python build_and_deploy.py --version 2.0.0     # Set exact version
    python build_and_deploy.py --skip-sounds       # Skip sound packing
    python build_and_deploy.py --skip-upload       # Build only, don't upload
    python build_and_deploy.py --notes "Fixed X"   # Release notes for TTS announcement
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import zipfile

# ---- Configuration ----
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_DIR = os.path.join(PROJECT_DIR, "Client")
CLIENT_OUT_DIR = os.path.join(CLIENT_DIR, "client")  # Compiled output folder
WEB_DIR_LOCAL = os.path.join(PROJECT_DIR, "web")
NVGT_PATH = r"C:\Users\16239\Documents\games\nvgt\nvgt.exe"

SERVER = "the-gdn.net"
SSH_PORT = 30001
USERNAME = "hearthstoner420"
KEY_PATH = os.path.expanduser("~/.ssh/id_ed25519")
REMOTE_WEB_DIR = "/home/hearthstoner420/dungeon_legends/web"
DOWNLOAD_URL = "http://the-gdn.net:8080/DungeonLegends.zip"

# Files tracked in the manifest (relative to client/ output directory)
TRACKED_FILES = [
    "client.exe",
    "sounds.dat",
    "lib/SAAPI64.dll",
    "lib/nvdaControllerClient64.dll",
    "lib/nvgt_curl.dll",
    "lib/phonon.dll",
]


def sha256_file(filepath):
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(1 << 20)  # 1 MB chunks
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def read_current_version():
    """Read CLIENT_VERSION from client.nvgt source."""
    client_nvgt = os.path.join(CLIENT_DIR, "client.nvgt")
    with open(client_nvgt, "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'const string CLIENT_VERSION\s*=\s*"(\d+\.\d+\.\d+)"', content)
    if not match:
        print("WARNING: CLIENT_VERSION not found in client.nvgt, assuming 0.0.0")
        return "0.0.0"
    return match.group(1)


def bump_version(current, bump_type):
    """Bump a semantic version string."""
    parts = [int(x) for x in current.split(".")]
    while len(parts) < 3:
        parts.append(0)
    major, minor, patch = parts[0], parts[1], parts[2]

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    else:  # patch
        return f"{major}.{minor}.{patch + 1}"


def update_version_in_source(new_version):
    """Update CLIENT_VERSION in client.nvgt source file."""
    client_nvgt = os.path.join(CLIENT_DIR, "client.nvgt")
    with open(client_nvgt, "r", encoding="utf-8") as f:
        content = f.read()
    content = re.sub(
        r'(const string CLIENT_VERSION\s*=\s*")(\d+\.\d+\.\d+)(")',
        rf"\g<1>{new_version}\g<3>",
        content,
    )
    with open(client_nvgt, "w", encoding="utf-8") as f:
        f.write(content)


def should_pack_sounds():
    """Check if sounds need repacking by comparing modification times."""
    sounds_dir = os.path.join(CLIENT_DIR, "sounds")
    sounds_dat = os.path.join(CLIENT_DIR, "sounds.dat")

    if not os.path.exists(sounds_dat):
        return True
    if not os.path.isdir(sounds_dir):
        return False

    dat_mtime = os.path.getmtime(sounds_dat)
    for entry in os.listdir(sounds_dir):
        fpath = os.path.join(sounds_dir, entry)
        if os.path.isfile(fpath) and os.path.getmtime(fpath) > dat_mtime:
            return True
    return False


def pack_sounds():
    """Run pack_sounds.nvgt to encrypt sound files into sounds.dat."""
    print("Packing sounds...")
    result = subprocess.run(
        [NVGT_PATH, "pack_sounds.nvgt"],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Sound packing failed:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())


def compile_client():
    """Compile the client with NVGT."""
    print("Compiling client...")
    result = subprocess.run(
        [NVGT_PATH, "-c", "client.nvgt"],
        cwd=CLIENT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Compilation failed:\n{result.stderr}")
        sys.exit(1)
    print("Compilation successful.")

    client_zip = os.path.join(CLIENT_DIR, "client.zip")
    if os.path.exists(client_zip):
        size_mb = os.path.getsize(client_zip) / (1024 * 1024)
        print(f"  client.zip: {size_mb:.0f} MB")

    # Extract client.zip to populate client/ output directory (overwrites in place)
    if os.path.exists(client_zip):
        print("Extracting client.zip...")
        os.makedirs(CLIENT_OUT_DIR, exist_ok=True)
        with zipfile.ZipFile(client_zip, "r") as zf:
            zf.extractall(CLIENT_OUT_DIR)


def generate_manifest(version, release_notes):
    """Generate manifest.json with file hashes and sizes."""
    print("Generating manifest...")
    files = []
    for relpath in TRACKED_FILES:
        filepath = os.path.join(CLIENT_OUT_DIR, relpath)
        if not os.path.exists(filepath):
            print(f"  WARNING: {relpath} not found, skipping")
            continue
        file_hash = sha256_file(filepath)
        file_size = os.path.getsize(filepath)
        files.append({"path": relpath, "hash": file_hash, "size": file_size})
        size_mb = file_size / (1024 * 1024)
        print(f"  {relpath}: {size_mb:.1f} MB  sha256={file_hash[:12]}...")

    manifest = {
        "version": version,
        "release_notes": release_notes,
        "download_url": DOWNLOAD_URL,
        "files": files,
    }

    # Save manifest locally
    manifest_path = os.path.join(CLIENT_OUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  manifest.json written to {manifest_path}")

    # Also inject manifest.json into client.zip so new players get it
    client_zip = os.path.join(CLIENT_DIR, "client.zip")
    if os.path.exists(client_zip):
        with zipfile.ZipFile(client_zip, "a") as zf:
            # Remove existing manifest if present
            existing = zf.namelist()
            if "client/manifest.json" not in existing:
                zf.write(manifest_path, "client/manifest.json")
                print("  manifest.json added to client.zip")

    return manifest


def load_deployed_manifest():
    """Load the previously deployed manifest for hash comparison."""
    cache_path = os.path.join(PROJECT_DIR, ".last_deployed_manifest.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return None
    return None


def save_deployed_manifest(manifest):
    """Cache the deployed manifest so future deploys can compare hashes."""
    cache_path = os.path.join(PROJECT_DIR, ".last_deployed_manifest.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def upload_to_server(manifest):
    """Upload files to the-gdn.net via SFTP. Uses hash comparison to skip unchanged files."""
    import paramiko

    key_pass = os.environ.get("DL_SSH_KEY_PASS", "snowball")
    key = paramiko.Ed25519Key.from_private_key_file(KEY_PATH, password=key_pass)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f"\nConnecting to {SERVER}:{SSH_PORT}...")
    ssh.connect(SERVER, port=SSH_PORT, username=USERNAME, pkey=key)
    sftp = ssh.open_sftp()

    # Ensure directory structure exists
    for d in [REMOTE_WEB_DIR, f"{REMOTE_WEB_DIR}/files", f"{REMOTE_WEB_DIR}/files/lib"]:
        try:
            sftp.mkdir(d)
        except IOError:
            pass  # Already exists

    # Build hash lookup from last deployed manifest for smart skipping
    prev_manifest = load_deployed_manifest()
    prev_hashes = {}
    if prev_manifest and "files" in prev_manifest:
        for entry in prev_manifest["files"]:
            prev_hashes[entry["path"]] = entry["hash"]

    # Upload individual files for incremental updates (hash-based skip)
    print("\nUploading individual files for incremental updates...")
    uploaded_count = 0
    skipped_count = 0
    for file_entry in manifest["files"]:
        relpath = file_entry["path"]
        local_path = os.path.join(CLIENT_OUT_DIR, relpath)
        new_hash = file_entry["hash"]

        # Skip if hash matches last deploy (no bytes changed)
        if relpath in prev_hashes and prev_hashes[relpath] == new_hash:
            size_mb = file_entry["size"] / (1024 * 1024)
            print(f"  {relpath}: hash unchanged, skipping ({size_mb:.0f} MB saved)")
            skipped_count += 1
            continue

        remote_path = f"{REMOTE_WEB_DIR}/files/{relpath}"
        size_mb = file_entry["size"] / (1024 * 1024)
        print(f"  {relpath}: uploading ({size_mb:.0f} MB)...")
        sftp.put(local_path, remote_path)
        print(f"  {relpath}: done")
        uploaded_count += 1

    print(f"  [{uploaded_count} uploaded, {skipped_count} skipped]")

    # Upload manifest.json (always, it's tiny)
    manifest_local = os.path.join(CLIENT_OUT_DIR, "manifest.json")
    manifest_remote = f"{REMOTE_WEB_DIR}/manifest.json"
    print("Uploading manifest.json...")
    sftp.put(manifest_local, manifest_remote)

    # Upload full zip for new player downloads only if any tracked file changed
    client_zip = os.path.join(CLIENT_DIR, "client.zip")
    remote_zip = f"{REMOTE_WEB_DIR}/DungeonLegends.zip"
    if uploaded_count > 0:
        size_mb = os.path.getsize(client_zip) / (1024 * 1024)
        print(f"Uploading DungeonLegends.zip ({size_mb:.0f} MB)...")
        sftp.put(client_zip, remote_zip)
        print("DungeonLegends.zip: done")
    else:
        print("DungeonLegends.zip: no file changes, skipping")

    # Upload index.html
    html_local = os.path.join(WEB_DIR_LOCAL, "index.html")
    if os.path.exists(html_local):
        sftp.put(html_local, f"{REMOTE_WEB_DIR}/index.html")
        print("index.html: uploaded")

    sftp.close()

    # Ensure HTTP server is running
    print("\nEnsuring download server is running...")
    ssh.exec_command("pkill -f 'python3 -m http.server 8080' 2>/dev/null")
    time.sleep(1)
    ssh.exec_command(
        f"cd {REMOTE_WEB_DIR} && nohup python3 -m http.server 8080 > /dev/null 2>&1 &"
    )

    ssh.close()

    # Cache this manifest for next deploy comparison
    save_deployed_manifest(manifest)


def main():
    parser = argparse.ArgumentParser(description="Dungeon Legends build & deploy")
    bump_group = parser.add_mutually_exclusive_group()
    bump_group.add_argument("--major", action="store_true", help="Bump major version")
    bump_group.add_argument("--minor", action="store_true", help="Bump minor version")
    bump_group.add_argument(
        "--patch", action="store_true", default=True, help="Bump patch version (default)"
    )
    bump_group.add_argument("--version", type=str, help="Set exact version (e.g. 2.0.0)")
    parser.add_argument("--skip-sounds", action="store_true", help="Skip sound packing")
    parser.add_argument("--skip-upload", action="store_true", help="Build only, no upload")
    parser.add_argument("--skip-compile", action="store_true", help="Skip compilation (manifest + upload only)")
    parser.add_argument(
        "--notes",
        type=str,
        default="",
        help="Release notes (announced via TTS to players)",
    )
    args = parser.parse_args()

    print("=" * 50)
    print("  Dungeon Legends - Build & Deploy")
    print("=" * 50)

    # Step 1: Version
    current = read_current_version()
    if args.version:
        new_version = args.version
    elif args.major:
        new_version = bump_version(current, "major")
    elif args.minor:
        new_version = bump_version(current, "minor")
    else:
        new_version = bump_version(current, "patch")

    print(f"\nVersion: {current} -> {new_version}")
    update_version_in_source(new_version)

    if not args.skip_compile:
        # Step 2: Pack sounds
        if args.skip_sounds:
            print("\nSkipping sound packing (--skip-sounds)")
        elif should_pack_sounds():
            print()
            pack_sounds()
        else:
            print("\nSounds unchanged, skipping pack")

        # Step 3: Compile
        print()
        compile_client()

    # Step 4: Generate manifest
    release_notes = args.notes or f"Updated to version {new_version}"
    print()
    manifest = generate_manifest(new_version, release_notes)

    # Step 5: Upload
    if args.skip_upload:
        print("\nSkipping upload (--skip-upload)")
    else:
        upload_to_server(manifest)

    # Summary
    print("\n" + "=" * 50)
    print(f"  Version:  {new_version}")
    print(f"  Notes:    {release_notes}")
    if not args.skip_upload:
        print(f"  Download: {DOWNLOAD_URL}")
        print(f"  Manifest: http://the-gdn.net:8080/manifest.json")
    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
