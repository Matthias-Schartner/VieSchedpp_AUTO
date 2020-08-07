from pathlib import Path
import re

from Helper import read_sources, Message


def vlba_vex_file(**kwargs):
    path_selected = kwargs["path"]
    code = kwargs["session"]["code"].lower()
    path_to_skd = Path(path_selected) / (code + ".skd")
    path_to_vex = Path(path_selected) / (code + ".vex")
    # TODO: generate new .vex file in "sked" format
    # TODO: execute vlba_vex_correct on this .vex file and replace the existing one
    pass


def upload_vex_in_sked_format(**kwargs):
    path = kwargs["path"]
    print("TODO: convert .skd to .vex in \"sked format\" and upload it")
    pass


def VGOS_procs_block(**kwargs):
    path = kwargs["path"]
    session = kwargs["session"]
    stations = session["stations"]
    program_code = kwargs["program_code"]

    procs_cat = Path("Templates") / program_code / "procs.cat"
    if not procs_cat.exists():
        Message.addMessage("[WARNING] procs.cat file not found!", dump="session")
        return

    skd_file = next(Path(path).glob("*.skd"))

    re_begin = re.compile(r"BEGIN\s+(\w+)")
    re_end = re.compile(r"END\s+(\w+)")
    with open(skd_file, 'a') as f_skd:
        f_skd.write("$PROCS\n")

        with open(procs_cat) as f_procs:
            flag_write = False
            for l in f_procs:
                re_begin_search = re_begin.search(l)
                if re_begin_search:
                    station = re_begin_search.group(1)
                    if station == "COMMON" or station in stations:
                        flag_write = True

                if re_end.search(l):
                    f_skd.write(l)
                    flag_write = False

                if flag_write:
                    f_skd.write(l)


def VGOS_Broadband_block_512_8192_4096(**kwargs):
    path = kwargs["path"]
    session = kwargs["session"]
    stations = session["stations"]

    broadband_string = "$BROADBAND\n"
    for sta in stations:
        broadband_string += "{:8s}   512.00    8192       4096\n".format(sta)

    skd_file = next(Path(path).glob("*.skd"))
    with open(skd_file, 'r') as f:
        skd_content = f.read()

    skd_content = skd_content.replace("$BROADBAND\n", broadband_string)

    with open(skd_file, 'w') as f:
        f.write(skd_content)


def update_source_list(**kwargs):
    path = kwargs["path"]
    ds = kwargs["ds"]
    session = kwargs["session"]
    session_code = session["code"]
    program_code = kwargs["program_code"]

    target_source_list = Path("Templates") / program_code / "source.cat.target"
    calib_source_list = Path("Templates") / program_code / "source.cat.calib"

    targets, target_list, target_comment = read_sources(target_source_list)
    calibs, calib_list, calib_comment = read_sources(calib_source_list)

    target_comment = ["" if c.strip() == session_code else c.strip() for c in target_comment]
    calib_comment = ["" if c.strip() == session_code else c.strip() for c in calib_comment]

    _update_source_list_comment(ds, session_code, targets, target_comment)
    _update_source_list_comment(ds, session_code, calibs, calib_comment)

    _write_source_list(target_source_list, target_list, target_comment)
    _write_source_list(calib_source_list, calib_list, calib_comment)


def _update_source_list_comment(ds, session_code, name, comment):
    for idx, (n, c) in enumerate(zip(name, comment)):
        column_name = "n_src_scans_" + n
        if column_name in ds:
            val = ds[column_name]
            if val > 4:
                comment[idx] = session_code


def _write_source_list(path, list, comment):
    with open(path, 'w') as f:
        for l, c in zip(list, comment):
            c = c.strip()
            if c:
                f.write(l + "* " + c + "\n")
            else:
                f.write(l + "\n")
