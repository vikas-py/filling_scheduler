"""
Pydantic schemas for request/response validation.

Defines data models for:
- Authentication (users, tokens)
- Schedules (requests, responses)
- Comparisons
- Configuration templates
"""

import json
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# ============================================================================
# Authentication Schemas
# ============================================================================


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime


class TokenResponse(BaseModel):
    """Schema for JWT token response."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""

    email: str | None = None
    user_id: int | None = None


# ============================================================================
# Schedule Schemas
# ============================================================================


class ScheduleRequest(BaseModel):
    """Schema for creating a new schedule."""

    name: str | None = Field(None, description="Optional schedule name")
    lots_data: list[dict[str, Any]] = Field(..., description="List of lot dictionaries")
    strategy: str = Field("smart-pack", description="Scheduling strategy")
    config: dict[str, Any] | None = Field(None, description="Configuration overrides")
    start_time: str | None = Field(None, description="Start time (ISO format)")


class ScheduleResponse(BaseModel):
    """Schema for schedule response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None
    strategy: str
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None


class ScheduleDetailResponse(ScheduleResponse):
    """Schema for detailed schedule response with results."""

    result: Optional["ScheduleResultResponse"] = None


class ScheduleResultResponse(BaseModel):
    """Schema for schedule result."""

    model_config = ConfigDict(from_attributes=True)

    makespan: float
    utilization: float
    changeovers: int
    lots_scheduled: int
    window_violations: int
    kpis: dict[str, Any] = Field(..., alias="kpis_json")
    activities: list[dict[str, Any]] = Field(..., alias="activities_json")


class ScheduleListResponse(BaseModel):
    """Schema for paginated schedule list."""

    schedules: list[ScheduleResponse]
    total: int
    page: int
    page_size: int


# ============================================================================
# Comparison Schemas
# ============================================================================


class CompareRequest(BaseModel):
    """Schema for strategy comparison request."""

    lots_data: list[dict[str, Any]] = Field(..., description="List of lot dictionaries")
    strategies: list[str] = Field(..., description="List of strategies to compare")
    config: dict[str, Any] | None = Field(None, description="Configuration overrides")
    start_time: str | None = Field(None, description="Start time (ISO format)")


class ComparisonResultItem(BaseModel):
    """Schema for single comparison result."""

    strategy: str
    makespan: float
    utilization: float
    changeovers: int
    lots_scheduled: int
    window_violations: int
    execution_time: float


class CompareResponse(BaseModel):
    """Schema for comparison response."""

    results: list[ComparisonResultItem]
    best_strategy: str
    sort_by: str = "makespan"


# ============================================================================
# File Upload Schemas
# ============================================================================


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""

    filename: str
    size: int
    content_type: str
    rows: int | None = None
    columns: list[str] | None = None


class ValidationErrorResponse(BaseModel):
    """Schema for validation error response."""

    field: str
    message: str
    value: Any


# ============================================================================
# Comparison Schemas
# ============================================================================


class ComparisonRequest(BaseModel):
    """Schema for comparison creation request."""

    name: str | None = Field(None, max_length=255, description="Comparison name")
    lots_data: list[dict[str, Any]] = Field(..., description="Lots data to compare")
    strategies: list[str] = Field(
        ...,
        min_length=2,
        max_length=6,
        description="List of strategies to compare (2-6 strategies)",
    )
    config: dict[str, Any] | None = Field(
        None, description="Shared configuration for all strategies"
    )
    start_time: str | None = Field(None, description="ISO 8601 datetime string for schedule start")


class ComparisonStrategyResult(BaseModel):
    """Schema for a single strategy result in a comparison."""

    model_config = ConfigDict(from_attributes=True)

    strategy: str
    status: str
    error_message: str | None = None
    makespan: float | None = None
    utilization: float | None = None
    changeovers: int | None = None
    lots_scheduled: int | None = None
    window_violations: int | None = None
    execution_time: float | None = Field(None, description="Execution time in seconds")
    kpis: dict[str, Any] | None = Field(None, alias="kpis_json")
    activities: list[dict[str, Any]] | None = Field(None, alias="activities_json")


class ComparisonResponse(BaseModel):
    """Schema for comparison creation response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str | None = None
    strategies: list[str]
    status: str
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class ComparisonDetailResponse(ComparisonResponse):
    """Schema for detailed comparison response with results."""

    best_strategy: str | None = None
    error_message: str | None = None
    results: list[ComparisonStrategyResult] | None = None


class ComparisonListResponse(BaseModel):
    """Schema for paginated comparison list response."""

    comparisons: list[ComparisonResponse]
    total: int
    page: int
    page_size: int
    pages: int


# ============================================================================
# Common Schemas
# ============================================================================


class MessageResponse(BaseModel):
    """Schema for simple message response."""

    message: str
    detail: str | None = None


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""

    status: str
    app: str
    version: str


class ErrorResponse(BaseModel):
    """Schema for error response."""

    error: str
    detail: str | None = None
    status_code: int


# ============================================================================
# Configuration Template Schemas
# ============================================================================


class ConfigTemplateBase(BaseModel):
    """Base configuration template schema."""

    name: str = Field(..., min_length=1, max_length=255, description="Template name")
    description: str | None = Field(None, description="Template description")
    config: dict[str, Any] = Field(..., description="Configuration dictionary")


class ConfigTemplateCreate(ConfigTemplateBase):
    """Schema for creating a configuration template."""

    is_public: bool = Field(default=False, description="Make template visible to all users")


class ConfigTemplateUpdate(BaseModel):
    """Schema for updating a configuration template."""

    name: str | None = Field(None, min_length=1, max_length=255, description="Template name")
    description: str | None = Field(None, description="Template description")
    config: dict[str, Any] | None = Field(None, description="Configuration dictionary")
    is_public: bool | None = Field(None, description="Make template visible to all users")


class ConfigTemplateResponse(BaseModel):
    """Schema for configuration template response."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int
    name: str
    description: str | None = None
    config: dict[str, Any] = Field(
        ..., validation_alias="config_json", serialization_alias="config"
    )
    is_public: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime

    @field_validator("config", mode="before")
    @classmethod
    def parse_config_json(cls, v):
        """Convert JSON string to dict if needed."""
        if isinstance(v, str):
            return json.loads(v)
        return v


class ConfigTemplateListResponse(BaseModel):
    """Schema for paginated configuration template list response."""

    templates: list[ConfigTemplateResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SetDefaultRequest(BaseModel):
    """Schema for setting default configuration."""

    pass  # No body needed, just POST to endpoint


class ConfigValidationResponse(BaseModel):
    """Schema for configuration validation response."""

    valid: bool
    errors: list[str] = []
    warnings: list[str] = []
