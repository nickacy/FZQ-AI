from enum import Enum
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LanguageCode(str, Enum):
    EN = "en"
    ZH = "zh"
    JA = "ja"
    KO = "ko"
    FR = "fr"
    DE = "de"
    ES = "es"
    RU = "ru"
    AR = "ar"


class RegionCode(str, Enum):
    GLOBAL = "global"
    US = "us"
    CN = "cn"
    EU = "eu"
    APAC = "apac"
    MIDDLE_EAST = "middle_east"
    AFRICA = "africa"
    LATAM = "latam"


class NewsSource(str, Enum):
    OFFICIAL = "official"
    MEDIA = "media"
    SOCIAL = "social"
    BLOG = "blog"
    RSS = "rss"
    API = "api"


class RawNewsItem(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-id-123", description="Unique identifier")
    title: str = Field(default="Mock News Title", description="News title")
    content: str = Field(default="Mock news content for testing.", description="Raw content")
    language: LanguageCode = Field(default=LanguageCode.EN, description="Language code")
    region: RegionCode = Field(default=RegionCode.GLOBAL, description="Region code")
    source: NewsSource = Field(default=NewsSource.API, description="News source")
    timestamp: datetime = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Publication timestamp")
    url: Optional[str] = Field(default="https://example.com/mock", description="Source URL")
    raw_text: Optional[str] = Field(default="Mock raw extracted text", description="Raw extracted text")


class TranslatedNewsItem(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(default="mock-translated-123", description="Unique identifier")
    original_id: str = Field(default="mock-original-123", description="Reference to raw item")
    language: LanguageCode = Field(default=LanguageCode.ZH, description="Target language")
    title: str = Field(default="Mock Translated Title", description="Translated title")
    content: str = Field(default="Mock translated content for testing.", description="Translated content")
    translator: Optional[str] = Field(default="mock-translator", description="Translator name or model")
    confidence: Optional[float] = Field(default=1.0, ge=0, le=1, description="Translation confidence")
    translated_at: Optional[datetime] = Field(default=datetime(2024, 1, 1, 0, 0, 0), description="Translation timestamp")
