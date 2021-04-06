from typing import TypeVar


T = TypeVar('T')


class ResultNotFound(Exception):
    def __init__(self, instance: T, search_terms: str) -> None:
        self.msg = "No results found for this search."
        self.instance = instance
        self.search_terms = search_terms

        super().__init__(self.msg)


class DuplicateDocument(Exception):
    def __init__(self, instance: T, document_id: str) -> None:
        self.instance = instance
        self.document_id = document_id
        self.instance_type = type(instance).__name__
        self.msg = ("Duplicated document found for: "
                    f"{self.instance_type}/{document_id}")

        super().__init__(self.msg)


class ResourceNotDefined(Exception):
    def __init__(self, resource_type: str) -> None:
        self.msg = f"No definition found for resource type: {resource_type}"
        self.resource_type = resource_type

        super().__init__(self.msg)
