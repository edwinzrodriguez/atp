import argparse
import sys
import os
from .io import read_xml_all_metrics
from .plotting import plot_metrics

def main():
    parser = argparse.ArgumentParser(description="Plot metrics from one or more XML performance summary files.")
    parser.add_argument("xml_files", nargs="+", help="Path to one or more XML files")
    parser.add_argument("--x-axis", required=True, help="Metric name for the horizontal axis")
    parser.add_argument("--y-axis", required=True, help="Metric name for the vertical axis")
    parser.add_argument("--output-pdf", help="Output path for PDF plot")
    parser.add_argument("--output-html", help="Output path for HTML/SVG plot")
    parser.add_argument("--title", help="Plot title")
    parser.add_argument("--show", action="store_true", help="Show the plot in a window")

    args = parser.parse_args()

    datasets = []
    for xml_file in args.xml_files:
        if not os.path.exists(xml_file):
            print(f"Error: File {xml_file} not found.")
            sys.exit(1)

        try:
            df = read_xml_all_metrics(xml_file)
        except Exception as e:
            print(f"Error reading XML file {xml_file}: {e}")
            sys.exit(1)

        if args.x_axis not in df.columns:
            print(f"Error: Metric '{args.x_axis}' not found in {xml_file}. Available metrics: {', '.join(df.columns)}")
            sys.exit(1)
        if args.y_axis not in df.columns:
            print(f"Error: Metric '{args.y_axis}' not found in {xml_file}. Available metrics: {', '.join(df.columns)}")
            sys.exit(1)

        # Convert to numeric, dropping rows with non-numeric data for selected columns if necessary
        df[args.x_axis] = df[args.x_axis].apply(lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.','',1).isdigit() else None)
        df[args.y_axis] = df[args.y_axis].apply(lambda x: float(x) if isinstance(x, (int, float, str)) and str(x).replace('.','',1).isdigit() else None)
        
        df = df.dropna(subset=[args.x_axis, args.y_axis])
        
        if df.empty:
            print(f"Warning: No valid numeric data found for selected axes in {xml_file}. Skipping.")
            continue

        # Sort by x-axis for better plotting
        df = df.sort_values(by=args.x_axis)
        
        datasets.append({
            'x': df[args.x_axis].values,
            'y': df[args.y_axis].values,
            'label': os.path.basename(xml_file)
        })

    if not datasets:
        print("Error: No valid data to plot from any of the provided files.")
        sys.exit(1)

    plot_metrics(
        datasets=datasets,
        x_label=args.x_axis,
        y_label=args.y_axis,
        title=args.title,
        save_pdf=args.output_pdf,
        save_html=args.output_html,
        show=args.show
    )
    
    if args.output_pdf:
        print(f"PDF plot saved to {args.output_pdf}")
    if args.output_html:
        print(f"HTML plot saved to {args.output_html}")

if __name__ == "__main__":
    main()
