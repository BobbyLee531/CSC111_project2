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

from datetime import datetime
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from networkx.algorithms.community import greedy_modularity_communities
import networkx as nx
import plotly.graph_objects as go
import pandas as pd


# Global variables
G = nx.Graph()
communities = []
correlation_matrix = pd.DataFrame()
threshold = 0.68


def validate_date(date_text):
    """
    Validate that the input date string is in YYYY-MM-DD format.

    Preconditions:
        - date_text is a string in format 'YYYY-MM-DD'.

    Returns:
        - datetime object parsed from the input string.

    Raises:
        - ValueError if the input format is incorrect.
    """
    try:
        return datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect date format, should be YYYY-MM-DD")


def analyze_stocks(start_date, end_date):
    """
    Download historical stock data, compute correlations, generate a graph, identify communities,
    and visualize using Plotly.

    Preconditions:
        - start_date and end_date are in 'YYYY-MM-DD' format.
        - start_date < end_date.

    Representation Invariants:
        - G is populated with nodes and edges based on correlation threshold.
        - correlation_matrix is a symmetric DataFrame with float values.
        - communities is a list of disjoint sets representing modularity-based communities.
        - start_date and end_date are the dates that indicate the time range of the data
    """
    global G, communities, correlation_matrix

    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    returns = data.pct_change().dropna()
    correlation_matrix = returns.corr()

    # Plot heatmap
    plt.figure(figsize=(20, 16))
    sns.heatmap(correlation_matrix, annot=False, cmap='coolwarm', fmt=".1f")
    plt.title(f'Stock Correlation Matrix ({start_date} to {end_date})')
    plt.show()

    G = nx.Graph()
    for stock in correlation_matrix.columns:
        G.add_node(stock)

    for i in range(len(correlation_matrix.columns)):
        for j in range(i + 1, len(correlation_matrix.columns)):
            correlation = correlation_matrix.iloc[i, j]
            if correlation >= threshold:
                G.add_edge(correlation_matrix.columns[i], correlation_matrix.columns[j], weight=correlation)

    communities = list(greedy_modularity_communities(G))

    pos = {}
    y_offset = 1
    for i, community in enumerate(communities):
        sub_g = G.subgraph(community)
        sub_pos = nx.spring_layout(sub_g, seed=42, k=15, iterations=100)
        x_offset = i * 6
        for node, (x, y) in sub_pos.items():
            pos[node] = (x + x_offset, y + y_offset)

    isolated_nodes = [node for node in G.nodes if G.degree(node) == 0]
    if isolated_nodes:
        isolated_pos = {node: (i * 1, -2) for i, node in enumerate(isolated_nodes)}
        pos.update(isolated_pos)

    edge_traces = []
    edge_labels = []
    for stock1, stock2, attributes in G.edges(data=True):
        x0, y0 = pos[stock1]
        x1, y1 = pos[stock2]
        edge_traces.append(go.Scatter(
            x=[x0, x1, None], y=[y0, y1, None],
            line=dict(width=1, color='gray'),
            mode='lines',
            hoverinfo='none'
        ))
        edge_labels.append(go.Scatter(
            x=[(x0 + x1) / 2], y=[(y0 + y1) / 2],
            mode='text',
            text=[f'{attributes["weight"]:.2f}'],
            showlegend=False,
            hoverinfo='name',
            name=f'{stock1}-{stock2}:{attributes["weight"]:.2f}'
        ))

    node_traces = []
    for i, community in enumerate(communities):
        for node in community:
            x, y = pos[node]
            node_traces.append(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                text=node,
                textposition="top center",
                hoverinfo='none',
                marker=dict(
                    size=10,
                    color=plt.cm.rainbow(i / len(communities)),
                    line=dict(width=2, color='black')
                )
            ))

    fig = go.Figure(data=edge_traces + edge_labels + node_traces)
    fig.update_layout(
        title=f'Stock Correlation Network ({start_date} to {end_date})',
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='white'
    )
    plt.show()
    fig.show()


def get_connected_stocks_in_community(stock):
    """
    Return a list of stocks that are in the same community as `stock` and have
    a correlation greater than or equal to the global threshold.

    Preconditions:
        - analyze_stocks() must be called before this function.
        - stock must be a valid ticker in the graph.

    Returns:
        - List of ticker symbols connected to `stock` within its community.
    """
    global G, communities, correlation_matrix, threshold

    if G is None or communities is None or correlation_matrix is None:
        print("Run analyze_stocks() first to build the network.")
        return []

    if stock not in G:
        print(f"{stock} is not in the graph.")
        return []

    for community in communities:
        if stock in community:
            return [other for other in community
                    if other != stock and correlation_matrix.loc[stock, other] >= threshold]
    return []


def get_correlation_between(stock1, stock2):
    """
    Return the correlation value between two stock tickers.

    Preconditions:
        - analyze_stocks() must be called before this function.
        - stock1 and stock2 must be in correlation_matrix.columns

    Returns:
        - Correlation coefficient between stock1 and stock2.
    """
    global correlation_matrix

    if correlation_matrix is None:
        print("Run analyze_stocks() first to calculate correlations.")
        return None

    if stock1 not in correlation_matrix.columns or stock2 not in correlation_matrix.columns:
        print("One or both stock symbols not found in the correlation matrix.")
        return None

    return correlation_matrix.loc[stock1, stock2]


if __name__ == '__main__':
    # import doctest
    #
    # doctest.testmod(verbose=True)
    #
    # import python_ta
    #
    # python_ta.check_all(config={
    #     'extra-imports': [],  # the names (strs) of imported modules
    #     'allowed-io': [],  # the names (strs) of functions that call print/open/input
    #     'max-line-length': 120
    # })

    # Define tickers
    # Precondition: All elements are valid stock tickers available on Yahoo Finance.
    tickers = [
        "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "AVGO", "TSLA", "LLY",
        "WMT", "JPM", "V", "XOM", "MA", "UNH", "JNJ", "PG", "HD", "CVX",
        "MRK", "ABBV", "COST", "DIS", "ADBE", "CSCO", "MCD", "ACN", "ABT", "DHR",
        "NFLX", "LIN", "INTC", "CMCSA", "VZ", "TMO", "NKE", "QCOM", "TXN", "NEE",
        "HON", "UNP", "LOW", "BMY", "SPGI", "IBM", "AMD", "GS", "CAT", "ISRG",
        "ELV", "AMGN", "GE", "BLK", "MDT", "NOW", "INTU", "LMT", "DE", "SYK",
        "AMT", "PLD", "ADI", "CB", "PYPL", "C", "T", "SCHW", "MO", "DUK",
        "SO", "MMC", "CI", "ZTS", "BSX", "HUM", "PGR", "TJX", "BDX", "ADP",
        "CME", "TGT", "USB", "ICE", "APD", "ITW", "EQIX", "PNC", "ECL", "NSC",
        "VRTX", "SHW", "CSX", "COP", "REGN", "FDX", "EW", "D", "AON", "MCO",
        "CL", "FIS", "MET", "MNST", "MAR", "KMB", "PSA", "ORLY", "SNPS", "EMR",
        "TRV", "PH", "HCA", "AEP", "KLAC", "AZO", "IDXX", "CDNS", "WELL", "ROST",
        "AIG", "SRE", "CTAS", "ROP", "ANET", "WMB", "LRCX", "OXY", "PRU", "ED",
        "FTNT", "PAYX", "CMG", "DLR", "F", "TEL", "EOG", "PCAR", "WEC", "OTIS",
        "MPC", "MSI", "IQV", "SPG", "XEL", "HLT", "SYY", "AMP", "STZ", "PPG",
        "BK", "ALL", "GWW", "RMD", "MTD", "AME", "NOC", "DOW", "CHTR", "NEM",
        "FAST", "RSG", "DXCM", "GILD", "EBAY", "VLO", "AFL", "PSX", "ETN", "KMI",
        "WBA", "LEN", "DFS", "WST", "TT", "FANG", "YUM", "HES", "KEYS", "NUE",
        "HPQ", "EXC", "HIG", "O", "DHI", "ES", "KR", "GLW", "MSCI", "MTB",
        "AJG", "MLM", "CBRE", "VICI", "CNC", "STT", "WAT", "FTV", "ENPH", "IR",
        "ZBH", "ALGN", "EFX", "EL", "LDOS", "CDW", "PWR", "LHX", "EIX", "PEG",
        "ANSS", "BR", "BALL", "TYL", "CHD", "CNP", "DTE", "RJF", "CTSH", "STE",
        "KHC", "WY", "ARE", "WAB", "VRSK", "HOLX", "NTAP", "MAA", "CMS", "VMC",
        "IT", "GRMN", "FICO", "MKC", "TSCO", "AVB", "BAX", "BBY", "XYL", "CINF",
        "AEE", "BIO", "TER", "URI", "CTVA", "EXR", "NDAQ", "LKQ", "FE", "RF",
        "COO", "INVH", "MPWR", "GNRC", "BKR", "TRGP", "HPE", "FDS", "EPAM", "CAG",
        "DG", "MCK", "K", "HBAN", "ON", "ETR", "STX", "J", "ODFL", "WDC",
        "LUV", "PFG", "CEG", "MTCH", "JCI", "TROW", "CLX", "D"
    ]

    start_input = input("Enter start date (YYYY-MM-DD): ")
    end_input = input("Enter end date (YYYY-MM-DD): ")

    try:
        start_date = validate_date(start_input).strftime('%Y-%m-%d')
        end_date = validate_date(end_input).strftime('%Y-%m-%d')
        analyze_stocks(start_date, end_date)

        while True:
            choice = (input("Choose mode: 1 - connected stocks, 2 - correlation between two stocks, exit - quit: ")
                      .strip().lower())
            if choice == 'exit':
                break
            elif choice == '1':
                user_stock = (input("Enter a stock symbol to see its connected stocks in the same community: ")
                              .strip().upper())
                connected = get_connected_stocks_in_community(user_stock)
                print(f"Connected stocks in the same community as {user_stock}: "
                      f"{connected if connected else 'None or not found'}")
            elif choice == '2':
                stock1 = input("Enter the first stock symbol: ").strip().upper()
                stock2 = input("Enter the second stock symbol: ").strip().upper()
                corr_value = get_correlation_between(stock1, stock2)
                if corr_value is not None:
                    print(f"Correlation between {stock1} and {stock2}: {corr_value:.4f}")
            else:
                print("Invalid choice. Please try again.")

    except ValueError as e:
        print(e)
