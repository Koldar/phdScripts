#!/bin/python3
import abc
import argparse
import os
import sys
import subprocess
import re
from typing import Optional, Tuple, List

Path = str


class Dependency(abc.ABC):
    """
    Dependency of a package
    """

    def __init__(self, name: str, version: str, type: str):
        self.name = name
        self.version = version
        self.type = type

    @property
    def to_build_depends(self):
        return f"{self.name} ({self.type} {self.version})"


################## UTILS #####################


def run_command(cmd: str, cwd: str = os.curdir) -> int:
    """
    run a command without expecting nothing in return

    :param cmd: the command to execute
    :param cwd: directory where to execute the command
    :return exit code of the command, usuallly 0
    :raise OSError: if the exit cde fo the command is not 0
    """
    result = subprocess.run(cmd.split(), cwd=cwd)
    if result.returncode != 0:
        raise OSError(f"command {cmd} failed with exit code {result.returncode}")
    return result.returncode


def is_all_lowercase(s: str) -> bool:
    """
    Check if a string contains only lowercase characters

    :param s:
    :return:
    """
    for c in s:
        if c.isupper():
            return False
    return True

################### DEBCREATOR FUNCTIONS #############################


def get_tarball_debian_basename(package_name: str, version_number: str) -> str:
    """
    Generate an upstream tarball specific name

    :param package_name: name of the package
    :param version_number: version number
    :return:
    :see: https://wiki.debian.org/Packaging/Intro?action=show&redirect=IntroDebianPackaging
    """
    if not is_string_valid_source_package_name(package_name):
        raise ValueError(f"package name {package_name} is invalid. only lowercase letters, digits and dashes are valid.")

    return f"{package_name}_{version_number}.orig"


def is_string_valid_tarball_unpack_directory_name(dirname: str, package_name: str, version_number: str) -> bool:
    """
    Check if the folder obtained by unpacking the source tarball is compliant
    with debian packaging

    :param dirname: directory to check
    :param package_name: name of the source package name
    :param version_number: name of the version
    :return: True if the directory obtained by unpacking the tarball has a valid name, false otherwise
    """

    m = re.match(r"^(?P<name>[a-z0-9\-]+)-(?P<version>[a-z0-9\.\-]+)$", dirname)
    if m is None:
        return False
    if m.group("name") != package_name:
        return False
    if m.group("version") != version_number:
        return False
    return True

def get_tarball_valid_unpack_directory_name(package_name: str, version_number: str) -> str:
    """
    get the name of the folder that should be obtained by unpacking the tarball
    :param package_name: name of the package to check
    :param version_number: version number
    :return: the name of the folder that is obtained by unpacking the tarball
    """
    return f"{package_name}-{version_number}"

def is_string_valid_source_package_name(pkgname: str) -> bool:
    """
    Check if a package name is debian compliant

    The source package name should be all in lower case, and can contain letters, digits, and dashes.
    Some other characters are also allowed.

    :param pkgname: string to check
    :return:
    :see https://wiki.debian.org/Packaging/Intro?action=show&redirect=IntroDebianPackaging:
    """
    return re.match(r"^[a-z0-9\-]+$", pkgname) is not None


def create_tarball(package_name: str, version_number: str, folder_to_upload: str, folder_to_upload_vcs: Optional[str], output_directory: Path) -> Path:
    """
    Create on the file system a tarball of the folder to upload

    :param package_name: name of the package
    :param version_number: version of the package
    :param folder_to_upload: folder used to create the tarball
    :param folder_to_upload_vcs:  versioning system to exploit to build the tarball within folder_to_upload
    :param output_directory: output folder where the tarball will be located
    :return: path of the tarball
    """
    tar_basename = get_tarball_debian_basename(package_name, version_number)
    result = os.path.abspath(os.path.join(output_directory, tar_basename + ".tar.gz"))
    if folder_to_upload_vcs is None:
        run_command(f"tar -czvf {result} {folder_to_upload}")
    elif folder_to_upload_vcs == "git":
        run_command(f'git archive --format="tar" {folder_to_upload} | gzip > {result}')
    else:
        raise ValueError(f"invalid folder-to-upload-vcs {folder_to_upload_vcs}")

    return result


def ensure_tarball_unpack_into_valid_folder(tarball: Path, package_name: str, version_number: str, output_directory: Path) -> Tuple[bool, Path, Path]:
    """

    In general, the sources should go into a directory named after the
    source package name and upstream version (with a hyphen, not an
    underscore, in between) so ideally the upstream tarball will unpack
    into a directory called "hithere-1.0".

    The function checks it and, if this is not the case, rename the folder

    :param tarball: the tarball to check
    :param package_name: name of the package to verify
    :param version_number: version number of the package
    :param output_directory: directory where we will put updated tarball
    :return: triple. first element is true if we the tarball in input was valid. second element is meaningful only
    if the first element of the pair is False and yield the path of the newly updated tarball. The third element is
    the path to the unpacked (debian compliant) folder (which is also the source tree in the debian documentation)

    :see: https://wiki.debian.org/Packaging/Intro?action=show&redirect=IntroDebianPackaging
    """

    check_folder = os.path.abspath(os.path.join(output_directory, "tarball-check"))
    os.removedirs(check_folder)
    os.makedirs(check_folder, exist_ok=True)

    run_command(f"tar -xf {tarball}", cwd=check_folder)

    with os.scandir(check_folder) as it:
        count = 0
        for _f in it:
            # there should be only one folder there
            f: os.DirEntry = _f

            if not f.is_dir():
                continue
            if count >= 1:
                raise ValueError(f"folder {check_folder} does not contain only one folder!")
            count += 1
            unpacked_folder_name = f.name
            unpacked_folder_path = os.path.abspath(os.path.join(check_folder, f.path))
            if is_string_valid_tarball_unpack_directory_name(unpacked_folder_name, package_name, version_number):
                return True, unpacked_folder_path, unpacked_folder_path
    # unpacking was invalid. Rename the folder to make it valid
    new_folder_name = get_tarball_valid_unpack_directory_name(package_name, version_number)
    new_folder_path = os.path.join(check_folder, new_folder_name)
    os.rename(src=unpacked_folder_name, dst=new_folder_name)

    # now repack it. We use the tar command because we obtain the folder by unpacking the previous source tarball
    result = os.path.abspath(os.path.join(output_directory, new_folder_name + ".tar.gz"))
    run_command(f"tar -czvf {result} {new_folder_path}")
    return False, result, new_folder_path


def generate_debian_folder(output_directory: Path) -> Path:
    """
    Create the structure of folder that will be the foundation for creating the .deb file

    :param output_directory: directory where to put the debian folder
    :return: path of the root of the debian folder
    """
    debian_directory = os.path.abspath(os.path.join(output_directory, "debian"))

    os.removedirs(debian_directory)
    os.makedirs(debian_directory, exist_ok=True)

    return debian_directory


def generate_changelog(output_directory: Path, package_name: str, version_number: str, bugs_to_close: List[int], urgency: str, vendor: str, distribution: str) -> Path:
    """
    Generate the changelog file


    :param output_directory: directory where to put the change log
    :param package_name: name fo the source package name
    :param version_number: number of the version
    :param bugs_to_close: list of id of bugs that this deb package update closes
    :return: the path to the changelog
    """

    run_command(
        f"debchange --append --newversion={version_number} --package={package_name} --closes={','.join(map(str, bugs_to_close))} --noquery --urgency={urgency} --distribution={distribution} --vendor={vendor} --controlmaint",
        cwd=output_directory
    )

    return os.path.join(output_directory, "changelog")


def generate_compat(output_directory: Path, compatibility_level: int = 10) -> Path:
    result = os.path.join(output_directory, "compat")
    with open(result, "w") as f:
        f.write(f"10")
    return result

def generate_control(output_directory: Path, package_name: str, maintainer_name: str, maintainer_mail: str, priority: str, dependencies: List[Dependency])
    result = os.path.join(output_directory, "control")
    with open(result, "w") as f:
        f.write(f"Source: {package_name}\n")
        f.write(f"Maintainer: {maintainer_name} <{maintainer_mail}>\n")
        f.write(f"Section: misc\n")
        f.write(f"Priority: {priority}\n")
        f.write(f"Build-Depends: {', '.join(map(lambda x: x.to_build_depends, dependencies))}\n")
        f.write(f"\n")
        f.write(f"Package: {package_name}\n")
        f.write(f"Architecture: {', '.join(architectures)}\n")
        f.write(f"Depends: ${{shlibs:Depends}}, ${{misc:Depends}}\n")
        f.write(f"Description: {brief_description}\n{long_description}\n")
    return result

def main():
    parser = argparse.ArgumentParser("debCreator",
        description="""
        Easy way to create a .deb package.
        Nothing too fancy.
        """
    )
    parser.add_argument("--folder-to-updload", required=True, type=str, help="""
    The root folder of the directory you want to upload. E.g., /home/foobar/cpp/myProject will create a
    tar from myProject.
    """)
    parser.add_argument("--folder-to-upload-vcs", required=False, type=str, default=None, choices=["git", ], help="""
        If specified, it tells which Version Control System folder-to-upload has. This is in turn used to create the source
        tarball (file.tar.gz). If you don't use version control system, the application will tar EVERYTHING from that folder.
    """)
    parser.add_argument("--package-name", required=True, type=str, help="""
        The name of the package to build. only lowercase letters, digits and dashes are accepted here.
    """)
    parser.add_argument("--version-number", required=True, type=str, help="""
        The version number of the package to build. E.g., 0.1, 1.3
    """)
    parser.add_argument("--temp-directory", required=False, default="/tmp", type=str, help="""
        Directory where to put temporary files. You should have permissions to write there
    """)
    parser.add_argument("--bugs-to-close", required=False, default="", type=str, help="""
        A comma separeted list of numbers, each representing a bug that this deb package update closes.
        E.g., --bugs-to-close="", --bugs-to-close="3", --bugs-to-close="3,5", 
    """)
    parser.add_argument("--vendor", required=True, type=str, help="""
        Vendor of the package. Used for sanity checking of the target distribution.
        For further information see the man page of debchange.
    """)
    parser.add_argument("--urgency", required=True, type=str, choices=["medium"], help="""
        Urgency of the package.
        For further information see the man page of debchange.
    """)
    parser.add_argument("--distribution", required=True, type=str, help="""
        Distribution of the package.
        For further information see the man page of debchange.
    """)
    parser.add_argument("--maintainer-name", required=True, type=str, help="""
        Name of the person who is responsible for this package
    """)
    parser.add_argument("--maintainer-mail", required=True, type=str, help="""
        Mail of the person who is responsible for this package
    """)
    parser.add_argument("--priority", required=True, type=str, choices=["optional", "extra"], help="""
        Choose optional for normal packages. Choose extra if the package conflicts with another optional package
        or if its' not intended to be used on a standard desktop installation (e.g., debug packages).
        For more information, see https://wiki.debian.org/Packaging/Intro?action=show&redirect=IntroDebianPackaging
    """)
    parser.add_argument("--dependency", nargs="*", type=str, help="""
        A dependency of this package. A dependency is declare as the name of the dependent package, a type and a version,
        each separated by a ",". Type can be either "=", ">=", ">", "<", "<=".
        For example "metis,>=,5" says that the building package requires at least version 5 of the pacakge metis
    """)
    options, _ = parser.parse_args(sys.argv[1:])

    folder_to_upload = options.folder_to_upload
    folder_to_upload_vcs = options.folder_to_upload_vcs
    package_name = options.package_name
    version_number = options.version_number
    temp_directory = options.temp_directory
    bugs_to_close = list(map(int, options.bugs_to_close.split(",")))
    urgency = options.urgency
    vendor = options.vendor
    distribution = options.distribution
    priority = options.priority
    maintainer_name = options.maintainer_name
    maintainer_mail = options.maintainer_mail
    dependency_list = list(map(lambda x: Dependency(name=x[0], type=x[1], version=x[2]), map(lambda x: x.split(","), options.dependency)))


    setup_system()
    tarball_path = create_tarball(
        package_name=package_name,
        version_number=version_number,
        folder_to_upload=folder_to_upload,
        folder_to_upload_vcs=folder_to_upload_vcs,
        output_directory=temp_directory
    )
    is_valid, tarball, unpacked_directory = ensure_tarball_unpack_into_valid_folder(
        tarball=tarball_path,
        package_name=package_name,
        version_number=version_number,
        output_directory=temp_directory,
    )
    debian_folder = generate_debian_folder(output_directory=unpacked_directory)

    changelog = generate_changelog(
        output_directory=debian_folder,
        package_name=package_name,
        version_number=version_number,
        bugs_to_close=bugs_to_close,
        urgency=urgency,
        vendor=vendor,
        distribution =distribution,
    )
    compat = generate_compat(
        output_directory=temp_directory,
        compatibility_level=10
    )

    generate_control(
        output_directory=temp_directory,
        package_name=package_name,
        priority=priority,
        maintainer_name=maintainer_name,
        maintainer_mail=maintainer_mail,
        dependencies=dependency_list,
    )


def setup_system():
    run_command("sudo apt-get install build-essential fakeroot devscripts")


if __name__=="__main__":
    main()
