import os
import sys
import json
import unittest

from verbatim.config import Config
from verbatim.verbatim import Verbatim
from verbatim.audio.sources.factory import create_audio_source
from verbatim.eval.compare import compute_metrics
from verbatim.eval.find import find_reference_file
from verbatim.transcript.format.json import read_dlm_utterances, read_utterances

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Use CPU only


class TestPipeline(unittest.TestCase):
    def test_pipeline_quick(self):
        """
        Quickly test the pipeline with a short audio file.
        """
        # Find audio file based on name
        name = "WizardOfOzToto"
        filename = None
        for file in os.listdir("audio"):
            if name in file:
                filename = file
                break
        if filename is None:
            raise FileNotFoundError(f"No audio file found with name '{name}'")
        audio_path = f"audio/{filename}"

        # Find reference file
        base_name = filename.split(".")[0][:-10]  # also exclude the duration timestamp at the end
        ref_path = find_reference_file(base_name)

        # Check if reference file was found
        if ref_path is None:
            raise FileNotFoundError(f"No reference file found for '{base_name}'")

        # Get the filename without extension of the reference file
        ref_filename = os.path.basename(ref_path).split(".")[0]

        # Get language from filename
        language_string = filename.split("_")[2]
        if "-" in language_string:
            languages = language_string.split("-")
        else:
            languages = [language_string]

        # Load reference transcripts
        with open(ref_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            ref_utterances = (
                read_dlm_utterances(ref_path) if data.get("utterances") and "ref_text" in data["utterances"][0] else read_utterances(ref_path)
            )
            print(ref_utterances)

        # Initialize and run transcription (use cpu)
        config = Config(device="cpu").configure_languages(languages)
        source = create_audio_source(input_source=audio_path, device=config.device)
        verbatim = Verbatim(config=config)

        # Process audio
        all_utterances = []
        with source.open() as audio_stream:
            for utterance, _, _ in verbatim.transcribe(audio_stream=audio_stream):
                all_utterances.append(utterance)

        # Evaluate results
        metrics = compute_metrics(all_utterances, ref_utterances)
        print(metrics)

        # Load expected metrics
        with open("tests/data/ground_truth/metrics.json", "r", encoding="utf-8") as f:
            expected_metrics = json.load(f)
            expected_wer = expected_metrics.get(ref_filename, {}).get("WER")
            expected_wder = expected_metrics.get(ref_filename, {}).get("WDER")
            expected_cpwer = expected_metrics.get(ref_filename, {}).get("cpWER")

        # Verify performance
        assert metrics.WER <= expected_wer, f"WER is too high: {metrics.WER} > {expected_wer}"
        assert metrics.WDER <= expected_wder, f"WDER is too high: {metrics.WDER} > {expected_wder}"
        assert metrics.cpWER <= expected_cpwer, f"cpWER is too high: {metrics.cpWER} > {expected_cpwer}"



if __name__ == "__main__":
    unittest.main()
