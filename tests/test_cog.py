import re

from cogclassifier import const
from cogclassifier.cog import CogDefinitionRecord, CogFuncCategoryRecord


class TestCogFuncCategoryRecord:
    def test_len_method(self):
        """Test dunder len method"""
        cog_fc_rec = CogFuncCategoryRecord(const.COG_FUNC_CATEGORY_FILE)
        assert len(cog_fc_rec) == 26

    def test_str_method(self):
        """Test dunder str method"""
        cog_fc_rec = CogFuncCategoryRecord(const.COG_FUNC_CATEGORY_FILE)
        with open(const.COG_FUNC_CATEGORY_FILE) as f:
            expected_str = f.read()
        assert str(cog_fc_rec) == expected_str


class TestCogDefinitionRecord:
    def test_len_method(self):
        """Test dunder len method"""
        cog_def_rec = CogDefinitionRecord(const.COG_DEFINITION_FILE)
        assert len(cog_def_rec) == 5050

    def test_str_method(self):
        """Test dunder str method

        The officially provided COG Definition files do not always have
        a constant number of tabs at the end of each line.
        This test checks if the result is the same after removing trailing tabs.
        """

        def _remove_trailing_tabs(text: str) -> str:
            return re.sub(r"\t+$", "", text, flags=re.MULTILINE)

        cog_def_rec = CogDefinitionRecord(const.COG_DEFINITION_FILE)
        with open(const.COG_DEFINITION_FILE) as f:
            expected_str = _remove_trailing_tabs(f.read())
        assert _remove_trailing_tabs(str(cog_def_rec)) == expected_str
