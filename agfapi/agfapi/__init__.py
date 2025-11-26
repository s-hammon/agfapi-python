import json
from subprocess import PIPE, Popen
import sys
from .bin import AGFAPI_BIN

class Session:
    """
    Session represents the HTTP session for the Agfa FHIR resource.
    """
    username: str
    password: str
    domain: str
    base_url: str
    token_url: str
    client_id: str
    redirect_list_id: str

    def __init__(
            self,
            username: str=None,
            password: str=None,
            domain: str=None,
            base_url: str=None,
            token_url: str=None,
            client_id: str=None,
            redirect_list_id: str=None,
    ):
        self.username: str = username
        self.password: str = password
        self.domain: str = domain
        self.base_url: str = base_url
        self.token_url: str = token_url
        self.client_id: str = client_id
        self.redirect_list_id: str = redirect_list_id

    def get_worklist(self, worklist_id):
        cmd = f"{AGFAPI_BIN} worklist get {worklist_id}"
        try:
            output = list(_exec_cmd(cmd))
            return "\n".join(output)
        except Exception as e:
            raise Exception(str(e))

def _exec_cmd(cmd: str):
    with Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True, encoding="utf-8", errors="replace") as proc:
        for line in proc.stdout:
            yield line.rstrip("\n")

        proc.wait()

        if proc.returncode != 0:
            err = proc.stderr.read()
            raise Exception(f"agfapi command failed:\n{err.strip()}")

def get_worklist(worklist_id: str):
    cmd = f"{AGFAPI_BIN} worklist get {worklist_id}"

    try:
        lines = list(_exec_cmd(cmd))
        output = "\n".join(lines).strip()

        return json.loads(output)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"agfapi returned non-JSON output for worklist '{worklist_id}':\n{output}") from e
    except Exception as e:
        raise e

def cli(*args, return_output=False):
    args = args or sys.argv[1:]
    escape = lambda a: a.replace('"', '\\"')
    cmd = f'''{AGFAPI_BIN} {" ".join([f'"{escape(a)}"' for a in args])}'''

    try:
        if return_output:
            output = list(_exec_cmd(cmd))
            return "\n".join(output)
        else:
            for line in _exec_cmd(cmd):
                print(line, flush=True)
            return 0

    except Exception as e:
        if return_output:
            raise e
        print(str(e), file=sys.stderr)
        return 11

def sanitize(line: str) -> str:
    return str(line.strip(), "utf-8", errors="replace")

