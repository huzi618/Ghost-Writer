from langchain.chains.query_constructor.base import AttributeInfo

METADATA_FIELD_INFO = [
    AttributeInfo(
        name="source",
        description="source link of lyrics.",
        type="string",
    ),
    AttributeInfo(
        name="writer",
        description="The name of the person who wrote the lyrics.",
        type="string",
    ),
    AttributeInfo(
        name="song",
        description="The name of the song",
        type="string",
    ),
    ]