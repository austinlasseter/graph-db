# -*- coding: utf-8 -*-

import sys
from helpers.setup_analysis import make_dirs
from helpers.process_json_files import process_json_files
from helpers.previz_prep import previz_prep
from helpers.make_viz import make_viz


def main(analysis_name, prime_repo):
    make_dirs(analysis_name)
    process_json_files(analysis_name, prime_repo)
    previz_prep(analysis_name, prime_repo)
    make_viz(analysis_name, prime_repo)


if __name__ == "__main__":
    analysis_name = sys.argv[1]
    prime_repo = sys.argv[2]
    main(analysis_name, prime_repo)
    print("end of line")
