"""通过 GitHub Git Data API 推送本地提交（用于 github.com 直连被屏蔽的场景）。"""
import base64
import json
import subprocess
import sys
import urllib.request
import urllib.error

REPO = "Sisphus1234/daily-biomedical-review-digest"
BRANCH = "master"


def gh_api(method, path, data=None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method)
    req.add_header("Authorization", f"token {TOKEN}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "push-via-api")
    if data is not None:
        req.add_header("Content-Type", "application/json")
        body = json.dumps(data).encode("utf-8")
    else:
        body = None
    try:
        with urllib.request.urlopen(req, data=body, timeout=60) as resp:
            text = resp.read().decode("utf-8")
            return json.loads(text) if text else None
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8")
        print(f"API error {e.code}: {err}", file=sys.stderr)
        raise


def git_bytes(*args):
    return subprocess.run(["git", *args], capture_output=True).stdout


def git_str(*args):
    out = subprocess.run(["git", *args], capture_output=True, encoding="utf-8", errors="replace").stdout
    return out.strip()


def list_tree(commit):
    """用 -z 字节级解析 ls-tree，避免带引号/非 ASCII 路径被二次转义损坏。"""
    raw = git_bytes("ls-tree", "-r", "-z", commit)
    entries = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, path = item.split(b"\t", 1)
        mode, otype, sha = meta.split()
        entries.append((mode.decode(), otype.decode(), sha.decode(),
                        path.decode("utf-8", errors="replace")))
    return entries


def main():
    global TOKEN
    TOKEN = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True).stdout.strip()

    remote_sha = git_str("rev-parse", f"origin/{BRANCH}")
    local_sha = git_str("rev-parse", "HEAD")
    if remote_sha == local_sha:
        print("已是最新，无需推送")
        return

    commits = git_str("log", "--format=%H", f"{remote_sha}..HEAD").splitlines()
    commits.reverse()
    print(f"将推送 {len(commits)} 个提交: {remote_sha[:8]} -> {local_sha[:8]}")

    current = remote_sha
    for c in commits:
        msg = git_str("log", "-1", "--format=%B", c).strip()
        parents = [p for p in git_str("log", "-1", "--format=%P", c).split() if p != current]
        tree_sha = git_str("rev-parse", f"{c}^{{tree}}")
        files = list_tree(c)

        # 创建所有 blob
        blob_map = {}
        for mode, otype, sha, path in files:
            if otype != "blob":
                continue
            content = git_bytes("show", f"{c}:{path}")
            data = base64.b64encode(content).decode("ascii")
            resp = gh_api("POST", "/repos/" + REPO + "/git/blobs", {"content": data, "encoding": "base64"})
            blob_map[sha] = resp["sha"]

        # 重建 tree（逐层递归）
        def make_tree(prefix=""):
            entries = []
            seen_dirs = set()
            for mode, otype, sha, path in files:
                if not path.startswith(prefix):
                    continue
                rel = path[len(prefix):]
                if "/" in rel:
                    sub = rel.split("/", 1)[0]
                    if sub not in seen_dirs:
                        seen_dirs.add(sub)
                        entries.append({"path": sub, "mode": "040000", "type": "tree", "sha": make_tree(prefix + sub + "/")})
                else:
                    entries.append({"path": rel, "mode": mode, "type": "tree" if otype == "tree" else "blob", "sha": blob_map.get(sha, sha)})
            resp = gh_api("POST", "/repos/" + REPO + "/git/trees", {"tree": entries})
            return resp["sha"]

        new_tree = make_tree()
        resp = gh_api("POST", "/repos/" + REPO + "/git/commits", {
            "message": msg, "tree": new_tree, "parents": [current] if current else [],
        })
        current = resp["sha"]
        print(f"  提交 {c[:8]} -> {current[:8]}")

    gh_api("PATCH", f"/repos/{REPO}/git/refs/heads/{BRANCH}", {"sha": current, "force": True})
    print(f"refs/heads/{BRANCH} 已更新为 {current[:8]}")


if __name__ == "__main__":
    main()