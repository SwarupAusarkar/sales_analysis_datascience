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

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(df.index, df["Daily_Revenue"], marker="o", linestyle="-", color="b", alpha=0.7)

    # Show labels only every 10 days
    ax.set_xticks(df.index[::10])  
    ax.set_xticklabels(df.index[::10], rotation=45, fontsize=8)

    ax.set_title("Daily Sales Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Days", fontsize=12)
    ax.set_ylabel("Revenue (₹)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add interactive toolbar
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    
# Function to show weekly trends
def show_weekly_trends():
    if df is None or df.empty:
        messagebox.showerror("Error", "No CSV file loaded or dataset is empty!")
        return

    clear_plot()
    
    # Ensure 'Week' column exists for grouping
    df["Week"] = df.index // 7  # Assign week numbers (assuming sequential days)

    weekly_sales = df.groupby("Week")["Daily_Revenue"].sum()

    fig, ax = plt.subplots(figsize=(8, 5))
    
    bars = ax.bar(weekly_sales.index, weekly_sales.values, color="orange", alpha=0.8)

    # Add labels but only for every 5th bar
    for i, bar in enumerate(bars):
        if i % 5 == 0:  
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, f"{int(yval)}", ha="center", va="bottom", fontsize=8, rotation=30)

    ax.set_title("Weekly Sales Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Weeks", fontsize=12)
    ax.set_ylabel("Total Weekly Revenue (₹)", fontsize=12)
    ax.set_xticks(weekly_sales.index[::5])  # Reduce x-axis labels
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack()
    canvas.draw()

    # Add interactive toolbar
    toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
    toolbar.update()
    
def show_monthly_trends():
    if df is None or df.empty:
        messagebox.showerror("Error", "No CSV file loaded or dataset is empty!")
        return

    clear_plot()

    df["Month"] = df.index // 30  # Assuming 30 days per month

    monthly_sales = df.groupby("Month")["Daily_Revenue"].sum()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(monthly_sales.index, monthly_sales.values, color="green", alpha=0.7)

    ax.set_title("Monthly Sales Trend", fontsize=14, fontweight="bold")
    ax.set_xlabel("Months", fontsize=12)
    ax.set_ylabel("Total Monthly Revenue (₹)", fontsize=12)
    ax.set_xticks(monthly_sales.index[::2])  # Show labels every 2 months

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

    df["Day_Number"] = np.arange(len(df))  

    X = df[["Day_Number"]]  
    y = df["Daily_Revenue"]  

    model = LinearRegression()
    model.fit(X, y)

    # **Show only last 25% of data before forecasting**
    last_25_percent = int(len(df) * 0.25)
    X_recent = X.iloc[-last_25_percent:]
    y_recent = y.iloc[-last_25_percent:]

    # **Generate Predictions for Next 30 Days**
    future_days = np.arange(len(df), len(df) + 30).reshape(-1, 1)
    future_days_df = pd.DataFrame(future_days, columns=["Day_Number"])  
    predicted_sales = model.predict(future_days_df)

    fig, ax = plt.subplots(figsize=(10, 5))

    # **Plot last 25% actual data**
    ax.plot(X_recent, y_recent, label="Recent Sales Data", color="blue", linewidth=2)

    # **Plot forecasted trend line (NO dots or labels)**
    ax.plot(future_days, predicted_sales, label="Predicted Sales", color="red", linestyle="dashed", linewidth=2)

    # **Confidence Zone (Shaded Area)**
    ax.fill_between(
        future_days.flatten(), 
        predicted_sales * 0.9,  # Lower bound (90% confidence)
        predicted_sales * 1.1,  # Upper bound (110% confidence)
        color="red", 
        alpha=0.2,
        label="Confidence Range"
    )

    # **Fix: Adjust X-axis ticks for better readability**
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5))  # Show every 5 days
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))  # Small ticks for each day
    plt.xticks(rotation=45)  # Rotate labels slightly for better spacing

    ax.set_title("Sales Forecast (Next 30 Days)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Days", fontsize=12)
    ax.set_ylabel("Revenue (₹)", fontsize=12)
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

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

forecast_button = ttk.Button(button_frame, text="Forecast Sales", command=forecast_sales)
forecast_button.pack(side=tk.LEFT, padx=10)

# Run Tkinter loop
root.mainloop()