"""
Command Line Interface for WebIntel
"""

import asyncio
import click
import json
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown
from rich.text import Text

from .config import get_default_config, Config
from .processor import DataProcessor
# Removed utils import - not needed

console = Console()

@click.group()
@click.version_option(version="1.0.0")
@click.option('--config', '-c', type=click.Path(), help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, config: Optional[str], verbose: bool):
    """
    WebIntel - High-Performance Web Information Retrieval CLI Tool
    
    Powered by Google Gemini 2.0 Flash AI for intelligent web scraping
    and comprehensive information synthesis.
    """
    # Setup logging - completely silent unless verbose
    if verbose:
        setup_logging("DEBUG")
    else:
        # Completely disable all logging
        import logging
        logging.disable(logging.CRITICAL)
    
    # Load configuration
    if config:
        config_obj = Config.load_from_file(config)
    else:
        config_obj = get_default_config()
    
    # Store in context
    ctx.ensure_object(dict)
    ctx.obj['config'] = config_obj
    ctx.obj['verbose'] = verbose

@cli.command()
@click.argument('query', required=True)
@click.option('--max-results', '-n', default=20, type=int, 
              help='Maximum number of results to process (default: 20)')
@click.option('--format', '-f', type=click.Choice(['rich', 'json', 'markdown', 'plain']),
              help='Output format (overrides config)')
@click.option('--save', '-s', is_flag=True, help='Save results to file')
@click.option('--output-dir', '-o', type=click.Path(), 
              help='Output directory for saved results')
@click.pass_context
def search(ctx, query: str, max_results: int, format: Optional[str],
           save: bool, output_dir: Optional[str]):
    """
    Search for comprehensive information about a topic.
    
    QUERY: The search query or topic to research
    
    Examples:
    \b
        webintel search "artificial intelligence trends 2024"
        webintel search "climate change solutions" --max-results 30
        webintel search "python web scraping" --format json --save
    """
    config = ctx.obj['config']
    
    # Override config with command line options
    if format:
        config.output.format = format
    if save:
        config.output.save_to_file = True
    if output_dir:
        config.output.output_directory = output_dir
    
    # Validate API key
    if not config.gemini.api_key:
        console.print(Panel(
            "[red]Error: Gemini API key is required![/red]\n\n"
            "Please set your API key using one of these methods:\n"
            "1. Set environment variable: GEMINI_API_KEY=your_key_here\n"
            "2. Add to config file: ~/.webintel/config.yaml\n"
            "3. Use: webintel config set-api-key YOUR_KEY",
            title="Configuration Error",
            border_style="red"
        ))
        sys.exit(1)
    
    # Minimal search info
    console.print(f"🔍 Searching: {query}")
    
    # Initialize processor
    processor = DataProcessor(config)
    
    # Execute search with progress indicator
    async def run_search():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:

            task = progress.add_task("Processing...", total=None)

            try:
                results = await processor.process_query(query, max_results)
                progress.update(task, completed=True)
                return results

            except KeyboardInterrupt:
                console.print("\n[yellow]Search interrupted by user[/yellow]")
                sys.exit(1)
            except Exception as e:
                console.print(f"\n[red]Search failed: {str(e)}[/red]")
                sys.exit(1)

    # Run the async search
    try:
        results = asyncio.run(run_search())
    except KeyboardInterrupt:
        console.print("\n[yellow]Search interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Search failed: {str(e)}[/red]")
        sys.exit(1)

    # Display results
    display_results(results, config.output.format)

def display_results(results: dict, output_format: str):
    """Display search results in specified format"""
    
    if results.get('status') == 'error':
        console.print(Panel(
            f"[red]Error:[/red] {results.get('message', 'Unknown error')}",
            title="Search Error",
            border_style="red"
        ))
        return
    
    if output_format == 'json':
        console.print_json(data=results)
        return
    
    if output_format == 'plain':
        _display_plain_results(results)
        return
    
    if output_format == 'markdown':
        _display_markdown_results(results)
        return
    
    # Default: rich format
    _display_rich_results(results)

def _display_rich_results(results: dict):
    """Display Tavily-like results with comprehensive information"""
    analysis = results.get('analysis', {})
    statistics = results.get('statistics', {})
    sources = results.get('sources', [])
    performance = results.get('performance', {})
    source_urls = results.get('source_urls', [])

    # Minimal results header
    processing_time = results.get('response_time', 0)
    answer = results.get('answer', '')

    total_sources = len(sources) if sources else statistics.get('total_sources', 0)
    console.print(f"✅ Found {total_sources} sources in {processing_time:.1f}s")

    # Comprehensive AI Response
    comprehensive_answer = analysis.get('comprehensive_answer', '')
    if comprehensive_answer and len(comprehensive_answer) > 20:
        console.print(Panel(
            comprehensive_answer,
            title="🤖 AI Assistant Response",
            border_style="cyan"
        ))
    elif answer and len(answer) > 20:
        console.print(f"\n💡 {answer}")
    
    # Skip executive summary for speed
    
    # Key Insights and Findings
    if analysis.get('key_findings'):
        console.print(f"\n🔍 Key Insights:")
        for i, finding in enumerate(analysis['key_findings'][:4], 1):  # Show more insights
            console.print(f"  {i}. {finding}")

    # Additional Information
    if analysis.get('detailed_analysis') and len(analysis['detailed_analysis']) > 20:
        console.print(Panel(
            analysis['detailed_analysis'],
            title="📊 Additional Information",
            border_style="yellow"
        ))
    
    # Skip detailed analysis for speed
    
    # Source Summary
    source_summary = analysis.get('source_summary', '')
    if source_summary:
        console.print(f"\n📚 Source Analysis: {source_summary}")

    # Detailed Sources List
    if sources:
        console.print(f"\n📋 Sources ({len(sources)} found):")
        for i, source in enumerate(sources[:5], 1):  # Show more sources
            title = source.get('title', 'No title')[:60]
            url = source.get('url', 'No URL')
            relevance = source.get('relevance_score', source.get('score', 0))
            console.print(f"  {i}. {title}")
            console.print(f"     🔗 {url}")
            console.print(f"     📊 Relevance: {relevance:.2f}")
            console.print()

def _display_markdown_results(results: dict):
    """Display results in markdown format"""
    synthesis = results.get('synthesis', {})
    sources = results.get('sources', [])
    
    markdown_content = f"""
# WebIntel Search Results

**Query:** {results.get('query', '')}
**Processing Time:** {results.get('processing_time', 0)}s
**Sources Analyzed:** {results.get('statistics', {}).get('sources_analyzed', 0)}

## Executive Summary

{synthesis.get('executive_summary', 'No summary available')}

## Key Findings

"""
    
    for i, finding in enumerate(synthesis.get('key_findings', []), 1):
        markdown_content += f"{i}. {finding}\n"
    
    markdown_content += "\n## Recommendations\n\n"
    
    for rec in synthesis.get('recommendations', []):
        markdown_content += f"- {rec}\n"
    
    markdown_content += f"\n## Detailed Analysis\n\n{synthesis.get('detailed_analysis', '')}\n"
    
    markdown_content += "\n## Sources\n\n"
    
    for i, source in enumerate(sources[:10], 1):
        markdown_content += f"{i}. **{source.get('title', 'No title')}** ({source.get('domain', 'Unknown')})\n"
        markdown_content += f"   - Relevance: {source.get('relevance_score', 0):.2f}\n"
        for point in source.get('key_points', [])[:2]:
            markdown_content += f"   - {point}\n"
        markdown_content += "\n"
    
    console.print(Markdown(markdown_content))

def _display_plain_results(results: dict):
    """Display results in plain text format"""
    synthesis = results.get('synthesis', {})
    sources = results.get('sources', [])
    
    print(f"WEBINTEL SEARCH RESULTS")
    print("=" * 50)
    print(f"Query: {results.get('query', '')}")
    print(f"Processing Time: {results.get('processing_time', 0)}s")
    print(f"Sources Analyzed: {results.get('statistics', {}).get('sources_analyzed', 0)}")
    print()
    
    print("EXECUTIVE SUMMARY:")
    print(synthesis.get('executive_summary', 'No summary available'))
    print()
    
    if synthesis.get('key_findings'):
        print("KEY FINDINGS:")
        for i, finding in enumerate(synthesis['key_findings'], 1):
            print(f"{i}. {finding}")
        print()
    
    if synthesis.get('recommendations'):
        print("RECOMMENDATIONS:")
        for rec in synthesis['recommendations']:
            print(f"- {rec}")
        print()
    
    print("DETAILED ANALYSIS:")
    print(synthesis.get('detailed_analysis', ''))
    print()
    
    if sources:
        print("SOURCES:")
        for i, source in enumerate(sources[:10], 1):
            print(f"{i}. {source.get('title', 'No title')} ({source.get('domain', 'Unknown')})")
            print(f"   Relevance: {source.get('relevance_score', 0):.2f}")

@cli.group()
def config():
    """Configuration management commands"""
    pass

@config.command()
@click.argument('api_key')
@click.pass_context
def set_api_key(ctx, api_key: str):
    """Set Gemini API key"""
    config_obj = ctx.obj['config']
    config_obj.gemini.api_key = api_key
    config_obj.save_to_file()
    
    console.print(Panel(
        "[green]API key has been saved successfully![/green]",
        title="Configuration Updated",
        border_style="green"
    ))

@config.command()
@click.pass_context
def show(ctx):
    """Show current configuration"""
    config_obj = ctx.obj['config']
    
    # Hide API key for security
    config_dict = config_obj.model_dump()
    if config_dict['gemini']['api_key']:
        config_dict['gemini']['api_key'] = '*' * 20
    
    console.print_json(data=config_dict)

def main():
    """Main entry point"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)

if __name__ == '__main__':
    main()
