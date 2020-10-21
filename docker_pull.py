#！/usr/env python3
import os
from os import name
import sys
import string
import subprocess
from typing import List, Tuple

from tqdm import tqdm

# MIRROR_REGISTER = "hub-mirror.c.163.com"
MIRROR_MAP={
    "gcr.io":"gcr.mirrors.ustc.edu.cn",
    # "k8s.gcr.io":"gcr.mirrors.ustc.edu.cn/google-containers",
    "k8s.gcr.io":"registry.cn-hangzhou.aliyuncs.com/google_containers",
    "quay.io":"quay.mirrors.ustc.edu.cn",
}
HUB_NAME = "mirrorgooglecontainers"
DOCKER_PULL = "docker pull %s"
DOCKER_TAG = "docker tag %s %s"
DOCKER_SAVE = "docker save %s %s"
DOCKER_LOAD = "docker load %s"
DOCKER_IMAGES = "docker images |grep %s"
DOCKER_CLAER = "docker rmi %s"


def exec_shell(cmd: List[str]) -> str:
    command = " ".join(cmd)
    print("\n ", command)
    p = subprocess.Popen(command, shell=True)
    p.wait()
    if p.stdout is not None:
        print("out:", p.stdout.read().decode())
    if p.stderr is not None:
        print("err:", p.stderr.read().decode())
    return ""


def check_image_name(image_name: str) -> Tuple[str, str]:
    """检查镜像名
    """
    fs = image_name.split(":")
    if len(fs) != 2:
        raise Exception("镜像名要制定具体版本")
    srv, tar = map_image(fs[0])
    lay = "%s:%s"
    return lay % (srv, fs[1]), lay % (tar, fs[1])


def map_image(image_name: str) -> Tuple[str, str]:
    """分配路径，和新tag名
    """
    names = image_name.split("/")
    if len(names) < 2:
        raise Exception("gcr.io/pause:3.1这种完整格式才行")
    # lay = "%s/%s/%s"
    # return image_name, lay % (MIRROR_REGISTER, HUB_NAME, names[-1])
    for k,v in MIRROR_MAP.items():
        if names[0].startswith(k):
            names[0]=names[0].replace(k,v)

    return image_name,"/".join(names)

def pull_image(image_path: str):
    """拉取image"""
    cmd = [DOCKER_PULL % image_path]
    exec_shell(cmd)


def tag_image(image_path: str, new_image: str):
    """重新大tag"""
    cmd = [DOCKER_TAG % (image_path, new_image)]
    exec_shell(cmd)


def clear_image(image_path: str):
    cmd = [DOCKER_CLAER % image_path]
    exec_shell(cmd)


def print_image(image_path: str):
    cmd = [DOCKER_IMAGES % image_path]
    exec_shell(cmd)


if __name__ == "__main__":
    try:
        # 镜像名
        images = sys.argv
        if len(images) >= 2:
            for i, image_name in tqdm(enumerate(images[1:], start=1)):
                srv, tar = check_image_name(image_name)
                pull_image(tar)
                print_image(tar)
                tag_image(tar, srv)
                print_image(srv)
                clear_image(tar)

        else:
            print(" push.py gcr.io/pause:3.1 这种格式")
    except Exception as e:
        print(e)
