#!/usr/bin/env python3

import os
import sys
import json
import subprocess

BASE_DIR = "/var/lib/mini-container"

def log_info(msg):
    print(f"[LOG-INFO] {msg}")

def log_success(msg):
    print(f"[LOG-SUCCESS] {msg}")

def log_failure(msg):
    print(f"[LOG-FAILURE] {msg}")

def load_config():
    log_info("Загрузка конфигурации config.json")
    with open("config.json") as f:
        return json.load(f)

def create_container_dirs(container_id):
    container_path = os.path.join(BASE_DIR, container_id)
    os.makedirs(container_path, exist_ok=True)
    log_success(f"Создана директория: {container_path}")

    upper = os.path.join(container_path, "upper")
    work = os.path.join(container_path, "work")
    merged = os.path.join(container_path, "merged")

    os.makedirs(upper, exist_ok=True)
    os.makedirs(work, exist_ok=True)
    os.makedirs(merged, exist_ok=True)

    log_success("Созданы директории overlayfs")

    return container_path

def setup_overlay(container_path, lowerdir):
    upperdir = os.path.join(container_path, "upper")
    workdir = os.path.join(container_path, "work")
    merged = os.path.join(container_path, "merged")

    lowerdir = os.path.abspath(lowerdir)

    log_info(f"Монтирование overlayfs")
    log_info(f"lower={lowerdir}")
    log_info(f"upper={upperdir}")
    log_info(f"work={workdir}")

    mount_cmd = [
        "mount",
        "-t", "overlay",
        "overlay",
        "-o", f"lowerdir={lowerdir},upperdir={upperdir},workdir={workdir}",
        merged
    ]

    subprocess.run(mount_cmd, check=True)

    log_success(f"Overlayfs смонтирован: {merged}")

    return merged

def mount_filesystems(config):
    log_info("Монтирование файловых систем")

    mounts = config.get("mounts", [])

    for mount in mounts:
        destination = mount["destination"]
        fs_type = mount["type"]
        source = mount["source"]

        os.makedirs(destination, exist_ok=True)

        log_info(f"mount {fs_type} -> {destination}")

        subprocess.run([
            "mount",
            "-t",
            fs_type,
            source,
            destination
        ], check=True)

    log_success("Файловые системы смонтированы")

def setup_hostname(config):
    hostname = config.get("hostname", "mini-container")

    log_info(f"Установка hostname: {hostname}")

    subprocess.run(["hostname", hostname], check=True)

def build_env(config):
    env = dict(os.environ)

    for e in config["process"].get("env", []):
        key, val = e.split("=", 1)
        env[key] = val

    return env

def build_unshare_command(config):
    namespaces = config["linux"]["namespaces"]

    cmd = ["unshare", "--fork"]

    for ns in namespaces:
        ns_type = ns["type"]

        if ns_type == "pid":
            cmd.append("--pid")
        elif ns_type == "mount":
            cmd.append("--mount")
        elif ns_type == "uts":
            cmd.append("--uts")
        elif ns_type == "ipc":
            cmd.append("--ipc")
        elif ns_type == "net":
            cmd.append("--net")

    return cmd

def run_container(rootfs, config):

    setup_hostname(config)

    log_info(f"Chroot в {rootfs}")

    os.chroot(rootfs)
    os.chdir("/")

    mount_filesystems(config)

    cmd = config["process"]["args"]

    env = build_env(config)

    log_info(f"Запуск процесса: {' '.join(cmd)}")
    log_info("Для выхода используйте exit")

    os.execvpe(cmd[0], cmd, env)

def main():

    if len(sys.argv) < 3:
        print("[LOG-FAILURE] Usage: run-mini-container.py run <id>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":

        container_id = sys.argv[2]

        log_info(f"Запуск контейнера: {container_id}")

        config = load_config()

        container_path = create_container_dirs(container_id)

        rootfs_path = config["root"]["path"]

        rootfs = setup_overlay(container_path, rootfs_path)

        unshare_cmd = build_unshare_command(config)

        log_info("Создание namespaces")

        subprocess.run(
            unshare_cmd + [
                "python3",
                __file__,
                "child",
                rootfs
            ],
            check=True
        )

    elif command == "child":

        rootfs = sys.argv[2]

        config = load_config()

        run_container(rootfs, config)

        log_success("Контейнер завершился")

if __name__ == "__main__":
    main()
