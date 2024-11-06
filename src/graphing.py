import argparse
import json
import matplotlib.pyplot as plt
from collections import defaultdict
import os
from pathlib import Path
import numpy as np
# import seaborn as sns
from scipy import stats

from printing import print_header_1

ALL_GRAPHING_PARAMS = ['bimodal_discount', 'set_size', 'num_people', 'num_interests', 'avg_points', 'think_through',
              'percent_chain_of_thought']

def get_latest_file(directory):
    return max(
        (os.path.join(root, f) for root, _, files in os.walk(directory) for f in files if f.endswith('.jsonl')),
        key=os.path.getmtime
    )


def load_results(file_path):
    print(f"Loading results from: {file_path}")
    with open(file_path, 'r') as f:
        results = [json.loads(line) for line in f]
    print(f"Loaded {len(results)} results")
    if results:
        print("First result keys:", results[0].keys())
    return results


def get_value(result, param):
    if "/" in param:
        parts = param.split("/")
        while parts:
            try:
                result = result[parts.pop(0)]
            except KeyError as e:
                raise e
        return result

    try:
        return result['doc']['scoring_guide']['parameters'][param]
    except KeyError as e:
        pass
    try:
        return result['doc']['scoring_guide'][param]
    except KeyError as e:
        pass
    try:
        return result['doc'][param]
    except KeyError as e:
        pass
    try:
        return result[param]
    except KeyError as e:
        raise e


def get_data(param, results, y_value, min_n=1):
    param_values = defaultdict(list)
    for i, result in enumerate(results):
        try:
            param_value = get_value(result, param)
            # For readability, convert integer values to strings
            if param == "think_through":
                param_value = {0: "No thinking through", 1: "Brief thought", 2: "Deep thought"}[param_value]
            if y_value:
                param_values[param_value].append(result[y_value])
            else:
                param_values[param_value].append(1)
        except KeyError as e:
            print(f"  KeyError: {e}")
            raise e
    
    # Get all x values
    all_x_data = list(param_values.keys())
    
    # Filter out groups with insufficient N
    if min_n > 1:
        valid_x_data = [x for x in all_x_data if len(param_values[x]) >= min_n]
        if len(valid_x_data) < len(all_x_data):
            print(f"\nNote: Excluding groups with N < {min_n}")
            print(f"Original groups: {len(all_x_data)}, Valid groups: {len(valid_x_data)}")
    else:
        valid_x_data = all_x_data

    # Sort x values if they're all numeric
    if all(isinstance(x, (int, float)) for x in valid_x_data):
        valid_x_data.sort()
    
    return param_values, valid_x_data


def print_full_combinatoric_stats(results, params, y_value, args):
    # Create combinations counter
    combinations = defaultdict(int)
    total_results = 0

    for result in results:
        try:
            # Build combination tuple
            combo = []
            for p in params:
                try:
                    val = get_value(result, p)
                    combo.append((p, val))
                except KeyError:
                    continue
            combo = tuple(combo)
            combinations[combo] += 1
            total_results += 1
        except KeyError:
            continue

    # Print each combination and its count
    print_header_1("Combinations:")
    for combo, count in sorted(combinations.items(), key=lambda x: (-x[1], x[0])):
        print()
        for param_name, value in combo:
            print(f"{param_name:25}: {value}")
        print(f"Count: {count} ({count/total_results*100:.1f}%)")


def print_stats(results, param, y_value, args):
    param_values, valid_x_data = get_data(param, results, y_value, args.min_n)
    
    print(f"\nStatistical Analysis for {param.replace('_', ' ').title()} vs {y_value.replace('_', ' ').title() if y_value else 'Count'}")
    print("-" * 80)

    # Print summary statistics for each parameter value
    for x in sorted(valid_x_data):
        values = param_values[x]
        print(f"\nGroup: {x}")
        print(f"  N: {len(values)}")
        if y_value:
            print(f"  Mean: {np.mean(values):.3f}")
            print(f"  Median: {np.median(values):.3f}")
            print(f"  Std Dev: {np.std(values):.3f}")
            print(f"  Min: {np.min(values):.3f}")
            print(f"  Max: {np.max(values):.3f}")
    
    # If we have numeric x values and more than one group, perform regression analysis
    if len(valid_x_data) > 1 and all(isinstance(x, (int, float)) for x in valid_x_data):
        all_x = []
        all_y = []
        for x in valid_x_data:
            all_x.extend([x] * len(param_values[x]))
            all_y.extend(param_values[x])
            
        slope, intercept, r_value, p_value, std_err = stats.linregress(all_x, all_y)
        print(f"\nRegression Analysis:")
        print(f"  Slope: {slope:.3f}")
        print(f"  Intercept: {intercept:.3f}")
        print(f"  R-squared: {r_value**2:.3f}")
        print(f"  P-value: {p_value:.3f}")
        print(f"  Standard Error: {std_err:.3f}")
    
    # If we have more than one group, perform ANOVA
    if len(valid_x_data) > 1 and y_value:
        groups = [param_values[x] for x in valid_x_data]
        f_stat, anova_p = stats.f_oneway(*groups)
        print(f"\nOne-way ANOVA:")
        print(f"  F-statistic: {f_stat:.3f}")
        print(f"  P-value: {anova_p:.3f}")


def create_graph(results, param, y_value, args):
    print(f"Creating graph with param: {param}, y_value: {y_value}")
    param_values, x_data = get_data(param, results, y_value, args.min_n)

    assert y_value, "No y_value specified. You probably want to run this command with `--y_value=correct` or similar."

    plt.figure(figsize=(14, 8))  # Larger figure to accommodate additional legend

    if args.graph_type == "default":
        args.graph_type = "box"
        # Check if data is all binary
        all_values = [v for values in param_values.values() for v in values]
        if all(v in [0, 1, False, True] for v in all_values):
            args.graph_type = "binary"

    if args.graph_type == "box":
        create_box_plot(args, param, param_values, x_data, y_value)
    elif args.graph_type == "binary":
        create_binary_plot(args, param, param_values, x_data, y_value)

    # print the location where these are all saved
    output_dir = Path(args.file).parent / Path(args.file).stem
    print(f"\nGraphs saved in: {output_dir}")


def create_binary_plot(args, param, param_values, x_data, y_value):
    # Calculate proportions and confidence intervals for each group
    proportions = []
    confidence_intervals = []
    ns = []
    
    for x in x_data:
        values = param_values[x]
        n = len(values)
        ns.append(n)
        # Calculate proportion of 1's
        prop = sum(1 for v in values if v == 1) / n
        proportions.append(prop)
        
        # Calculate Wilson score interval
        if n > 0:
            z = 1.96  # 95% confidence
            denominator = 1 + z**2/n
            center = (prop + z**2/(2*n))/denominator
            spread = z * np.sqrt(prop*(1-prop)/n + z**2/(4*n**2))/denominator
            confidence_intervals.append((spread, spread))
        else:
            confidence_intervals.append((0, 0))

    # Create bar plot with appropriate colors
    if args.use_multiple_colors:
        # Generate distinct colors using a colormap
        colors = plt.cm.Set3(np.linspace(0, 1, len(x_data)))
        bars = plt.bar(range(1, len(x_data) + 1), proportions, alpha=0.8, color=colors)
    else:
        # Use single color for all bars
        bars = plt.bar(range(1, len(x_data) + 1), proportions, alpha=0.6, color='#1E88E5')
    
    # Add error bars
    plt.errorbar(range(1, len(x_data) + 1), proportions, 
                yerr=np.array(confidence_intervals).T,
                fmt='none', color='#D81B60', capsize=5)

    # Customize the plot
    plt.xlabel(param.replace('_', ' ').title(), fontsize=11, fontweight='bold')
    plt.ylabel(f'Proportion of {y_value.replace("_", " ").title()}', fontsize=11, fontweight='bold')
    plt.title(f'Impact of {param.replace("_", " ").title()} on {y_value.replace("_", " ").title()}', 
              fontsize=13, fontweight='bold')
    
    # Set x-axis ticks
    plt.xticks(range(1, len(x_data) + 1), x_data, rotation=0, ha='center', fontsize=9)
    
    # Add sample size labels below x-axis
    for i, (x, n) in enumerate(zip(x_data, ns)):
        plt.text(i + 1, -0.05, f'N={n}', ha='center', va='top', transform=plt.gca().get_xaxis_transform())
    
    # Add proportion values on top of bars
    for i, prop in enumerate(proportions):
        plt.text(i + 1, prop, f'{prop:.2f}', ha='center', va='bottom')
    
    # Customize grid and background
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.gca().set_facecolor('#f9f9f9')
    
    # Set y-axis limits to accommodate labels
    plt.ylim(-0.05, 1.1)
    
    # Add subtle border
    for spine in plt.gca().spines.values():
        spine.set_edgecolor('#e0e0e0')
    
    # Add legend
    legend_labels = [f'{param.replace("_", " ").title()} = {x}: N={n}' for x, n in zip(x_data, ns)]
    plt.legend(bars,
              legend_labels,
              title="Parameter Values and Sample Sizes\n(Error bars show 95% CI)",
              title_fontsize=10, fontsize=8,
              loc='center left', bbox_to_anchor=(1, 0.5))
    
    plt.tight_layout()
    
    # Save the graph
    output_dir = Path(args.file).parent / Path(args.file).stem
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{param}_{y_value}_binary.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph saved as: {output_file}")
    
    if args.display_graph:
        plt.show()
    plt.close()


def create_box_plot(args, param, param_values, x_data, y_value):
    # Create box plot
    box_plot = plt.boxplot([param_values[x] for x in x_data], patch_artist=True, medianprops={'color': "#D81B60"})
    # Customize box plot colors
    if args.use_multiple_colors:
        # Generate distinct colors using a colormap
        colors = plt.cm.Set3(np.linspace(0, 1, len(x_data)))
        for box, color in zip(box_plot['boxes'], colors):
            box.set(facecolor=color, alpha=0.8)
    else:
        # Use single color for all boxes
        for box in box_plot['boxes']:
            box.set(facecolor='#1E88E5', alpha=0.6)
    # Plot individual data points with jitter
    all_x = []
    all_y = []
    for i, x in enumerate(x_data):
        y = param_values[x]
        jitter = np.random.normal(0, 0.1, len(y))
        plt.scatter(np.array([i + 1] * len(y)) + jitter, y, color='#888888', alpha=0.3, s=30, zorder=2)
        all_x.extend([x] * len(y))
        all_y.extend(y)
    # Compute best fit line
    # all_x will be non-numeric if it's string values
    if all(isinstance(i, (int, float)) for i in all_x):
        slope, intercept, r_value, p_value, std_err = stats.linregress(all_x, all_y)
        line = slope * np.array(x_data) + intercept
        plt.plot(range(1, len(x_data) + 1), line, color='red', linestyle='--',
                 label=f'Best Fit Line (R² = {r_value ** 2:.3f})')
        r_value_legend = [f'Best Fit Line (slope = {slope:.3f}) (R² = {r_value ** 2:.3f})']
    else:
        r_value_legend = []
    plt.xlabel(param.replace('_', ' ').title(), fontsize=11, fontweight='bold')
    plt.ylabel(f'{y_value.replace("_", " ").title()}', fontsize=11, fontweight='bold')
    plt.title(f'Impact of {param.replace("_", " ").title()} on {y_value.replace("_", " ").title()}', fontsize=13,
              fontweight='bold')
    plt.xticks(range(1, len(x_data) + 1), x_data, rotation=0, ha='center', fontsize=9)
    # Print median horizontally below the x-axis labels
    for i, x in enumerate(x_data):
        median_value = np.median(param_values[x])
        plt.text(i + 1, plt.gca().get_ylim()[0] - 0.03 * (plt.gca().get_ylim()[1] - plt.gca().get_ylim()[0]),
                 f'Median: {median_value:.2f}', rotation=0, va='top', ha='center', fontsize=8)
    plt.yticks(fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    plt.gca().set_facecolor('#f9f9f9')  # Very light gray background
    # Add a subtle border
    for spine in plt.gca().spines.values():
        spine.set_edgecolor('#e0e0e0')
    # Add legend to show N for each bin and best fit line info
    legend_labels = [f'{param.replace("_", " ").title()} = {x}: N={len(param_values[x])}' for x in x_data]
    plt.legend(legend_labels + r_value_legend,
               title="Parameter Values and Sample Sizes", title_fontsize=10, fontsize=8,
               loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    # Save the graph as an image
    output_dir = Path(args.file).parent / Path(args.file).stem
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{param}_{y_value}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph saved as: {output_file}")
    # Show it to the user if display_graph is True
    if args.display_graph:
        plt.show()
    plt.close()


def main(args):
    # default_input_dir = Path(__file__).parents[3] / "tasks" / "dinner_party" / "results"
    # default_input_file = get_latest_file(default_input_dir)

    params = args.parts

    print(f"Input file: {args.file}")
    print(f"Params: {params}")
    print(f"Y-value: {args.y_value}")
    print(f"Display graph: {args.display_graph}")

    results = load_results(args.file)

    if params[0] == 'all':
        params = ALL_GRAPHING_PARAMS

    if args.stats and args.full_combinatoric:
        print_full_combinatoric_stats(results, params, args.y_value, args)
        return

    for param in params:
        # Check to see if all the values are the same
        all_values = set()
        for result in results:
            all_values.add(get_value(result, param))
        if len(all_values) == 1:
            print(f"  Skipping graph for parameter {param} because all values are the same: {all_values}")
            continue

        if args.stats:
            print_stats(results, param, args.y_value, args)
        else:
            create_graph(results, param, args.y_value, args)
