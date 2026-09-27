from pydantic import BaseModel, Field, field_validator


class DocumentRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    parties: str = Field(min_length=2, max_length=5000)
    terms: str = Field(min_length=2, max_length=10000)
    effective_date: str = Field(min_length=2, max_length=100)
    jurisdiction: str = Field(default="", max_length=300)
    special_instructions: str = Field(default="", max_length=5000)
    company_name: str = Field(default="LegalEase", max_length=200)
    footer_text: str = Field(
        default="Generated with LegalEase — review with a qualified legal professional.",
        max_length=500,
    )

    @field_validator("document_type", "parties", "terms", "effective_date")
    @classmethod
    def strip_required(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Value cannot be blank.")
        return value


class GenerateResponse(BaseModel):
    document_type: str
    text: str
    model: str
    demo_mode: bool


class ExportRequest(BaseModel):
    document_type: str = Field(min_length=2, max_length=120)
    text: str = Field(min_length=1, max_length=100000)
    terms: str = Field(default="", max_length=10000)
    company_name: str = Field(default="LegalEase", max_length=200)
    footer_text: str = Field(default="", max_length=500)
    logo_data_url: str | None = Field(default=None, max_length=5_000_000)
