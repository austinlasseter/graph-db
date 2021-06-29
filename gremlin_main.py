# -*- coding: utf-8 -*-


from helpers.setup_analysis import make_dirs
from helpers.process_json_files import process_json_files
from helpers.open_gremlin import run_gremlin


def main(analysis_name):
    make_dirs(analysis_name)
    process_json_files(analysis_name)
    run_gremlin()


if __name__ == "__main__":
    analysis_name = "gremlin_data_20210512"
    main(analysis_name)
