import argparse
import sys
import os
import pandas as pd
from atp.io import read_xml_all_metrics
from atp.plotting import plot_metrics

def main():
    parser = argparse.ArgumentParser(description="Plot metrics from one or more XML performance summary files.")
    parser.add_argument("xml_files", nargs="+", help="Path to one or more XML files")
    parser.add_argument("--x-axis", help="Metric name for the horizontal axis")
    parser.add_argument("--y-axis", help="Metric name for the vertical axis")
    parser.add_argument("--output-pdf", help="Output path for PDF plot")
    parser.add_argument("--output-html", help="Output path for HTML/SVG plot")
    parser.add_argument("--title", help="Plot title")
    parser.add_argument("--show", action="store_true", help="Show the plot in a window")
    parser.add_argument("--prefix", help="Generate 3 standard plots using the specified prefix for file names")
    parser.add_argument("--output-excel", action="store_true", help="Generate Excel spreadsheets when used with --prefix")
    parser.add_argument("--excel-file", help="Output path for a combined Excel spreadsheet when not using --prefix")
    parser.add_argument("--sort-x", action="store_true", help="Sort the x-axis values (disabled by default)")
    parser.add_argument("--pct-diff", action="store_true", help="Plot percentage difference from the first series")

    args = parser.parse_args()

    if args.prefix:
        # Standard plots as defined in the bash script
        plots = [
            ("op rate", "average latency", f"{args.prefix}_op_rate_vs_avg_latency"),
            ("op rate", "achieved rate", f"{args.prefix}_op_rate_vs_achieved_rate"),
            ("achieved rate", "average latency", f"{args.prefix}_achieved_rate_vs_avg_latency")
        ]
        
        for x_metric, y_metric, output_base in plots:
            print(f"Generating plot: {x_metric} vs {y_metric}")
            run_plot(
                xml_files=args.xml_files,
                x_axis=x_metric,
                y_axis=y_metric,
                output_pdf=f"{output_base}.pdf",
                output_html=f"{output_base}.html",
                title=args.title,
                show=args.show,
                sort_x=args.sort_x,
                pct_diff=args.pct_diff
            )
            
            # Generate a 4th plot for percentage difference if requested
            if args.pct_diff:
                print(f"Generating % difference plot: {x_metric} vs {y_metric}")
                run_plot(
                    xml_files=args.xml_files,
                    x_axis=x_metric,
                    y_axis=y_metric,
                    output_pdf=f"{output_base}_pct_diff.pdf",
                    output_html=f"{output_base}_pct_diff.html",
                    title=f"{args.title} (% Diff)" if args.title else None,
                    show=args.show,
                    sort_x=args.sort_x,
                    pct_diff=True
                )
            
            if args.output_excel:
                print(f"Exporting Excel: {x_metric} vs {y_metric}")
                run_excel_export(
                    xml_files=args.xml_files,
                    x_axis=x_metric,
                    y_axis=y_metric,
                    output_excel=f"{output_base}.xlsx",
                    sort_x=args.sort_x
                )
                
                if args.pct_diff:
                    print(f"Exporting % difference Excel: {x_metric} vs {y_metric}")
                    run_excel_export(
                        xml_files=args.xml_files,
                        x_axis=x_metric,
                        y_axis=y_metric,
                        output_excel=f"{output_base}_pct_diff.xlsx",
                        sort_x=args.sort_x,
                        pct_diff=True
                    )
    else:
        # Check for required metrics unless prefix is used
        if not args.x_axis or not args.y_axis:
            parser.error("the following arguments are required: --x-axis, --y-axis (unless --prefix is used)")

    # Run Excel export if requested
    if args.excel_file:
        run_excel_export(
            xml_files=args.xml_files,
            x_axis=args.x_axis,
            y_axis=args.y_axis,
            output_excel=args.excel_file,
            sort_x=args.sort_x,
            pct_diff=args.pct_diff
        )

    # Run Plot if PDF or HTML or show is requested
    if args.output_pdf or args.output_html or args.show:
        run_plot(
                xml_files=args.xml_files,
                x_axis=args.x_axis,
                y_axis=args.y_axis,
                output_pdf=args.output_pdf,
                output_html=args.output_html,
                title=args.title,
                show=args.show,
                sort_x=args.sort_x,
                pct_diff=args.pct_diff
            )

def run_plot(xml_files, x_axis, y_axis, output_pdf=None, output_html=None, title=None, show=False, sort_x=False, pct_diff=False):
    datasets = []
    for xml_file in xml_files:
        if not os.path.exists(xml_file):
            print(f"Error: File {xml_file} not found.")
            sys.exit(1)

        try:
            df = read_xml_all_metrics(xml_file)
        except Exception as e:
            print(f"Error reading XML file {xml_file}: {e}")
            sys.exit(1)

        if x_axis not in df.columns:
            print(f"Error: Metric '{x_axis}' not found in {xml_file}. Available metrics: {', '.join(df.columns)}")
            sys.exit(1)
        if y_axis not in df.columns:
            print(f"Error: Metric '{y_axis}' not found in {xml_file}. Available metrics: {', '.join(df.columns)}")
            sys.exit(1)

        # Convert to numeric, dropping rows with non-numeric data for selected columns if necessary
        def to_float(x):
            if isinstance(x, (int, float)):
                return float(x)
            if isinstance(x, str):
                try:
                    return float(x)
                except ValueError:
                    return None
            return None

        # Print debug info if types look strange
        # print(f"DEBUG: {xml_file} {x_axis} types: {df[x_axis].apply(type).unique()}")
        
        df[x_axis] = df[x_axis].apply(to_float)
        df[y_axis] = df[y_axis].apply(to_float)
        
        # Ensure x-axis is rounded to avoid precision issues during merge
        if pd.api.types.is_float_dtype(df[x_axis]):
            df[x_axis] = df[x_axis].round(6)
        
        df = df.dropna(subset=[x_axis, y_axis])
        
        if df.empty:
            print(f"Warning: No valid numeric data found for selected axes in {xml_file}. Skipping.")
            continue

        if sort_x:
            # Sort by x-axis for better plotting
            df = df.sort_values(by=x_axis)
        
        datasets.append({
            'x': df[x_axis].values,
            'y': df[y_axis].values,
            'label': os.path.basename(xml_file)
        })

    if not datasets:
        print("Error: No valid data to plot from any of the provided files.")
        return

    if pct_diff:
        if len(datasets) < 2:
            print("Warning: Percentage difference requires at least two datasets. Plotting normal values.")
        else:
            # Use pandas to align datasets by x-axis for computation
            baseline_label = datasets[0]['label']
            
            # Create a combined dataframe for all points
            dfs = []
            for d in datasets:
                dfs.append(pd.DataFrame({x_axis: d['x'], d['label']: d['y']}))
            
            # Merge all dataframes on x_axis
            merged_df = dfs[0]
            for next_df in dfs[1:]:
                # We use a custom suffix to handle cases where labels might overlap if not careful, 
                # but labels are unique (filenames).
                merged_df = pd.merge(merged_df, next_df, on=x_axis, how='outer')
            
            # Re-read filenames from datasets to ensure we use the same labels
            labels = [d['label'] for d in datasets]
            baseline_col = labels[0]
            # Use a copy of the baseline values to ensure it's not modified while computing other columns
            baseline_values = merged_df[baseline_col].copy()
            
            if sort_x:
                merged_df = merged_df.sort_values(by=x_axis)
                
            # Compute percentage difference relative to the first column
            pct_datasets = []
            
            for label in labels:
                # Formula: (value / baseline) * 100
                diff_vals = (merged_df[label] / baseline_values) * 100
                
                # Handle cases where baseline is zero (if any)
                diff_vals = diff_vals.replace([float('inf'), float('-inf')], float('nan'))
                
                # We need to extract back to datasets format
                valid_mask = ~diff_vals.isna() & ~merged_df[x_axis].isna()
                pct_datasets.append({
                    'x': merged_df.loc[valid_mask, x_axis].values,
                    'y': diff_vals[valid_mask].values,
                    'label': label
                })
            
            datasets = pct_datasets
            if not title:
                title = f"% of Baseline of {y_axis} vs {x_axis} (Baseline: {baseline_label})"
            y_axis = f"% of Baseline ({y_axis})"

    plot_metrics(
        datasets=datasets,
        x_label=x_axis,
        y_label=y_axis,
        title=title,
        save_pdf=output_pdf,
        save_html=output_html,
        show=show
    )
    
    if output_pdf:
        print(f"PDF plot saved to {output_pdf}")
    if output_html:
        print(f"HTML plot saved to {output_html}")

def run_excel_export(xml_files, x_axis, y_axis, output_excel, sort_x=False, pct_diff=False):
    combined_df = None
    
    def to_float(x):
        if isinstance(x, (int, float)):
            return float(x)
        if isinstance(x, str):
            try:
                return float(x)
            except ValueError:
                return None
        return None

    for xml_file in xml_files:
        if not os.path.exists(xml_file):
            print(f"Error: File {xml_file} not found.")
            sys.exit(1)

        try:
            df = read_xml_all_metrics(xml_file)
        except Exception as e:
            print(f"Error reading XML file {xml_file}: {e}")
            sys.exit(1)

        if x_axis not in df.columns:
            print(f"Error: Metric '{x_axis}' not found in {xml_file}. Available metrics: {', '.join(df.columns)}")
            sys.exit(1)
        if y_axis not in df.columns:
            print(f"Error: Metric '{y_axis}' not found in {xml_file}. Available metrics: {', '.join(df.columns)}")
            sys.exit(1)

        # Filter and convert to numeric
        df = df[[x_axis, y_axis]].copy()
        df[x_axis] = df[x_axis].apply(to_float)
        df[y_axis] = df[y_axis].apply(to_float)
        
        df = df.dropna(subset=[x_axis, y_axis])
        
        if df.empty:
            print(f"Warning: No valid numeric data found for selected axes in {xml_file}. Skipping.")
            continue

        # Rename y_axis column to filename for identification
        label = os.path.basename(xml_file)
        
        # We need to keep x_axis for merging, but we want the y_axis to be named after the file.
        # If x_axis and y_axis are same, we create a copy for the y values.
        temp_df = pd.DataFrame()
        temp_df[x_axis] = df[x_axis]
        temp_df[label] = df[y_axis]
        
        if combined_df is None:
            combined_df = temp_df
        else:
            # Outer merge to include all x-axis values from all files
            combined_df = pd.merge(combined_df, temp_df, on=x_axis, how='outer')

    if combined_df is None or combined_df.empty:
        print("Error: No valid data to export from any of the provided files.")
        return

    if sort_x:
        # Sort by x-axis for better readability
        combined_df = combined_df.sort_values(by=x_axis)
    
    if pct_diff:
        # Use the first filename as baseline
        baseline_col = os.path.basename(xml_files[0])
        if baseline_col in combined_df.columns:
            # Create a copy of the baseline to avoid issues when baseline itself is modified
            baseline_values = combined_df[baseline_col].copy()
            # We want to skip x_axis column
            cols_to_convert = [c for c in combined_df.columns if c != x_axis]
            for col in cols_to_convert:
                # Calculate % of Baseline: (value / baseline) * 100
                # Using .loc to avoid SettingWithCopyWarning (though not strictly needed here as we are modifying a newly merged df)
                combined_df[col] = (combined_df[col] / baseline_values) * 100
                # Handle baseline being zero
                combined_df[col] = combined_df[col].replace([float('inf'), float('-inf')], float('nan'))

    try:
        sheet_name = os.path.splitext(os.path.basename(output_excel))[0]
        # Excel sheet names have a maximum length of 31 characters
        sheet_name = sheet_name[:31]
        combined_df.to_excel(output_excel, index=False, sheet_name=sheet_name)
        print(f"Combined Excel spreadsheet saved to {output_excel}")
    except ImportError:
        print("Error: 'openpyxl' is required for Excel output. Please install it with: pip install openpyxl")
        sys.exit(1)
    except Exception as e:
        print(f"Error saving Excel file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
