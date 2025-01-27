from enum import Enum

class DocumentElementType(Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    FORMULA = "formula"
    IMAGE_CAPTION = "image_caption"
    TABLE_CAPTION = "table_caption"
    FORMULA_CAPTION = "formula_caption"