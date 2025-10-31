"""
Command-line interface for AutoGBD.

Provides a user-friendly CLI for running harmonization pipelines.
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from autogbd.core.pipeline import AutoGBDPipeline
from autogbd.core.config_loader import ConfigLoader
from autogbd.core.provenance import ProvenanceTracker

app = typer.Typer(
    name="autogbd",
    help="AutoGBD: Intelligent health data harmonization framework",
    add_completion=False,
)
console = Console()


@app.command()
def run(
    config: str = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to the configuration YAML file",
    ),
    output_dir: Optional[str] = typer.Option(
        None,
        "--output-dir",
        "-o",
        help="Output directory (overrides config if specified)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
):
    """
    Run the AutoGBD harmonization pipeline.

    This command loads the configuration file and executes the complete
    harmonization process, including data loading, cleaning, mapping,
    quality checks, and report generation.
    """
    config_path = Path(config)

    if not config_path.exists():
        console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
        raise typer.Exit(1)

    try:
        # Load configuration
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading configuration...", total=None)
            config_obj = ConfigLoader.load(config_path)
            progress.update(task, completed=True)

        if verbose:
            console.print(f"[green]✓[/green] Configuration loaded from {config_path}")

        # Initialize pipeline
        provenance = ProvenanceTracker()
        pipeline = AutoGBDPipeline(config_obj, provenance)

        if verbose:
            console.print("[green]✓[/green] Pipeline initialized")

        # Run pipeline
        console.print("\n[bold]Running harmonization pipeline...[/bold]\n")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Processing data...", total=None)
            result = pipeline.run()
            progress.update(task, completed=True)

        # Print summary
        summary = provenance.get_summary()

        console.print("\n[bold green]Harmonization Complete![/bold green]\n")
        console.print(f"Total rows processed: {len(result):,}")
        console.print(f"Total transformations: {summary['total_entries']}")
        console.print(f"\nOutput file: {config_obj.io.output_file}")
        console.print(f"Report file: {config_obj.reporting.output_file}")
        console.print(f"Provenance log: provenance.json")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        if verbose:
            import traceback

            console.print("\n[red]Traceback:[/red]")
            console.print(traceback.format_exc())
        raise typer.Exit(1)


@app.command()
def validate(
    config: str = typer.Option(
        ...,
        "--config",
        "-c",
        help="Path to the configuration YAML file",
    ),
):
    """
    Validate a configuration file without running the pipeline.

    This command checks if the configuration file is valid and
    displays any errors or warnings.
    """
    config_path = Path(config)

    if not config_path.exists():
        console.print(f"[red]Error: Configuration file not found: {config_path}[/red]")
        raise typer.Exit(1)

    try:
        config_obj = ConfigLoader.load(config_path)
        console.print("[green]✓[/green] Configuration file is valid!")
        console.print(f"\nConfiguration summary:")
        console.print(f"  Input file: {config_obj.io.input_file}")
        console.print(f"  Output file: {config_obj.io.output_file}")
        console.print(f"  Cleaning enabled: {config_obj.cleaning.enabled}")
        console.print(f"  Mapping enabled: {config_obj.mapping.enabled}")
        console.print(f"  Quality checks enabled: {config_obj.quality.enabled}")
        console.print(f"  Reporting enabled: {config_obj.reporting.enabled}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """Display the AutoGBD version."""
    from autogbd import __version__

    console.print(f"AutoGBD version {__version__}")


@app.command()
def config_builder(
    port: int = typer.Option(
        8501,
        "--port",
        "-p",
        help="Port to run the Streamlit app on",
    ),
):
    """
    Launch the visual configuration builder.

    Opens a web interface in your browser for creating and editing
    config.yaml files without manually writing YAML.
    """
    try:
        import streamlit
    except ImportError:
        console.print(
            "[red]Error: Streamlit is not installed.[/red]\n"
            "Install it with: pip install streamlit\n"
            "Or install the app extras: pip install -e '.[app]'"
        )
        raise typer.Exit(1)

    import subprocess
    import sys

    app_path = Path(__file__).parent / "app.py"

    console.print(f"[green]Launching config builder on port {port}...[/green]")
    console.print("[yellow]Press Ctrl+C to stop the server[/yellow]\n")

    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(app_path),
                "--server.port",
                str(port),
            ],
            check=True,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Config builder stopped.[/yellow]")
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error launching app: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

