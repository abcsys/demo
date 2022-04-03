import yaml
import subprocess


def bash(cmd: str, quiet=False):
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        executable='/bin/bash',
    )
    out, e = proc.communicate()
    if not quiet:
        print(out.decode())
    if e is not None:
        print(e.decode())


def run(config: dict, name="*"):
    if name == "*":
        cases = config["spec"]
    else:
        cases = {name: config["spec"][name]}

    for name, spec in cases.items():
        create_digi(spec["digi"])
        create_mount(spec.get("mount", []))


def create_digi(config: dict):
    for kind, names in config.items():
        bash(f"digi run {kind} {' '.join(names)}")


def create_mount(config: list):
    pass


def run_query(query: str):
    pass


if __name__ == '__main__':
    with open("expt.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    run(config, "single-device")
