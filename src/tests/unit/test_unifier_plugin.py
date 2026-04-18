from unittest import mock
from uuid import uuid4

import pytest
import requests_mock
from deps_lil_chyn.domain.exceptions import UnknownDocumentExtension
from deps_lil_chyn.infrastructure.services import DocxUnifier, ImageUnifier, PdfUnifier

FAKE_DOCUMENT_ID: str = uuid4().hex


@pytest.fixture
def pdf_unifier_mock(test_unified_data):
    patcher = mock.patch.object(PdfUnifier, "unify", return_value=test_unified_data)
    patcher.start()
    yield test_unified_data
    patcher.stop()


@pytest.fixture
def image_unifier_mock(test_unified_data):
    patcher = mock.patch.object(ImageUnifier, "unify", return_value=test_unified_data)
    patcher.start()
    yield test_unified_data
    patcher.stop()


@pytest.fixture
def docx_unifier_mock(test_unified_data):
    patcher = mock.patch.object(DocxUnifier, "unify", return_value=test_unified_data)
    patcher.start()
    yield test_unified_data
    patcher.stop()


def test_unifier_plugin__unify_pdf_document__edata_gotten(unifier_plugin, pdf_unifier_mock):
    expected_udata = pdf_unifier_mock
    files = ["tests/data/vector.pdf"]
    res = unifier_plugin._unify_document(expected_udata.document_id, files)

    assert res == expected_udata


def test_unifier_plugin__unify_png_document__edata_gotten(unifier_plugin, image_unifier_mock):
    expected_udata = image_unifier_mock
    files = ["tests/data/vector.PnG"]
    res = unifier_plugin._unify_document(expected_udata.document_id, files)

    assert res == expected_udata


def test_unifier_plugin__unify_jpg_document__edata_gotten(unifier_plugin, image_unifier_mock):
    expected_udata = image_unifier_mock
    files = ["tests/data/vector.jPg"]
    res = unifier_plugin._unify_document(expected_udata.document_id, files)

    assert res == expected_udata


def test_unifier_plugin__unify_jpeg_document__edata_gotten(unifier_plugin, image_unifier_mock):
    expected_udata = image_unifier_mock
    files = ["tests/data/vector.jpEG"]
    res = unifier_plugin._unify_document(expected_udata.document_id, files)

    assert res == expected_udata


def test_unifier_plugin____unify_docx_document__edata_gotten(unifier_plugin, docx_unifier_mock):
    expected_udata = docx_unifier_mock
    files = ["tests/data/file.docx"]
    res = unifier_plugin._unify_document(expected_udata.document_id, files)

    assert res == expected_udata


def test_unifier_plugin__wrong_extension__unknown_extension_error(unifier_plugin):
    files = ["tests/data/vector.scv"]

    with pytest.raises(UnknownDocumentExtension):
        unifier_plugin._unify_document(FAKE_DOCUMENT_ID, files)


def test_unifier_plugin__save_unified_data__requested(unifier_plugin, pdf_unifier_mock):
    unified_data = pdf_unifier_mock
    expected_json = {"documentId": unified_data.document_id, "elements": []}

    with requests_mock.mock() as rm:
        rm.put("http://deps-unifier:8000/api/unifier/v1/unified_data/upsert-data")
        unifier_plugin._save_unified_data(unified_data)

    assert rm.called
    assert rm.request_history[0].json() == expected_json
