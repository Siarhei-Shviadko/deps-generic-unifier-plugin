import pytest

from deps_generic_unifier_plugin.extension_extractor import ExtensionExtractor


@pytest.fixture(
    params=(
        "tests/data/vector.pDf",
        "tests/data/你好我的名字是2.pdf",
        "tests/data/}{~5.pdf",
        "tests/data/ішоў3.pdf",
        "tests/data/.....pdf",
    ),
)
def file_path(request):
    return request.param


def test_extension_extractor__extract__extracted(file_path):
    extractor = ExtensionExtractor(file_path)

    assert extractor.extract() == "pdf"
