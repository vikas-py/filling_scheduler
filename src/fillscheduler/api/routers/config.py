"""
Configuration template router.

Endpoints for managing configuration templates:
- CRUD operations on templates
- Public template sharing
- Default configuration management
- Configuration validation
- Import/export functionality
"""

import json

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from fillscheduler.api.dependencies import get_current_active_user, get_db
from fillscheduler.api.models.database import ConfigTemplate, User
from fillscheduler.api.models.schemas import (
    ConfigTemplateCreate,
    ConfigTemplateListResponse,
    ConfigTemplateResponse,
    ConfigTemplateUpdate,
    ConfigValidationResponse,
    MessageResponse,
)
from fillscheduler.api.services.config import (
    export_config_to_dict,
    get_default_config,
    get_user_default_config,
    import_config_from_dict,
    set_user_default_config,
    unset_user_default_config,
    validate_config,
)

router = APIRouter()


@router.post("/config", response_model=ConfigTemplateResponse, status_code=201)
async def create_config_template(
    request: ConfigTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create a new configuration template.

    The configuration will be validated before creation.
    """
    # Validate configuration
    validation = validate_config(request.config)
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Invalid configuration",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
            },
        )

    # Create template
    template = ConfigTemplate(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        config_json=json.dumps(request.config),
        is_public=request.is_public,
        is_default=False,  # Not default by default
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    return ConfigTemplateResponse.model_validate(template)


@router.get("/configs", response_model=ConfigTemplateListResponse)
async def list_config_templates(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    public_only: bool = Query(False, description="Show only public templates"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List configuration templates.

    By default, shows user's own templates + public templates.
    Set public_only=true to show only public templates.
    """
    query = db.query(ConfigTemplate)

    if public_only:
        # Show only public templates
        query = query.filter(ConfigTemplate.is_public.is_(True))
    else:
        # Show user's own templates + public templates
        query = query.filter(
            (ConfigTemplate.user_id == current_user.id) | (ConfigTemplate.is_public.is_(True))
        )

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    templates = (
        query.order_by(ConfigTemplate.created_at.desc()).offset(offset).limit(page_size).all()
    )

    # Calculate total pages
    pages = (total + page_size - 1) // page_size

    # Convert templates to response format
    template_responses = [ConfigTemplateResponse.model_validate(template) for template in templates]

    return ConfigTemplateListResponse(
        templates=template_responses,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.put("/config/{template_id}", response_model=ConfigTemplateResponse)
async def update_config_template(
    template_id: int,
    request: ConfigTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update a configuration template.

    Only the owner can update a template.
    """
    # Get template (owner only)
    template = (
        db.query(ConfigTemplate)
        .filter(
            ConfigTemplate.id == template_id,
            ConfigTemplate.user_id == current_user.id,
        )
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update fields
    if request.name is not None:
        template.name = request.name

    if request.description is not None:
        template.description = request.description

    if request.config is not None:
        # Validate configuration
        validation = validate_config(request.config)
        if not validation["valid"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Invalid configuration",
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                },
            )
        template.config_json = json.dumps(request.config)

    if request.is_public is not None:
        template.is_public = request.is_public

    db.commit()
    db.refresh(template)

    return ConfigTemplateResponse.model_validate(template)


@router.delete("/config/default", response_model=MessageResponse)
async def unset_default_config_template(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Unset the user's default configuration template.

    After this, no template will be marked as default for the user.
    """
    unset_user_default_config(db, current_user.id)

    return MessageResponse(
        message="Default configuration template unset successfully",
    )


@router.delete("/config/{template_id}", response_model=MessageResponse)
async def delete_config_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Delete a configuration template.

    Only the owner can delete a template.
    If the template is the user's default, the default will be unset.
    """
    # Get template (owner only)
    template = (
        db.query(ConfigTemplate)
        .filter(
            ConfigTemplate.id == template_id,
            ConfigTemplate.user_id == current_user.id,
        )
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    db.delete(template)
    db.commit()

    return MessageResponse(
        message="Configuration template deleted successfully",
        detail=f"Deleted template: {template.name}",
    )


@router.post("/config/{template_id}/set-default", response_model=ConfigTemplateResponse)
async def set_default_config_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Set a configuration template as the user's default.

    Only the owner can set their own template as default.
    Any existing default will be unset.
    """
    try:
        template = set_user_default_config(db, current_user.id, template_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    return ConfigTemplateResponse.model_validate(template)


@router.get("/config/default", response_model=ConfigTemplateResponse | None)
async def get_default_config_template(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get the user's default configuration template.

    Returns null if no default is set.
    """
    template = get_user_default_config(db, current_user.id)

    if not template:
        return None

    return ConfigTemplateResponse.model_validate(template)


@router.post("/config/validate", response_model=ConfigValidationResponse)
async def validate_config_endpoint(
    config: dict,
    current_user: User = Depends(get_current_active_user),
):
    """
    Validate a configuration without saving it.

    Useful for pre-flight validation in the UI.
    """
    validation = validate_config(config)

    return ConfigValidationResponse(
        valid=validation["valid"],
        errors=validation["errors"],
        warnings=validation["warnings"],
    )


@router.get("/config/system/default", response_model=dict)
async def get_system_default_config(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the system default configuration.

    This is the base configuration used when no custom configuration is provided.
    """
    return get_default_config()


@router.post("/config/import", response_model=ConfigTemplateResponse, status_code=201)
async def import_config_template(
    import_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Import a configuration template from a dictionary.

    Expected format:
    {
        "name": "Template name",
        "description": "Optional description",
        "config": { ... configuration object ... }
    }
    """
    try:
        template = import_config_from_dict(db, current_user.id, import_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    return ConfigTemplateResponse.model_validate(template)


@router.get("/config/{template_id}", response_model=ConfigTemplateResponse)
async def get_config_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get a configuration template by ID.

    Users can access their own templates or public templates.
    """
    # Query for user's own template or public template
    template = (
        db.query(ConfigTemplate)
        .filter(
            ConfigTemplate.id == template_id,
            ((ConfigTemplate.user_id == current_user.id) | (ConfigTemplate.is_public.is_(True))),
        )
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return ConfigTemplateResponse.model_validate(template)


@router.get("/config/{template_id}/export", response_model=dict)
async def export_config_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Export a configuration template to a portable format.

    Users can export their own templates or public templates.
    """
    # Query for user's own template or public template
    template = (
        db.query(ConfigTemplate)
        .filter(
            ConfigTemplate.id == template_id,
            ((ConfigTemplate.user_id == current_user.id) | (ConfigTemplate.is_public.is_(True))),
        )
        .first()
    )

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return export_config_to_dict(template)
