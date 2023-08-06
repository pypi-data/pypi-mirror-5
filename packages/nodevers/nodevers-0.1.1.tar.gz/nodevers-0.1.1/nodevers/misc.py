"""
This modules includes all the functions that are used very frequently.
"""

import os
import shutil
import re
import subprocess

def get_nodevers_prefix():
    """
    Return the path where Nodes will be installed
    and configuration will be created.
    """
    nodevers_prefix = os.getenv("NODEVERS_PREFIX")
    if nodevers_prefix is not None:
        return nodevers_prefix
    elif os.geteuid() == 0:
        return "/opt/nodevers"
    else:
        home_path = os.getenv("HOME")
        return os.path.join(home_path, ".nodevers")

def valid_nodevers_prefix(path):
    """
    Check if path exists and if it has the required subdirs:
        versions/
        tmp/
        patches/
        patches/global
    """
    dirs = ["versions", "tmp", "patches", os.path.join("patches", "global")]
    for i in dirs:
        full_path = os.path.join(path, i)
        if not os.path.isdir(full_path):
            return False
    return True

def mknodevers_prefix(path):
    """
    Removes the path if it exists and then creates the directories
    needed by nodevers.
    """
    if os.path.exists(path):
        shutil.rmtree(path)
    dirs = ["versions", "tmp", "patches", os.path.join("patches", "global")]
    for i in dirs:
        full_path = os.path.join(path, i)
        os.makedirs(full_path)

def valid_version_string(ver):
    """
    Use regex to see if version
    looks valid.
    """
    regex = "^(\d+)\.(\d+)\.(\d+)$"
    match = re.match(regex, ver)
    if match is None:
        return False
    else:
        return True

def get_versions_dir():
    """
    Return the path where Nodes will be installed.
    """
    return os.path.join(get_nodevers_prefix(), "versions")

def get_bin_dir():
    """
    Return the path where the symlink to current Node's bin
    will be created.
    """
    return os.path.join(get_nodevers_prefix(), "bin")

def get_patches_dir():
    """
    Return the path where the user should put his patches in.
    """
    return os.path.join(get_nodevers_prefix(), "patches")

def get_tmp_dir():
    """
    Return the path where nodevers will download source packages
    and build Node.
    """
    return os.path.join(get_nodevers_prefix(), "tmp")

def get_version_dir(ver):
    """
    Return the path where version should be installed.
    """
    return os.path.join(get_versions_dir(), ver)

def get_real_version_dir(ver):
    """
    Same as get_version_dir() except return None if the path doesn't exist.
    """
    if version_exists(ver):
        return get_version_dir(ver)
    else:
        return None

def version_exists(ver):
    """
    Checks if version is installed.
    """
    version_dir = get_version_dir(ver)
    if os.path.isdir(version_dir):
        return True
    else:
        return False

def get_patches_list(ver):
    """
    Return a list of patches that should be applied to the Node source code.
    """
    patches_list = []
    global_patch_dir = os.path.join(get_patches_dir(), "global")
    version_patch_dir = os.path.join(get_patches_dir(), ver)
    for patch in os.listdir(global_patch_dir):
        full_path = os.path.join(global_patch_dir, patch)
        if not os.path.isdir(full_path):
            patches_list.append(full_path)
    if os.path.isdir(version_patch_dir):
        for patch in os.listdir(version_patch_dir):
            full_path = os.path.join(version_patch_dir, patch)
            if not os.path.isdir(full_path):
                patches_list.append(full_path)
    return patches_list

def __try_python(python_exe):
    """
    Check if python is OK for building Node
    If it is, return True.
    If it is not, return False.
    """
    # Node supports building only with Python 2.6 or 2.7
    regex = "Python (2\.[67]\.\d+)"
    try:
        process = subprocess.Popen([python_exe, "-V"], stderr=subprocess.PIPE)
        ver = process.stderr.read()
        if re.match(regex, ver) is None:
            return False
        else:
            return True
    except OSError:
        return False

def __try_make(make_exe):
    """
    Check if make is GNU make.
    If it is, return True.
    Otherwise return False.
    """
    regex = "GNU [Mm]ake"
    try:
        process = subprocess.Popen([make_exe, "-v"], stdout=subprocess.PIPE)
        ver = process.stdout.read()
        if re.match(regex, ver) is None:
            return False
        else:
            return True
    except OSError:
        return False

def python():
    """
    Return the python executable that will be used to execute configure.
    """
    if __try_python("python"):
        return "python"
    elif __try_python("python2"):
        return "python2"
    else:
        raise install_helper.MissingToolError("python is either missing, newer than 2.x or older than 2.6")

def gmake():
    """
    Return the make executable that will be used to build Node.
    """
    if __try_make("make"):
        return "make"
    elif __try_make("gmake"):
        return "gmake"
    else:
        raise install_helper.MissingToolError("make is either missing or not GNU make")
