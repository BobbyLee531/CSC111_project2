"""
PearTrader – Stock Correlation Calculator
=========================

This module allows users to analyze and visualize correlations among a selected list of
stock tickers. Users can choose a date range and:
- Visualize the correlation matrix as a heatmap
- Build a correlation network with edges above a certain threshold
- Detect communities in the network using greedy modularity
- Query connected stocks in the same community
- Query the correlation coefficient between any two stocks

Copyright (c) 2025 by [Yuanzhe Li, Luke Pan, Alec Jiang, Junchen Liu]
All rights reserved.
"""
from click import command

import CorrelationCalc
import tkinter as tk
from tkinter import *

window = tk.Tk()
window.title("PearTrader")
window.geometry("1024x450")


def submit_date() -> None:
    start_input = start_entry.get()
    end_input = end_entry.get()
    try:
        start_date = CorrelationCalc.validate_date(start_input).strftime('%Y-%m-%d')
        end_date = CorrelationCalc.validate_date(end_input).strftime('%Y-%m-%d')
        CorrelationCalc.analyze_stocks(start_date, end_date)
    except ValueError as e:
        print(e)


def submit_stock_community() -> None:
    user_stock = community_entry.get().strip().upper()
    connected = CorrelationCalc.get_connected_stocks_in_community(user_stock)

    connected_window = Toplevel(window)
    connected_window.title("Stocks in the same community")
    connected_window.geometry("200x400")
    connected_scroll = Scrollbar(connected_window)
    connected_scroll.pack(side=RIGHT, fill=Y)
    connected_tickers = Text(connected_window, width=5, height=len(connected),
                             wrap=NONE, yscrollcommand=connected_scroll.set)
    if not connected:
        connected_tickers.insert(END, "No connected tickers")
    else:
        for ticker in connected:
            connected_tickers.insert(END, f"{ticker}: "
                                          f"{CorrelationCalc.get_correlation_between(user_stock, ticker):>8.4f} \n")

    connected_tickers.pack(side=TOP, fill=X)
    print(f"Connected stocks in the same community as {user_stock}: "
          f"{connected if connected else 'None or not found'}")


def submit_stock_comparison() -> None:
    stock1 = first_comparison_entry.get().strip().upper()
    stock2 = second_comparison_entry.get().strip().upper()
    corr_value = CorrelationCalc.get_correlation_between(stock1, stock2)
    if corr_value is not None:
        print(f"Correlation between {stock1} and {stock2}: {corr_value:.4f}")
        correlation_text.config(text=f"Correlation between {stock1} and {stock2}: {corr_value:.4f}")
    else:
        print("Invalid choice. Please try again.")
        correlation_text.config(text="Invalid choice. Please try again.")


start_text = Label(window, text="Enter Start Date")
start_text.pack()

start_entry = Entry(window)
start_entry.pack()
end_entry = Entry(window)
end_entry.pack()

submit = Button(window, text="submit dates", command=submit_date)
submit.pack()

community_text = Label(window, text="Enter a stock symbol to see its connected stocks in the same community: ")
community_text.pack()

community_entry = Entry(window)
community_entry.pack()

community_button = Button(window, text="Check stock community", command=submit_stock_community)
community_button.pack()

first_comparison_text = Label(window, text="Enter first stock")
first_comparison_text.pack()
first_comparison_entry = Entry(window)
first_comparison_entry.pack()

second_comparison_text = Label(window, text="Enter second stock")
second_comparison_text.pack()
second_comparison_entry = Entry(window)
second_comparison_entry.pack()

stock_comparison_submit = Button(window, text="Check stock correlation", command=submit_stock_comparison)
stock_comparison_submit.pack()

correlation_text = Label(window, text="")
correlation_text.pack()

if __name__ == '__main__':
    window.mainloop()
    # start_input = input("Enter start date (YYYY-MM-DD): ")
    # end_input = input("Enter end date (YYYY-MM-DD): ")
    #
    # try:
    #     start_date = CorrelationCalc.validate_date(start_input).strftime('%Y-%m-%d')
    #     end_date = CorrelationCalc.validate_date(end_input).strftime('%Y-%m-%d')
    #     CorrelationCalc.analyze_stocks(start_date, end_date)
    #
    #     while True:
    #         choice = (input("Choose mode: 1 - connected stocks, 2 - correlation between two stocks, exit - quit: ")
    #                   .strip().lower())
    #         if choice == 'exit':
    #             break
    #         elif choice == '1':
    #             user_stock = (input("Enter a stock symbol to see its connected stocks in the same community: ")
    #                           .strip().upper())
    #             connected = CorrelationCalc.get_connected_stocks_in_community(user_stock)
    #             print(f"Connected stocks in the same community as {user_stock}: "
    #                   f"{connected if connected else 'None or not found'}")
    #         elif choice == '2':
    #             stock1 = input("Enter the first stock symbol: ").strip().upper()
    #             stock2 = input("Enter the second stock symbol: ").strip().upper()
    #             corr_value = CorrelationCalc.get_correlation_between(stock1, stock2)
    #             if corr_value is not None:
    #                 print(f"Correlation between {stock1} and {stock2}: {corr_value:.4f}")
    #         else:
    #             print("Invalid choice. Please try again.")
    #
    # except ValueError as e:
    #     print(e)
