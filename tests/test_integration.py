# Basic integration tests
import json
import logging
from pathlib import Path

import pandas as pd
import pytest

from eyeloop import run_eyeloop

TESTDATA_DIR = Path(__file__).parent / "testdata"

TEST_VIDEOS = {  # Basic short videos to use for end to end testing
    "short_human_3blink": {
        "path": Path(TESTDATA_DIR, "short_human_3blink.mp4").absolute(),
        "animal": "human",
        "blinks": 3,
        "n_frames": 282,
    },
    "short_mouse_noblink": {
        "path": Path(TESTDATA_DIR, "short_mouse_noblink.m4v").absolute(),
        "animal": "mouse",
        "blinks": 0,
        "n_frames": 307,
    }
}
logger = logging.getLogger(__name__)


def output_json_parser(json_file: Path) -> pd.DataFrame:
    data_log = json_file.read_text().splitlines()
    data_dicts = [json.loads(line) for line in data_log]
    return pd.DataFrame(data_dicts)


class TestIntegration:
    @pytest.mark.parametrize("test_video_name", ["short_human_3blink", "short_mouse_noblink"])
    def test_integration(self, tmpdir, test_video_name: str):
        test_video = TEST_VIDEOS[test_video_name]
        print(f"Running test on video {test_video}")
        testargs = ["--video", str(test_video["path"]),
                    "--output_dir", str(tmpdir)]
        eyeloop_obj = run_eyeloop.EyeLoop(args=testargs, logger=logger)

        # Ensure output is expected
        data_dir = list(Path(tmpdir).glob("trial_*"))[0]
        vid_frames = list(Path(data_dir).glob("frame_*.jpg"))
        assert len(vid_frames) == test_video["n_frames"] + 1  # Account for 0-indexing
        datalog = Path(data_dir, "datalog.json")
        assert datalog.exists()

        #data_df = output_json_parser(datalog)
        #assert len(data_df.index) == test_video["n_frames"]
        #assert Path(data_dir, "output.avi").exists()
        # TODO add assertions based on blink, cr and pupil values

    #def test_no_video_stream_error(self):
    #    with pytest.raises(ValueError) as excinfo:
    #        run_eyeloop.EyeLoop(args=[])
    #    assert "Failed to initialize video stream" in str(excinfo.value)

# Tests for each importer

# TODO Add tests that use that animal tag of the videos
