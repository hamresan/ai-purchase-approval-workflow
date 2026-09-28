class CatalogItemMatcher:
    def matches(self, requested_description: str, catalog_description: str) -> bool:
        requested_tokens = self._normalize_tokens(requested_description)
        catalog_tokens = self._normalize_tokens(catalog_description)
        return requested_tokens == catalog_tokens

    def _normalize_tokens(self, description: str) -> tuple[str, ...]:
        return tuple(self._normalize_token(token) for token in description.split())

    @staticmethod
    def _normalize_token(token: str) -> str:
        normalized = token.casefold()
        if normalized.endswith("s") and not normalized.endswith("ss") and len(normalized) > 1:
            return normalized[:-1]
        return normalized
