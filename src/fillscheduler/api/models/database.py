"""
SQLAlchemy database models.

Defines the database schema for:
- Users and authentication
- Schedules and results
- Configuration templates
"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """User model for authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    config_templates = relationship(
        "ConfigTemplate", back_populates="user", cascade="all, delete-orphan"
    )
    comparisons = relationship("Comparison", back_populates="user", cascade="all, delete-orphan")


class Schedule(Base):
    """Schedule model representing a scheduling job."""

    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=True)
    strategy = Column(String(50), nullable=False)
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    config_json = Column(Text, nullable=True)  # JSON string for SQLite, JSONB for PostgreSQL
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="schedules")
    result = relationship(
        "ScheduleResult", back_populates="schedule", uselist=False, cascade="all, delete-orphan"
    )


class ScheduleResult(Base):
    """Schedule result model storing the output of a scheduling job."""

    __tablename__ = "schedule_results"

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=False, unique=True)

    # KPIs
    makespan = Column(Float, nullable=False)
    utilization = Column(Float, nullable=False)
    changeovers = Column(Integer, nullable=False)
    lots_scheduled = Column(Integer, nullable=False)
    window_violations = Column(Integer, default=0, nullable=False)

    # Full data as JSON
    kpis_json = Column(Text, nullable=False)  # Complete KPIs dictionary
    activities_json = Column(Text, nullable=False)  # List of activities

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    schedule = relationship("Schedule", back_populates="result")


class ConfigTemplate(Base):
    """Configuration template model for saving and reusing configurations."""

    __tablename__ = "config_templates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    config_json = Column(Text, nullable=False)  # JSON string containing configuration
    is_public = Column(Boolean, default=False, nullable=False)  # If True, visible to all users
    is_default = Column(Boolean, default=False, nullable=False)  # If True, user's default config
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="config_templates")


class Comparison(Base):
    """Comparison model for comparing multiple scheduling strategies."""

    __tablename__ = "comparisons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=True)
    lots_data_hash = Column(String(64), nullable=False, index=True)  # SHA256 hash for caching
    lots_data_json = Column(Text, nullable=False)  # Store lots data for reproducibility
    strategies = Column(Text, nullable=False)  # JSON list of strategy names
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)
    config_json = Column(Text, nullable=True)  # Shared config for all strategies
    best_strategy = Column(String(50), nullable=True)  # Recommended strategy
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="comparisons")
    results = relationship(
        "ComparisonResult", back_populates="comparison", cascade="all, delete-orphan"
    )


class ComparisonResult(Base):
    """Result for a single strategy in a comparison."""

    __tablename__ = "comparison_results"

    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"), nullable=False)
    strategy = Column(String(50), nullable=False)
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, running, completed, failed
    error_message = Column(Text, nullable=True)

    # KPIs
    makespan = Column(Float, nullable=True)
    utilization = Column(Float, nullable=True)
    changeovers = Column(Integer, nullable=True)
    lots_scheduled = Column(Integer, nullable=True)
    window_violations = Column(Integer, nullable=True)

    # Full data as JSON
    kpis_json = Column(Text, nullable=True)  # Complete KPIs dictionary
    activities_json = Column(Text, nullable=True)  # List of activities

    # Execution time
    execution_time = Column(Float, nullable=True)  # Seconds

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    comparison = relationship("Comparison", back_populates="results")
