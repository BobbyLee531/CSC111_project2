"""
PearTrader – Stock Correlation Calculator
=========================

This module handles the GUI for the application. Users can
input information into text boxes to use the calculator.
Results will be updated on the page, open in seperate windows,
or open in your browser.

Copyright (c) 2025 by [Yuanzhe Li, Luke Pan, Alec Jiang, Junchen Liu]
All rights reserved.
"""

import tkinter as tk
import correlation_calc


def threshold_set() -> float:
    """
    Get input threshold value, and filter if threshold is invalid.
    """
    threshold_value = threshold_entry.get()
    try:
        threshold_value = float(threshold_value)
        threshold_alert.config(text="", fg="red")
        if threshold_value < 0.5:
            threshold_alert.config(text="Threshold too low, set to default", fg="red")
            threshold_value = 0.68
    except ValueError:
        threshold_value = 0.68
        threshold_alert.config(text="Invalid threshold, set to default", fg="red")
    return threshold_value


def submit_date() -> None:
    """
    Take input from the date and threshold entry fields, and recieve data from Yahoo Finance.
    Analyze the given data with correlation_calc methods.

    Preconditions:
        - start_entry is not None and end_entry is not None
        - start_entry.get() and end_entry.get() are in 'YYYY-MM-DD' format.
        - threshold_entry.get() >= 0
        - start_date < end_date.
    """
    start_input = start_entry.get()
    end_input = end_entry.get()
    threshold_value = threshold_set()
    try:
        start_date = correlation_calc.validate_date(start_input).strftime('%Y-%m-%d')
        end_date = correlation_calc.validate_date(end_input).strftime('%Y-%m-%d')
        correlation_calc.filter_data(start_date, end_date)
        correlation_calc.analyze_stocks(start_date, end_date, threshold_value)
        progress_text.config(text="Opening graph in browser", fg="green")
    except ValueError as e:
        progress_text.config(text="Incorrect date format, should be YYYY-MM-DD", fg="red")
        print(e)


def submit_stock_community() -> None:
    """
    Take input from the community entry fields, and find all stocks in the same community.
    Open a new window with all the stocks in the community with their correlation values.

    Preconditions:
        - community_entry is not None
        - community_entry.get() is a valid node in the graph
    """
    user_stock = community_entry.get().strip().upper()
    threshold_value = threshold_set()

    connected = correlation_calc.get_connected_stocks_in_community(user_stock, threshold_value)

    connected_window = tk.Toplevel(window)
    connected_window.title("Stocks in the same community")
    connected_window.geometry("200x400")
    connected_scroll = tk.Scrollbar(connected_window)
    connected_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    connected_tickers = tk.Text(connected_window, width=5, height=len(connected),
                                wrap=tk.NONE, yscrollcommand=connected_scroll.set)
    if not connected:
        connected_tickers.insert(tk.END, "No connected tickers")
    else:
        connected_tickers.insert(tk.END, "Ticker  | Correlation\n")
        for ticker in connected:
            connected_tickers.insert(tk.END, f"{ticker:<7} | "
                                     f"{correlation_calc.get_correlation_between(user_stock, ticker):.4f} \n")

    connected_tickers.pack(side=tk.TOP, fill=tk.X)


def submit_stock_comparison() -> None:
    """
    Find and display the correlation value between two inputted stocks.

    Preconditions:
        - first_comparison_entry is not None and second_comparison_entry is not None
        - first_comparison_entry.get() and second_comparison_entry.get() are valid nodes in the graph
    """
    stock1 = first_comparison_entry.get().strip().upper()
    stock2 = second_comparison_entry.get().strip().upper()
    corr_value = correlation_calc.get_correlation_between(stock1, stock2)
    if corr_value is not None:
        correlation_text.config(text=f"Correlation between {stock1} and {stock2}: {corr_value:.4f}")
    else:
        correlation_text.config(text="Invalid choice. Please try again.")


if __name__ == '__main__':
    # import python_ta
    # python_ta.check_all(config={
    #     'extra-imports': ['correlation_calc', 'tkinter'],  # the names (strs) of imported modules
    #     'allowed-io': ['submit_date', 'submit_date'],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

    window = tk.Tk()
    window.title("PearTrader")
    window.geometry("400x400")

    start_text = tk.Label(window, text="Enter Start and End Dates (YYYY-MM-DD)")
    start_text.pack()

    start_entry = tk.Entry(window)
    start_entry.pack()
    end_entry = tk.Entry(window)
    end_entry.pack()

    threshold_text = tk.Label(window, text="Enter threshold (<0.5, >1, default 0.68):")
    threshold_text.pack()

    threshold_entry = tk.Entry(window)
    threshold_entry.pack()

    threshold_alert = tk.Label(window, text="")
    threshold_alert.pack()

    submit = tk.Button(window, text="submit dates", command=submit_date)
    submit.pack()

    progress_text = tk.Label(window, text="")
    progress_text.pack()

    community_text = tk.Label(window, text="Enter a stock symbol to see its connected stocks in the same community: ")
    community_text.pack(pady=(20, 0))

    community_entry = tk.Entry(window)
    community_entry.pack()

    community_button = tk.Button(window, text="Check stock community", command=submit_stock_community)
    community_button.pack()

    first_comparison_text = tk.Label(window, text="Enter first stock")
    first_comparison_text.pack(pady=(20, 0))
    first_comparison_entry = tk.Entry(window)
    first_comparison_entry.pack()

    second_comparison_text = tk.Label(window, text="Enter second stock")
    second_comparison_text.pack()
    second_comparison_entry = tk.Entry(window)
    second_comparison_entry.pack()

    stock_comparison_submit = tk.Button(window, text="Check stock correlation", command=submit_stock_comparison)
    stock_comparison_submit.pack()

    correlation_text = tk.Label(window, text="")
    correlation_text.pack()
    window.mainloop()
