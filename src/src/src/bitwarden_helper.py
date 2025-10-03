import os, subprocess, json

class BitwardenHelper:
    def __init__(self):
        # if BW_SESSION is set, we'll use the bw CLI
        self.session = os.getenv("BW_SESSION")

    def _run_bw(self, args):
        cmd = ["bw"] + args
        env = None
        if self.session:
            env = dict(**os.environ)
            env["BW_SESSION"] = self.session
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            raise Exception(f"bw failed: {r.stderr}")
        return r.stdout

    def get_secret(self, name):
        # Try: environment variable first (convenient for Replit prototype)
        env_key = os.getenv(name)
        if env_key:
            return env_key

        # Next: try Bitwarden 'bw get' by item name
        if self.session:
            out = self._run_bw(["list","items"])
            items = json.loads(out)
            for it in items:
                if it.get("name") == name:
                    item_id = it["id"]
                    out2 = self._run_bw(["get","item", item_id])
                    item = json.loads(out2)
                    # attempt to read login.password
                    pw = item.get("login", {}).get("password")
                    if pw:
                        return pw
            raise Exception("Secret not found in Bitwarden: " + name)
        raise Exception("Secret not set and no BW_SESSION available: " + name)
