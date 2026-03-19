import argparse
import sys
import os
from .io import read_xml_all_metrics
from .plotting import plot_metrics

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
                show=args.show
            )
    else:
        if not args.x_axis or not args.y_axis:
            parser.error("the following arguments are required: --x-axis, --y-axis (unless --prefix is used)")
        
        run_plot(
            xml_files=args.xml_files,
            x_axis=args.x_axis,
            y_axis=args.y_axis,
            output_pdf=args.output_pdf,
            output_html=args.output_html,
            title=args.title,
            show=args.show
        )

def run_plot(xml_files, x_axis, y_axis, output_pdf=None, output_html=None, title=None, show=False):
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

        df[x_axis] = df[x_axis].apply(to_float)
        df[y_axis] = df[y_axis].apply(to_float)
        
        df = df.dropna(subset=[x_axis, y_axis])
        
        if df.empty:
            print(f"Warning: No valid numeric data found for selected axes in {xml_file}. Skipping.")
            continue

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

if __name__ == "__main__":
    main()
