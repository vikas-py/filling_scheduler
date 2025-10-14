"""
Improved database models with performance optimizations and better data integrity.

This file contains the enhanced version of the database models with:
- Proper indexes on foreign keys and common query patterns
- Database-level constraints for data validation
- Audit trail fields
- Better naming conventions
- Denormalized fields for performance

To apply these changes:
1. Set up Alembic migrations (see docs/DATABASE_IMPROVEMENTS.md)
2. Create a migration from current schema to this one
3. Test thoroughly in development
4. Apply to production

Author: Database Review 2025-01-23
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base: Any = declarative_base()


class User(Base):
    """User model for authentication with audit fields."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)  # Added index
    is_superuser = Column(Boolean, default=False, nullable=False, index=True)  # Added index
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    config_templates = relationship(
        "ConfigTemplate", back_populates="user", cascade="all, delete-orphan"
    )
    comparisons = relationship("Comparison", back_populates="user", cascade="all, delete-orphan")

    # Table constraints
    __table_args__ = (
        CheckConstraint("length(email) >= 5", name="check_email_min_length"),
        CheckConstraint("email LIKE '%@%.%'", name="check_email_format"),
    )


class Schedule(Base):
    """Schedule model with improved indexes and constraints."""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Added index
    name = Column(String(255), nullable=True, index=True)  # Added index for searches
    strategy = Column(String(50), nullable=False, index=True)  # Added index for filters
    status = Column(String(50), default="pending", nullable=False, index=True)  # Added index
    error_message = Column(Text, nullable=True)

    # Configuration stored as JSON
    config_json = Column(Text, nullable=True)

    # Denormalized fields for performance (avoid JSON parsing)
    num_lots = Column(Integer, nullable=True)  # NEW: Cache lot count
    num_fillers = Column(Integer, nullable=True)  # NEW: Cache filler count
    file_name = Column(String(255), nullable=True)  # NEW: Original filename
    input_hash = Column(String(64), nullable=True, index=True)  # NEW: For deduplication

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit fields - NEW
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Soft delete - NEW
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Execution metrics - NEW
    execution_time = Column(Float, nullable=True)  # Seconds

    # Relationships
    user = relationship("User", back_populates="schedules", foreign_keys=[user_id])
    result = relationship(
        "ScheduleResult", back_populates="schedule", uselist=False, cascade="all, delete-orphan"
    )

    # Composite indexes for common query patterns
    __table_args__ = (
        # Status filtering by user
        Index("idx_schedules_user_status", "user_id", "status"),
        # Recent schedules by user
        Index("idx_schedules_user_created_desc", "user_id", "created_at"),
        # Strategy filtering by user
        Index("idx_schedules_user_strategy", "user_id", "strategy"),
        # Active schedules (not deleted)
        Index("idx_schedules_active", "user_id", "is_deleted", "created_at"),
        # Status validation
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="check_status_valid",
        ),
        # Strategy validation
        CheckConstraint(
            "strategy IN ('LPT', 'SPT', 'MILP', 'SMART', 'HYBRID', 'CFS')",
            name="check_strategy_valid",
        ),
        # Positive numbers
        CheckConstraint("num_lots IS NULL OR num_lots >= 0", name="check_num_lots_positive"),
        CheckConstraint(
            "num_fillers IS NULL OR num_fillers > 0", name="check_num_fillers_positive"
        ),
        CheckConstraint(
            "execution_time IS NULL OR execution_time >= 0", name="check_execution_time_positive"
        ),
    )


class ScheduleResult(Base):
    """Schedule result with validation constraints."""

    __tablename__ = "schedule_results"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(
        Integer, ForeignKey("schedules.id"), nullable=False, unique=True, index=True
    )

    # KPIs (nullable until job completes)
    makespan = Column(Float, nullable=True)
    utilization = Column(Float, nullable=True)
    changeovers = Column(Integer, nullable=True)
    lots_scheduled = Column(Integer, nullable=True)
    window_violations = Column(Integer, nullable=True, default=0)

    # Full data as JSON
    kpis_json = Column(Text, nullable=True)
    activities_json = Column(Text, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedule = relationship("Schedule", back_populates="result")

    # Validation constraints
    __table_args__ = (
        CheckConstraint("makespan IS NULL OR makespan >= 0", name="check_makespan_positive"),
        CheckConstraint(
            "utilization IS NULL OR (utilization >= 0 AND utilization <= 100)",
            name="check_utilization_range",
        ),
        CheckConstraint(
            "changeovers IS NULL OR changeovers >= 0", name="check_changeovers_positive"
        ),
        CheckConstraint(
            "lots_scheduled IS NULL OR lots_scheduled >= 0", name="check_lots_scheduled_positive"
        ),
        CheckConstraint(
            "window_violations IS NULL OR window_violations >= 0",
            name="check_window_violations_positive",
        ),
    )


class ConfigTemplate(Base):
    """Configuration template with better indexing."""

    __tablename__ = "config_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Added index
    name = Column(String(255), nullable=False, index=True)  # Added index
    description = Column(Text, nullable=True)
    config_json = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False, index=True)  # Added index
    is_default = Column(Boolean, default=False, nullable=False, index=True)  # Added index

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Audit fields - NEW
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Soft delete - NEW
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="config_templates", foreign_keys=[user_id])

    # Composite indexes
    __table_args__ = (
        Index("idx_config_user_public", "user_id", "is_public"),
        Index("idx_config_user_default", "user_id", "is_default"),
        Index("idx_config_public_active", "is_public", "is_deleted"),
    )


class Comparison(Base):
    """Comparison model with improved indexing."""

    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Added index
    name = Column(String(255), nullable=True, index=True)  # Added index
    lots_data_hash = Column(String(64), nullable=False, index=True)
    lots_data_json = Column(Text, nullable=False)
    strategies = Column(Text, nullable=False)  # JSON list
    status = Column(String(50), default="pending", nullable=False, index=True)  # Added index
    error_message = Column(Text, nullable=True)
    config_json = Column(Text, nullable=True)
    best_strategy = Column(String(50), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Audit fields - NEW
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Soft delete - NEW
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="comparisons", foreign_keys=[user_id])
    results = relationship(
        "ComparisonResult", back_populates="comparison", cascade="all, delete-orphan"
    )

    # Composite indexes and constraints
    __table_args__ = (
        Index("idx_comparison_user_status", "user_id", "status"),
        Index("idx_comparison_user_created", "user_id", "created_at"),
        Index("idx_comparison_hash", "lots_data_hash", "is_deleted"),  # For caching
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="check_comparison_status_valid",
        ),
    )


class ComparisonResult(Base):
    """Comparison result with validation."""

    __tablename__ = "comparison_results"

    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(
        Integer, ForeignKey("comparisons.id"), nullable=False, index=True
    )  # Added index
    strategy = Column(String(50), nullable=False, index=True)  # Added index
    status = Column(String(50), default="pending", nullable=False)
    error_message = Column(Text, nullable=True)

    # KPIs (nullable until completed)
    makespan = Column(Float, nullable=True)
    utilization = Column(Float, nullable=True)
    changeovers = Column(Integer, nullable=True)
    lots_scheduled = Column(Integer, nullable=True)
    window_violations = Column(Integer, nullable=True)

    # Full data as JSON
    kpis_json = Column(Text, nullable=True)
    activities_json = Column(Text, nullable=True)

    # Execution time
    execution_time = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    comparison = relationship("Comparison", back_populates="results")

    # Composite indexes and constraints
    __table_args__ = (
        Index("idx_comparison_result_strategy", "comparison_id", "strategy"),
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="check_comparison_result_status_valid",
        ),
        CheckConstraint(
            "makespan IS NULL OR makespan >= 0", name="check_comparison_makespan_positive"
        ),
        CheckConstraint(
            "utilization IS NULL OR (utilization >= 0 AND utilization <= 100)",
            name="check_comparison_utilization_range",
        ),
        CheckConstraint(
            "execution_time IS NULL OR execution_time >= 0",
            name="check_comparison_execution_time_positive",
        ),
    )
