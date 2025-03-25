import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Global variable for dataset
df = None

# Tkinter window
root = tk.Tk()
root.title("Sales Analysis Tool")
root.geometry("1000x700")

# Frames for layout
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

plot_frame = ttk.Frame(root)
plot_frame.pack(fill=tk.BOTH, expand=True)

toolbar_frame = ttk.Frame(root)  # Frame for toolbar
toolbar_frame.pack(fill=tk.X)

# Function to load a CSV file
def open_csv():
    global df
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    
    if not file_path:
        return  # If no file is selected, do nothing
    
    try:
        df = pd.read_csv(file_path)

        # Check if required column exists
        if "Daily_Revenue" not in df.columns:
            messagebox.showerror("Error", "Invalid CSV format! 'Daily_Revenue' column not found.")
            df = None
            return

        # Reduce dataset to only the last 2 years (730 days)
        df = df.tail(730)
        
        messagebox.showinfo("Success", "CSV loaded successfully! (Last 2 years of data)")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")

# Function to clear previous plot and toolbar
def clear_plot():
    for widget in plot_frame.winfo_children():
        widget.destroy()
    for widget in toolbar_frame.winfo_children():
        widget.destroy()

# Function to show daily trends
def show_trends():
    if df is None or df.empty:
        messagebox.showerror("Error", "No CSV file loaded or dataset is empty!")
        return

    clear_plot()

    # Take last 'n' days of data (ensuring index starts from 1)
    last_n_days = 730  # Adjust this based on how much data you want to show
    df_trimmed = df.tail(last_n_days).copy()
    df_trimmed.reset_index(drop=True, inplace=True)
    df_trimmed.index = df_trimmed.index + 1  # Make index start from 1

    # Reduce number of plotted points dynamically
    downsample_factor = max(1, len(df_trimmed) // 50)  # Adjust to control density
    df_downsampled = df_trimmed.iloc[::downsample_factor]  # Pick every Nth point

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df_downsampled.index, df_downsampled["Daily_Revenue"], marker="o", linestyle="-", color="b", alpha=0.7)

    # Show labels every 20th point to reduce clutter
    tick_spacing = max(1, len(df_downsampled) // 20)
    ax.set_xticks(df_downsampled.index[::tick_spacing])
    ax.set_xticklabels(df_downsampled.index[::tick_spacing], rotation=45, fontsize=8)

    ax.set_title("Daily Sales Trend of last 2 years", fontsize=14, fontweight="bold")
    ax.set_xlabel("Days", fontsize=12)
    ax.set_ylabel("Revenue (₹)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    
# Function to show weekly trends
def show_weekly_trends():
    if df is None or df.empty:
        messagebox.showerror("Error", "No CSV file loaded or dataset is empty!")
        return

    clear_plot()

    # Take last 'n' weeks of data (ensuring index starts from 1)
    last_n_weeks = 104  # Adjust this based on how much data you want to show
    df_trimmed = df.tail(last_n_weeks * 7).copy()  # Last N weeks (each week = 7 days)

    # Group by week and sum revenue
    df_weekly = df_trimmed.groupby(df_trimmed.index // 7).sum()
    df_weekly.index = range(1, len(df_weekly) + 1)  # Make index start from 1

    # Reduce number of plotted points dynamically
    downsample_factor = max(1, len(df_weekly) // 50)  # Adjust to control density
    df_downsampled = df_weekly.iloc[::downsample_factor]  # Pick every Nth week

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df_downsampled.index, df_downsampled["Daily_Revenue"], marker="o", linestyle="-", color="g", alpha=0.7)

    # Show labels every 10th point to reduce clutter
    tick_spacing = max(1, len(df_downsampled) // 10)
    ax.set_xticks(df_downsampled.index[::tick_spacing])
    ax.set_xticklabels(df_downsampled.index[::tick_spacing], rotation=45, fontsize=8)

    ax.set_title("Weekly Sales Trend of last 24 months", fontsize=14, fontweight="bold")
    ax.set_xlabel("Weeks", fontsize=12)
    ax.set_ylabel("Revenue (₹)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    
def show_monthly_trends():
    if df is None or df.empty:
        messagebox.showerror("Error", "No CSV file loaded or dataset is empty!")
        return

    clear_plot()

    # Take last 'n' months of data (ensuring index starts from 1)
    last_n_months = 24  # Adjustable: Last 24 months (2 years)
    df_trimmed = df.tail(last_n_months * 30).copy()  # Assuming each month ≈ 30 days

    # Group by month and sum revenue
    df_monthly = df_trimmed.groupby(df_trimmed.index // 30).sum()
    df_monthly.index = range(1, len(df_monthly) + 1)  # Make index start from 1

    # Reduce number of plotted points dynamically
    downsample_factor = max(1, len(df_monthly) // 15)  # Adjust based on graph clarity
    df_downsampled = df_monthly.iloc[::downsample_factor]

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df_downsampled.index, df_downsampled["Daily_Revenue"], marker="o", linestyle="-", color="b", alpha=0.7)

    # Reduce x-axis label clutter
    tick_spacing = max(1, len(df_downsampled) // 10)
    ax.set_xticks(df_downsampled.index[::tick_spacing])
    ax.set_xticklabels(df_downsampled.index[::tick_spacing], rotation=45, fontsize=8)

    ax.set_title("Monthly Sales Trend of last 2 years", fontsize=14, fontweight="bold")
    ax.set_xlabel("Months", fontsize=12)
    ax.set_ylabel("Revenue (₹)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Ensure it appears properly in the GUI
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

def forecast_sales():
    if df is None or df.empty:
        messagebox.showerror("Error", "No CSV file loaded or dataset is empty!")
        return

    clear_plot()

    # Ensure required column exists
    if "Daily_Revenue" not in df.columns:
        messagebox.showerror("Error", "'Daily_Revenue' column not found in dataset!")
        return

    df_copy = df.copy()
    df_copy["Day_Number"] = np.arange(1, len(df_copy) + 1)  # Ensure numbering starts from 1

    X = df_copy[["Day_Number"]]
    y = df_copy["Daily_Revenue"]

    model = LinearRegression()
    model.fit(X, y)

    # Show only last 25% of data before forecasting
    last_25_percent = int(len(df_copy) * 0.25)
    X_recent = X.iloc[-last_25_percent:]
    y_recent = y.iloc[-last_25_percent:]

    # Generate Predictions for Next 30 Days
    future_days = np.arange(len(df_copy) + 1, len(df_copy) + 31).reshape(-1, 1)  # Next 30 days
    predicted_sales = model.predict(future_days)

    fig, ax = plt.subplots(figsize=(10, 5))

    # Fix X-axis scaling issue
    min_x = X_recent["Day_Number"].min()

    # Plot recent actual data
    ax.plot(X_recent["Day_Number"] - min_x + 1, y_recent, label="Recent Sales Data", color="blue", linewidth=2)

    # Plot forecasted trend line
    ax.plot(future_days - min_x + 1, predicted_sales, label="Predicted Sales", color="red", linestyle="dashed", linewidth=2)

    # Confidence Range (90%-110%)
    ax.fill_between(
        (future_days - min_x + 1).flatten(),
        predicted_sales * 0.9,
        predicted_sales * 1.1,
        color="red",
        alpha=0.2,
        label="Confidence Range"
    )

    # Adjust X-axis ticks
    max_visible_x = (future_days - min_x + 1).max()
    ax.set_xticks(range(1, max_visible_x + 1, max_visible_x // 10))

    ax.set_title("Sales Forecast (Next 30 Days)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Days", fontsize=12)
    ax.set_ylabel("Revenue (₹)", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    # Embed plot into Tkinter
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()

# Buttons
btn_open = ttk.Button(button_frame, text="Open CSV", command=open_csv)
btn_open.pack(side=tk.LEFT, padx=10)

btn_trends = ttk.Button(button_frame, text="Show Daily Trends", command=show_trends)
btn_trends.pack(side=tk.LEFT, padx=10)

btn_weekly = ttk.Button(button_frame, text="Show Weekly Trends", command=show_weekly_trends)
btn_weekly.pack(side=tk.LEFT, padx=10)

btn_monthly = ttk.Button(button_frame, text="Show Monthly Trends", command=show_monthly_trends)
btn_monthly.pack(side=tk.LEFT, padx=5, pady=5)

forecast_button = ttk.Button(button_frame, text="Forecast Sales", command=forecast_sales)
forecast_button.pack(side=tk.LEFT, padx=10)

# Run Tkinter loop
root.mainloop()