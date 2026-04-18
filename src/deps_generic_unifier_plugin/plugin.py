import logging

from deps_lil_chyn import (
    csv_unifier,
    doc_unifier,
    docx_unifier,
    eml_unifier,
    excel_unifier,
    image_unifier,
    msg_unifier,
    pdf_unifier,
    tiff_unifier,
    unifier_proxy,
)
from deps_lil_chyn.domain.dto import UnifiedContainerData
from deps_lil_chyn.domain.exceptions import UnknownDocumentExtension
from deps_lil_chyn.domain.interfaces import IUnifierPlugin
from deps_lil_chyn.infrastructure.services import (
    AbstractContainerUnifier,
    AbstractUnifier,
    UnifierProxy,
)
from deps_unified_data import UnifiedData

from deps_generic_unifier_plugin.extension_extractor import ExtensionExtractor

FIRST_ELEMENT: int = 0


class UnifierPlugin(IUnifierPlugin):
    def __init__(self):
        self._unifier_proxy: UnifierProxy = unifier_proxy()  # type: ignore

        self._unifiers: list[AbstractUnifier] = [  # type: ignore
            pdf_unifier(),
            image_unifier(),
            excel_unifier(),
            docx_unifier(),
            doc_unifier(),
            csv_unifier(),
            tiff_unifier(),
        ]

        self._container_unifiers: list[AbstractContainerUnifier] = [  # type: ignore
            eml_unifier(),
            msg_unifier(),
        ]

        self._logger = logging.getLogger(UnifierPlugin.__class__.__name__)

    def unify(self, document_id: str, files: list[str]) -> None:
        unified_data = self._unify_document(document_id, files)
        self._save_unified_data(unified_data)
        self._logger.info(f"Document with id '{document_id}' is unified.")

    def unify_container(self, document_id: int, file_path: str) -> UnifiedContainerData:
        container_unified_data = self._unify_container_document(file_path)
        self._logger.info(f"Document with id '{document_id}' is unified.")
        return container_unified_data

    def _unify_document(self, document_id: str, files: list[str]) -> UnifiedData:
        extension = ExtensionExtractor(files[FIRST_ELEMENT]).extract()
        for unifier in self._unifiers:
            if extension in unifier.extensions:
                self._logger.info(f"Document `{document_id}` will be unified by `{unifier.__class__.__name__}`")
                return unifier.unify(document_id, files)

        raise UnknownDocumentExtension(f"UnifierPlugin cannot unify document with '{extension}' extension")

    def _unify_container_document(self, file_path: str) -> UnifiedContainerData:
        extension = ExtensionExtractor(file_path).extract()
        for unifier in self._container_unifiers:
            if extension in unifier.extensions:
                return unifier.unify(file_path)

        raise UnknownDocumentExtension(f"UnifierPlugin cannot unify document with '{extension}' extension")

    def _save_unified_data(self, unified_data: UnifiedData) -> None:
        self._unifier_proxy.save_unified_data(unified_data)
