"""
PDF Report Generator

Generates professional PDF reports from schedule data using WeasyPrint and Jinja2.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import io

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

from .chart_generator import (
    generate_gantt_chart_image,
    generate_utilization_chart_image,
    generate_activity_distribution_chart,
    generate_filler_breakdown_data,
)


def get_template_path() -> Path:
    """Get the path to the templates directory."""
    return Path(__file__).parent / 'templates'


def generate_pdf_report(
    schedule_data: Dict[str, Any],
    user_name: str = "System",
    include_charts: bool = True,
    output_path: Optional[str] = None,
) -> bytes:
    """
    Generate a professional PDF report from schedule data.
    
    Args:
        schedule_data: Dictionary containing schedule information:
            - schedule: Schedule model data (id, name, description, status, strategy, config)
            - results: ScheduleResult model data (makespan, utilization, changeovers, lots_scheduled)
            - activities: List of activity dictionaries
            - validation: Optional validation results (errors, warnings)
        user_name: Name of the user generating the report
        include_charts: Whether to include chart visualizations
        output_path: Optional path to save PDF file (otherwise returns bytes)
    
    Returns:
        PDF content as bytes (or writes to output_path if provided)
    
    Raises:
        ValueError: If required data is missing
        Exception: If PDF generation fails
    """
    # Validate required data
    if 'schedule' not in schedule_data:
        raise ValueError("schedule_data must contain 'schedule' key")
    if 'results' not in schedule_data:
        raise ValueError("schedule_data must contain 'results' key")
    
    schedule = schedule_data['schedule']
    results = schedule_data['results']
    activities = schedule_data.get('activities', [])
    validation = schedule_data.get('validation', None)
    config = schedule_data.get('config', schedule.get('config', {}))
    
    # Generate chart images if requested
    gantt_chart = ""
    utilization_chart = ""
    activity_distribution_chart = ""
    filler_stats = []
    
    if include_charts and activities:
        try:
            num_fillers = config.get('num_fillers', 4)
            makespan = results.get('makespan', 0)
            
            # Generate charts
            print("Generating Gantt chart...")
            gantt_chart = generate_gantt_chart_image(
                activities=activities,
                num_fillers=num_fillers,
                makespan=makespan,
            )
            
            print("Generating utilization chart...")
            utilization_chart = generate_utilization_chart_image(
                activities=activities,
                num_fillers=num_fillers,
                makespan=makespan,
            )
            
            print("Generating activity distribution chart...")
            activity_distribution_chart = generate_activity_distribution_chart(
                activities=activities,
            )
            
            print("Calculating filler statistics...")
            filler_stats = generate_filler_breakdown_data(
                activities=activities,
                num_fillers=num_fillers,
            )
            
        except Exception as e:
            print(f"Warning: Failed to generate some charts: {e}")
            # Continue without charts rather than failing completely
    
    # Prepare template context
    context = {
        'schedule': schedule,
        'results': results,
        'activities': activities,
        'config': config,
        'validation': validation,
        'user_name': user_name,
        'generated_at': datetime.now(),
        'description': schedule.get('description', ''),
        'gantt_chart': gantt_chart,
        'utilization_chart': utilization_chart,
        'activity_distribution_chart': activity_distribution_chart,
        'filler_stats': filler_stats,
    }
    
    # Load Jinja2 template
    template_path = get_template_path()
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('schedule_report.html')
    
    # Render HTML
    print("Rendering HTML template...")
    html_content = template.render(**context)
    
    # Generate PDF
    print("Generating PDF...")
    try:
        pdf_bytes = HTML(string=html_content, base_url=str(template_path)).write_pdf()
        
        # Save to file if path provided
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(pdf_bytes)
            print(f"PDF saved to: {output_path}")
        
        return pdf_bytes
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        raise Exception(f"Failed to generate PDF: {str(e)}")


def generate_comparison_pdf_report(
    comparison_data: Dict[str, Any],
    user_name: str = "System",
    output_path: Optional[str] = None,
) -> bytes:
    """
    Generate a PDF report comparing multiple schedules.
    
    Args:
        comparison_data: Dictionary containing comparison information:
            - comparison: Comparison model data
            - schedules: List of schedule data dictionaries
        user_name: Name of the user generating the report
        output_path: Optional path to save PDF file
    
    Returns:
        PDF content as bytes
    
    Note:
        This is a placeholder for future implementation.
        Currently raises NotImplementedError.
    """
    raise NotImplementedError("Comparison PDF reports are not yet implemented. Coming in Phase 3.")


def test_pdf_generation():
    """
    Test function to verify PDF generation works.
    Can be run standalone to check dependencies.
    """
    import random
    
    # Generate sample data
    activities = []
    for i in range(20):
        filler_id = random.randint(1, 3)
        start = random.uniform(0, 40)
        duration = random.uniform(2, 8)
        activities.append({
            'id': f'act_{i}',
            'lot_id': f'LOT_{i:03d}',
            'filler_id': filler_id,
            'start_time': start,
            'end_time': start + duration,
            'duration': duration,
            'kind': random.choice(['FILL', 'CLEAN', 'CHANGEOVER']),
            'lot_type': random.choice(['TypeA', 'TypeB']),
        })
    
    schedule_data = {
        'schedule': {
            'id': 1,
            'name': 'Test Schedule',
            'description': 'This is a test schedule for PDF generation',
            'status': 'completed',
            'strategy': 'MILP',
            'config': {
                'num_fillers': 3,
                'clean_time_same': 1.5,
                'clean_time_different': 3.0,
            },
        },
        'results': {
            'makespan': 48.5,
            'utilization': 0.85,
            'changeovers': 12,
            'lots_scheduled': 20,
        },
        'activities': activities,
        'config': {
            'num_fillers': 3,
            'clean_time_same': 1.5,
            'clean_time_different': 3.0,
        },
    }
    
    try:
        print("Testing PDF generation...")
        pdf_bytes = generate_pdf_report(
            schedule_data=schedule_data,
            user_name="Test User",
            include_charts=True,
            output_path="test_report.pdf",
        )
        print(f"✓ PDF generated successfully! Size: {len(pdf_bytes)} bytes")
        print("✓ Saved to: test_report.pdf")
        return True
    except Exception as e:
        print(f"✗ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Run test when module is executed directly
    test_pdf_generation()
