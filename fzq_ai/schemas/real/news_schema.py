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

    id: str = Field(..., description="Unique identifier")
    title: str = Field(..., description="News title")
    content: str = Field(..., description="Raw content")
    language: LanguageCode = Field(..., description="Language code")
    region: RegionCode = Field(..., description="Region code")
    source: NewsSource = Field(..., description="News source")
    timestamp: datetime = Field(..., description="Publication timestamp")
    url: Optional[str] = Field(default=None, description="Source URL")
    raw_text: Optional[str] = Field(default=None, description="Raw extracted text")


class TranslatedNewsItem(BaseModel):
    model_config = ConfigDict(frozen=False, protected_namespaces=())

    id: str = Field(..., description="Unique identifier")
    original_id: str = Field(..., description="Reference to raw item")
    language: LanguageCode = Field(..., description="Target language")
    title: str = Field(..., description="Translated title")
    content: str = Field(..., description="Translated content")
    translator: Optional[str] = Field(default=None, description="Translator name or model")
    confidence: Optional[float] = Field(default=None, ge=0, le=1, description="Translation confidence")
    translated_at: Optional[datetime] = Field(default=None, description="Translation timestamp")
