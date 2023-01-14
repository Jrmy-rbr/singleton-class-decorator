import shutil
import subprocess
import os
import sys
import tempfile

sys.path = list(set(sys.path + [os.getcwd()]))
current_path = os.getcwd()
cmd = "./get_coverage.sh"
coverage_fraction: str = subprocess.run([cmd], stdout=subprocess.PIPE).stdout.decode().replace("\n", "")


def make_new_line(coverage_fraction):
    return (
        f"![coverage_badge](https://img.shields.io/badge/coverage-{coverage_fraction}25-{get_color(coverage_fraction)})"
    )


def get_color(coverage_fraction):
    coverage_fraction = int(coverage_fraction.replace("%", ""))
    bool_list = [
        coverage_fraction == 100,
        *[threshold - 10 <= coverage_fraction < threshold for threshold in range(100, 50, -10)],
        coverage_fraction < 50,
    ]
    return_list = ["brighgreen", "green", "yellowgreen", "yellow", "orange", "red"]
    return return_list[bool_list.index(True)]


def insert_line_front(insert_filename, to_insert):
    directory = os.path.dirname(insert_filename)
    with open(insert_filename) as src, tempfile.NamedTemporaryFile("w", dir=directory, delete=False) as dst:
        src.readline()  # Discard first line
        dst.write(to_insert + "\n")  # Save the new first line
        shutil.copyfileobj(src, dst)  # Copy the rest of the file

    os.unlink(insert_filename)  # remove old version
    os.rename(dst.name, insert_filename)  # rename new version


new_first_line = make_new_line(coverage_fraction)
insert_line_front("README.md", new_first_line)
