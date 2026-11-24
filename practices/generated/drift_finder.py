# --------------------------------------------------------------------------------
# The drift finder: where generated/ differs from what the masters render to
# --------------------------------------------------------------------------------
# One list entry per file: its drift line, then for a changed text file the diff.
# --------------------------------------------------------------------------------

import difflib

from practices.generated.generated_file import GeneratedFile
from practices.generated.generated_folder import GENERATED_FOLDER


# --------------------------------------------------------------------------------
# Finding drift
# --------------------------------------------------------------------------------

def find_drift(
    expected_by_path_map: dict[str, GeneratedFile], actual_by_path_map: dict[str, GeneratedFile]
) -> list[str]:
    drift_list = []

    for generated_path in sorted(set(expected_by_path_map) | set(actual_by_path_map)):
        if generated_path not in actual_by_path_map:
            drift_list.append(f"missing file: {GENERATED_FOLDER}/{generated_path}")
        elif generated_path not in expected_by_path_map:
            drift_list.append(f"extra file: {GENERATED_FOLDER}/{generated_path}")
        else:
            expected = expected_by_path_map[generated_path]
            actual = actual_by_path_map[generated_path]

            if expected.content != actual.content:
                drift_list.append(_describe_changed_file(generated_path, expected, actual))
            elif expected.executable != actual.executable:
                drift_list.append(f"changed mode: {GENERATED_FOLDER}/{generated_path}")

    return drift_list


# --------------------------------------------------------------------------------

def _describe_changed_file(generated_path: str, expected: GeneratedFile, actual: GeneratedFile) -> str:
    drift_line = f"changed file: {GENERATED_FOLDER}/{generated_path}"

    try:
        expected_line_list = expected.content.decode("utf-8").splitlines()
        actual_line_list = actual.content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return drift_line

    diff_line_list = difflib.unified_diff(
        expected_line_list,
        actual_line_list,
        fromfile=f"expected {generated_path}",
        tofile=f"{GENERATED_FOLDER}/{generated_path}",
        n=3,
        lineterm="",
    )

    return "\n".join([drift_line, *diff_line_list])
