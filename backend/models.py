from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(
        min_length=2,
        max_length=150,
    )

    parties: str = Field(
        min_length=2,
        max_length=4000,
    )

    terms: str = Field(
        min_length=2,
        max_length=12000,
    )

    effective_date: str = Field(
        min_length=2,
        max_length=100,
    )

    jurisdiction: str = Field(
        default="India",
        min_length=2,
        max_length=150,
    )

    additional_instructions: str = Field(
        default="",
        max_length=4000,
    )

    @field_validator(
        "document_type",
        "parties",
        "terms",
        "effective_date",
        "jurisdiction",
        "additional_instructions",
    )
    @classmethod
    def strip_values(cls, value: str) -> str:
        return value.strip()