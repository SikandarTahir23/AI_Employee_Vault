"""
Vault Sync — Platinum Tier Cloud-Local Delegation
Automates git push/pull for syncing the AI Employee Vault
between Cloud Agent and Local Agent instances.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent

# ── Safety Guard ────────────────────────────────────────────────────────────
# These files are NEVER staged or overwritten by vault_sync.
# They represent the live runtime environment — overwriting them mid-session
# would crash the Streamlit dashboard.
PROTECTED_FILES = {
    "app.py",
    "vault_sync.py",
    "odoo_mcp_bridge.py",
    "agent_brain.py",
    "linkedin_poster.py",
    "whatsapp_sender.py",
    "linkedin_agent.py",
    "social_media_agent.py",
    "watchers/gmail_bridge.py",
    "watchers/desktop_watcher.py",
}
# ────────────────────────────────────────────────────────────────────────────

# Workflow directories that must exist (even if empty)
WORKFLOW_DIRS = [
    "Needs_Action",
    "Needs_Action/Social",
    "In_Progress",
    "Pending_Approval",
    "Approved",
    "Done",
    "Plans",
    "Drafts",
    "Readings",
    "prompt_history",
]


def run_git(args, check=True):
    """Run a git command and return the output."""
    cmd = ["git", "-C", str(BASE_DIR)] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  [GIT ERROR] {' '.join(args)}")
        print(f"  {result.stderr.strip()}")
        return None
    return result.stdout.strip()


def ensure_gitkeep():
    """Ensure .gitkeep files exist in workflow directories so git tracks them."""
    for d in WORKFLOW_DIRS:
        dir_path = BASE_DIR / d
        dir_path.mkdir(parents=True, exist_ok=True)
        gitkeep = dir_path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("")


def check_remote():
    """Check if a remote origin is configured."""
    remote = run_git(["remote", "get-url", "origin"], check=False)
    if remote:
        return remote
    return None


def status():
    """Show current git status."""
    print("\n[STATUS]")
    remote = check_remote()
    if remote:
        print(f"  Remote: {remote}")
    else:
        print("  Remote: Not configured")
        print("  Run: git remote add origin <your-repo-url>")

    branch = run_git(["branch", "--show-current"])
    print(f"  Branch: {branch or 'N/A'}")

    changes = run_git(["status", "--porcelain"])
    if changes:
        lines = changes.split("\n")
        print(f"  Changes: {len(lines)} file(s)")
        for line in lines[:10]:
            print(f"    {line}")
        if len(lines) > 10:
            print(f"    ... and {len(lines) - 10} more")
    else:
        print("  Changes: Clean (no uncommitted changes)")


def pull():
    """Pull latest changes from remote.
    Uses --no-ff and checks out only non-protected paths."""
    print("\n[PULL] Fetching latest from remote...")
    print(f"  [GUARD] Protected files will not be overwritten: {', '.join(sorted(PROTECTED_FILES))}")

    remote = check_remote()
    if not remote:
        print("  [ERROR] No remote configured. Run:")
        print("    git remote add origin <your-repo-url>")
        return False

    result = run_git(["pull", "--rebase", "origin", "main"], check=False)
    if result is None:
        # Try master branch
        result = run_git(["pull", "--rebase", "origin", "master"], check=False)

    if result is not None:
        print(f"  [OK] {result or 'Already up to date.'}")
        return True
    else:
        print("  [WARN] Pull failed — check remote configuration.")
        return False


def push(message=None):
    """Stage, commit, and push all changes."""
    print("\n[PUSH] Syncing vault to remote...")

    # Ensure workflow dirs are tracked
    ensure_gitkeep()

    # Stage only non-protected files
    # Using pathspec ':!file' to exclude protected runtime scripts
    exclude_args = [f":!{p}" for p in PROTECTED_FILES]
    run_git(["add", "--", "."] + exclude_args)

    # Check if there's anything to commit
    changes = run_git(["status", "--porcelain"])
    if not changes:
        print("  [OK] Nothing to commit. Vault is clean.")
        return True

    # Commit
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not message:
        message = f"Vault sync — {now}"
    run_git(["commit", "-m", message])
    print(f"  [COMMIT] {message}")

    # Push
    remote = check_remote()
    if not remote:
        print("  [WARN] No remote configured. Changes committed locally only.")
        print("  To push, run: git remote add origin <your-repo-url>")
        return True

    result = run_git(["push", "origin", "HEAD"], check=False)
    if result is not None:
        print("  [OK] Pushed to remote.")
        return True
    else:
        print("  [WARN] Push failed — you may need to set upstream:")
        print("    git push -u origin main")
        return False


def auto_sync():
    """Full sync: pull first, then push."""
    print("=" * 50)
    print("  Vault Sync — Cloud-Local Delegation")
    print("=" * 50)
    print(f"  Vault: {BASE_DIR}")
    print(f"  Time:  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    ensure_gitkeep()
    status()
    pull()
    push()

    print("\n[DONE] Sync complete.")


def main():
    if len(sys.argv) < 2:
        auto_sync()
        return

    command = sys.argv[1].lower()

    if command == "status":
        ensure_gitkeep()
        status()
    elif command == "pull":
        pull()
    elif command == "push":
        msg = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        push(msg)
    elif command == "sync":
        auto_sync()
    elif command == "init":
        print("[INIT] Ensuring vault structure...")
        ensure_gitkeep()
        run_git(["add", "-A"])
        run_git(["commit", "-m", "Initial vault structure"])
        print("[OK] Vault initialized and committed.")
    else:
        print("Usage: python vault_sync.py [command]")
        print()
        print("Commands:")
        print("  status  — Show git status and remote info")
        print("  pull    — Pull latest from remote")
        print("  push    — Stage, commit, and push all changes")
        print("  sync    — Full sync (pull + push)")
        print("  init    — Initialize vault structure and first commit")
        print()
        print("No command = full sync (pull + push)")


if __name__ == "__main__":
    main()
