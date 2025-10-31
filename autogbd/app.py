"""
Streamlit web interface for AutoGBD configuration.

This provides a user-friendly GUI for creating and editing config.yaml files.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to allow importing autogbd
# This allows running: streamlit run autogbd/app.py from project root
# or: streamlit run app.py from autogbd/ directory

# Get the absolute path to this file
if '__file__' in globals():
    app_file = Path(__file__).resolve()
else:
    # Fallback if __file__ is not available
    import inspect
    try:
        app_file = Path(inspect.getfile(inspect.currentframe())).resolve()
    except:
        # Last resort: use current working directory
        app_file = Path(os.getcwd()) / "app.py"

# Get project root (parent of autogbd directory)
app_dir = app_file.parent
# If we're in autogbd/ directory, go up one level to get project root
# If we're running from project root with autogbd/app.py, go up from app.py to autogbd to project root
if app_dir.name == "autogbd":
    project_root = app_dir.parent
else:
    # If app.py is directly in autogbd/, its parent is autogbd/, parent of that is project root
    project_root = app_dir.parent

# Add project root to path if not already there
project_root_str = str(project_root.absolute())
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import streamlit as st
import yaml
from typing import Dict, Any



def initialize_session_state():
    """Initialize session state variables."""
    if "config_data" not in st.session_state:
        st.session_state.config_data = get_default_config()
    if "config_valid" not in st.session_state:
        st.session_state.config_valid = False
    if "validation_message" not in st.session_state:
        st.session_state.validation_message = ""


def get_default_config() -> Dict[str, Any]:
    """Get default configuration dictionary."""
    return {
        "io": {
            "input_file": "",
            "output_file": "output/harmonized_data.csv",
            "input_format": "csv",
            "output_format": "csv",
        },
        "cleaning": {
            "enabled": True,
            "rules": [],
        },
        "mapping": {
            "enabled": True,
            "source_column": "icd10_code",
            "target_column": "gbd_cause",
            "sources": [],
        },
        "quality": {
            "enabled": True,
            "checks": [],
        },
        "reporting": {
            "enabled": True,
            "output_file": "harmonization_report.md",
            "format": "markdown",
        },
    }


def render_io_config(config: Dict[str, Any]):
    """Render I/O configuration section."""
    st.subheader("📁 Input/Output Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        config["io"]["input_file"] = st.text_input(
            "Input File Path",
            value=config["io"]["input_file"],
            help="Path to your input data file",
        )
        
        config["io"]["input_format"] = st.selectbox(
            "Input Format",
            ["csv", "excel", "xlsx", "parquet"],
            index=["csv", "excel", "xlsx", "parquet"].index(
                config["io"].get("input_format", "csv")
            ),
        )
    
    with col2:
        config["io"]["output_file"] = st.text_input(
            "Output File Path",
            value=config["io"]["output_file"],
            help="Path where harmonized data will be saved",
        )
        
        config["io"]["output_format"] = st.selectbox(
            "Output Format",
            ["csv", "excel", "xlsx", "parquet"],
            index=["csv", "excel", "xlsx", "parquet"].index(
                config["io"].get("output_format", "csv")
            ),
        )
    
    if config["io"]["input_format"] in ["excel", "xlsx"]:
        config["io"]["sheet_name"] = st.text_input(
            "Sheet Name (Optional)",
            value=config["io"].get("sheet_name", ""),
            help="Leave empty to use first sheet",
        )


def render_cleaning_config(config: Dict[str, Any]):
    """Render cleaning configuration section."""
    st.subheader("🧹 Data Cleaning")
    
    config["cleaning"]["enabled"] = st.checkbox(
        "Enable Data Cleaning",
        value=config["cleaning"]["enabled"],
    )
    
    if config["cleaning"]["enabled"]:
        st.write("**Cleaning Rules**")
        
        # Available cleaning rules
        available_rules = [
            "normalize_column_names",
            "remove_duplicates",
            "normalize_sex",
            "standardize_ages",
            "handle_missing_values",
            "normalize_text",
            "remove_outliers",
            "standardize_dates",
        ]
        
        # Initialize rules list if needed
        if "rules" not in config["cleaning"]:
            config["cleaning"]["rules"] = []
        
        # Build rule keys map
        rule_keys = {rule["name"]: i for i, rule in enumerate(config["cleaning"]["rules"])}
        new_rules = []
        
        for rule_name in available_rules:
            is_enabled = rule_name in rule_keys
            
            col1, col2 = st.columns([1, 4])
            with col1:
                enabled = st.checkbox(
                    rule_name.replace("_", " ").title(),
                    value=is_enabled,
                    key=f"cleaning_rule_{rule_name}",
                )
            
            if enabled:
                # Get or create rule
                if rule_name in rule_keys:
                    rule = config["cleaning"]["rules"][rule_keys[rule_name]]
                else:
                    rule = {
                        "name": rule_name,
                        "enabled": True,
                        "parameters": {},
                    }
                
                with col2:
                    # Show rule-specific parameters
                    if rule_name == "normalize_sex":
                        rule["parameters"]["column"] = st.text_input(
                            "Sex Column Name",
                            value=rule["parameters"].get("column", "sex"),
                            key=f"sex_col_{rule_name}",
                        )
                    elif rule_name == "standardize_ages":
                        col_age1, col_age2 = st.columns(2)
                        with col_age1:
                            rule["parameters"]["column"] = st.text_input(
                                "Age Column Name",
                                value=rule["parameters"].get("column", "age"),
                                key=f"age_col_{rule_name}",
                            )
                            rule["parameters"]["min_age"] = st.number_input(
                                "Min Age",
                                value=int(rule["parameters"].get("min_age", 0)),
                                key=f"min_age_{rule_name}",
                            )
                        with col_age2:
                            rule["parameters"]["max_age"] = st.number_input(
                                "Max Age",
                                value=int(rule["parameters"].get("max_age", 150)),
                                key=f"max_age_{rule_name}",
                            )
                    elif rule_name == "handle_missing_values":
                        strategy = st.selectbox(
                            "Strategy",
                            ["keep", "drop", "fill"],
                            index=["keep", "drop", "fill"].index(
                                rule["parameters"].get("strategy", "keep")
                            ),
                            key=f"missing_strategy_{rule_name}",
                        )
                        rule["parameters"]["strategy"] = strategy
                    elif rule_name == "normalize_text":
                        columns_input = st.text_input(
                            "Columns (comma-separated)",
                            value=", ".join(rule["parameters"].get("columns", [])),
                            key=f"text_cols_{rule_name}",
                            help="Enter column names separated by commas",
                        )
                        if columns_input:
                            rule["parameters"]["columns"] = [
                                c.strip() for c in columns_input.split(",") if c.strip()
                            ]
                
                new_rules.append(rule)
        
        # Update rules list
        config["cleaning"]["rules"] = new_rules


def render_mapping_config(config: Dict[str, Any]):
    """Render mapping configuration section."""
    st.subheader("🔗 Cause Mapping")
    
    config["mapping"]["enabled"] = st.checkbox(
        "Enable Cause Mapping",
        value=config["mapping"]["enabled"],
    )
    
    if config["mapping"]["enabled"]:
        col1, col2 = st.columns(2)
        
        with col1:
            config["mapping"]["source_column"] = st.text_input(
                "Source Code Column",
                value=config["mapping"]["source_column"],
                help="Column containing source codes (e.g., ICD-10)",
            )
        
        with col2:
            config["mapping"]["target_column"] = st.text_input(
                "Target Column",
                value=config["mapping"]["target_column"],
                help="Column for mapped GBD causes",
            )
        
        st.write("**Mapping Sources** (processed in order)")
        
        # Initialize sources list if needed
        if "sources" not in config["mapping"]:
            config["mapping"]["sources"] = []
        
        # Show existing sources
        for idx, source in enumerate(config["mapping"]["sources"]):
            with st.expander(f"Mapping Source {idx + 1}: {source.get('type', 'unknown').title()}"):
                source_type = st.selectbox(
                    "Type",
                    ["direct", "fuzzy", "ai"],
                    index=["direct", "fuzzy", "ai"].index(source.get("type", "direct")),
                    key=f"source_type_{idx}",
                )
                source["type"] = source_type
                source["enabled"] = st.checkbox(
                    "Enabled",
                    value=source.get("enabled", True),
                    key=f"source_enabled_{idx}",
                )
                
                if source_type == "direct":
                    source["file"] = st.text_input(
                        "Mapping File Path",
                        value=source.get("file", ""),
                        key=f"direct_file_{idx}",
                    )
                    source["version"] = st.text_input(
                        "Version",
                        value=source.get("version", ""),
                        key=f"direct_version_{idx}",
                    )
                elif source_type == "fuzzy":
                    source["file"] = st.text_input(
                        "Cause List File Path",
                        value=source.get("file", ""),
                        key=f"fuzzy_file_{idx}",
                    )
                    source["threshold"] = st.slider(
                        "Similarity Threshold",
                        min_value=0.0,
                        max_value=1.0,
                        value=source.get("threshold", 0.85),
                        step=0.05,
                        key=f"fuzzy_threshold_{idx}",
                    )
                elif source_type == "ai":
                    source["threshold"] = st.slider(
                        "Confidence Threshold",
                        min_value=0.0,
                        max_value=1.0,
                        value=source.get("threshold", 0.85),
                        step=0.05,
                        key=f"ai_threshold_{idx}",
                    )
                
                if st.button("Remove", key=f"remove_source_{idx}"):
                    config["mapping"]["sources"].pop(idx)
                    st.rerun()
        
        if st.button("➕ Add Mapping Source"):
            config["mapping"]["sources"].append({
                "type": "direct",
                "enabled": True,
                "file": "",
            })


def render_quality_config(config: Dict[str, Any]):
    """Render quality configuration section."""
    st.subheader("✅ Data Quality Checks")
    
    config["quality"]["enabled"] = st.checkbox(
        "Enable Quality Checks",
        value=config["quality"]["enabled"],
    )
    
    if config["quality"]["enabled"]:
        # Available quality checks
        available_checks = [
            "check_age_range",
            "check_sex_values",
            "check_missing_values",
            "check_unmapped_codes",
            "check_death_count_validity",
            "check_value_ranges",
            "check_duplicates",
            "check_date_validity",
            "check_completeness",
        ]
        
        # Initialize checks list if needed
        if "checks" not in config["quality"]:
            config["quality"]["checks"] = []
        
        check_keys = {check["name"]: i for i, check in enumerate(config["quality"]["checks"])}
        new_checks = []
        
        for check_name in available_checks:
            is_enabled = check_name in check_keys
            
            enabled = st.checkbox(
                check_name.replace("_", " ").title(),
                value=is_enabled,
                key=f"quality_check_{check_name}",
            )
            
            if enabled:
                # Get or create check
                if check_name in check_keys:
                    check = config["quality"]["checks"][check_keys[check_name]]
                else:
                    check = {
                        "name": check_name,
                        "enabled": True,
                        "parameters": {},
                    }
                
                # Add check-specific parameters
                if check_name == "check_age_range":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        check["parameters"]["column"] = st.text_input(
                            "Age Column",
                            value=check["parameters"].get("column", "age"),
                            key=f"age_col_check_{check_name}",
                        )
                    with col2:
                        check["parameters"]["min_age"] = st.number_input(
                            "Min Age",
                            value=int(check["parameters"].get("min_age", 0)),
                            key=f"min_age_check_{check_name}",
                        )
                    with col3:
                        check["parameters"]["max_age"] = st.number_input(
                            "Max Age",
                            value=int(check["parameters"].get("max_age", 150)),
                            key=f"max_age_check_{check_name}",
                        )
                elif check_name == "check_sex_values":
                    col1, col2 = st.columns(2)
                    with col1:
                        check["parameters"]["column"] = st.text_input(
                            "Sex Column",
                            value=check["parameters"].get("column", "sex"),
                            key=f"sex_col_check_{check_name}",
                        )
                    with col2:
                        valid_values_input = st.text_input(
                            "Valid Values (comma-separated)",
                            value=", ".join(check["parameters"].get("valid_values", ["male", "female", "unknown"])),
                            key=f"sex_values_check_{check_name}",
                        )
                        check["parameters"]["valid_values"] = [
                            v.strip() for v in valid_values_input.split(",") if v.strip()
                        ]
                elif check_name == "check_unmapped_codes":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        check["parameters"]["source_column"] = st.text_input(
                            "Source Column",
                            value=check["parameters"].get("source_column", "icd10_code"),
                            key=f"unmapped_source_{check_name}",
                        )
                    with col2:
                        check["parameters"]["target_column"] = st.text_input(
                            "Target Column",
                            value=check["parameters"].get("target_column", "gbd_cause"),
                            key=f"unmapped_target_{check_name}",
                        )
                    with col3:
                        check["parameters"]["threshold"] = st.number_input(
                            "Threshold (0-1)",
                            value=float(check["parameters"].get("threshold", 0.05)),
                            min_value=0.0,
                            max_value=1.0,
                            step=0.01,
                            key=f"unmapped_threshold_{check_name}",
                        )
                
                new_checks.append(check)
        
        # Update checks list
        config["quality"]["checks"] = new_checks


def render_reporting_config(config: Dict[str, Any]):
    """Render reporting configuration section."""
    st.subheader("📊 Reporting")
    
    config["reporting"]["enabled"] = st.checkbox(
        "Enable Report Generation",
        value=config["reporting"]["enabled"],
    )
    
    if config["reporting"]["enabled"]:
        config["reporting"]["output_file"] = st.text_input(
            "Report File Path",
            value=config["reporting"]["output_file"],
        )
        
        config["reporting"]["format"] = st.selectbox(
            "Report Format",
            ["markdown", "html"],
            index=["markdown", "html"].index(
                config["reporting"].get("format", "markdown")
            ),
        )


def validate_config(config_data: Dict[str, Any]) -> tuple[bool, str]:
    """Validate configuration."""
    try:
        # Try to create AutoGBDConfig from the data
        config = AutoGBDConfig(**config_data)
        return True, "✅ Configuration is valid!"
    except Exception as e:
        return False, f"❌ Configuration error: {str(e)}"


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AutoGBD Config Builder",
        page_icon="⚙️",
        layout="wide",
    )
    
    initialize_session_state()
    
    st.title("⚙️ AutoGBD Configuration Builder")
    st.markdown("Create and edit your `config.yaml` file with ease!")
    
    # Sidebar for file operations
    with st.sidebar:
        st.header("📂 File Operations")
        
        # Upload existing config
        uploaded_file = st.file_uploader(
            "Upload Existing Config",
            type=["yaml", "yml"],
            help="Upload an existing config.yaml file",
        )
        
        if uploaded_file is not None:
            try:
                config_data = yaml.safe_load(uploaded_file)
                st.session_state.config_data = config_data
                st.success("Config loaded!")
                st.rerun()
            except Exception as e:
                st.error(f"Error loading config: {e}")
        
        st.divider()
        
        # Reset to defaults
        if st.button("🔄 Reset to Defaults"):
            st.session_state.config_data = get_default_config()
            st.rerun()
        
        st.divider()
        
        # Validation
        st.header("✓ Validation")
        if st.button("Validate Configuration"):
            valid, message = validate_config(st.session_state.config_data)
            st.session_state.config_valid = valid
            st.session_state.validation_message = message
            if valid:
                st.success(message)
            else:
                st.error(message)
    
    # Main configuration editor
    tabs = st.tabs(["📝 Editor", "👀 Preview", "ℹ️ About"])
    
    with tabs[0]:
        # Render each configuration section
        render_io_config(st.session_state.config_data)
        st.divider()
        
        render_cleaning_config(st.session_state.config_data)
        st.divider()
        
        render_mapping_config(st.session_state.config_data)
        st.divider()
        
        render_quality_config(st.session_state.config_data)
        st.divider()
        
        render_reporting_config(st.session_state.config_data)
    
    with tabs[1]:
        st.subheader("YAML Preview")
        
        # Generate YAML from current config
        yaml_output = yaml.dump(
            st.session_state.config_data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        
        st.code(yaml_output, language="yaml")
        
        # Download button
        st.download_button(
            label="📥 Download config.yaml",
            data=yaml_output,
            file_name="config.yaml",
            mime="text/yaml",
        )
        
        # Copy to clipboard button (using st.code with copy button)
        st.info("💡 Click the copy icon above the code block to copy YAML to clipboard")
    
    with tabs[2]:
        st.subheader("About AutoGBD Config Builder")
        st.markdown("""
        This tool helps you create configuration files for the AutoGBD harmonization framework.
        
        **Features:**
        - ✨ Visual form-based editor
        - 🔍 Live YAML preview
        - ✓ Configuration validation
        - 📥 Download your config file
        - 📤 Upload existing configs to edit
        
        **Quick Start:**
        1. Fill in the configuration sections
        2. Check the Preview tab to see the YAML
        3. Validate your configuration
        4. Download the config.yaml file
        5. Use it with: `autogbd run --config config.yaml`
        
        **Need Help?**
        - See the [README](https://github.com/m-aljasem/autogbd) for detailed documentation
        - Check `examples/config.example.yaml` for a complete example
        """)
        
        st.subheader("Configuration Sections")
        st.markdown("""
        - **Input/Output**: Define your data files and formats
        - **Data Cleaning**: Select and configure cleaning rules
        - **Cause Mapping**: Set up code mapping sources (direct, fuzzy, AI)
        - **Quality Checks**: Enable data quality validation
        - **Reporting**: Configure report generation
        """)


if __name__ == "__main__":
    main()

