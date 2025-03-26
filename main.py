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
        "AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA", "JPM", "V",
        "WMT", "MA", "PG", "UNH", "JNJ", "HD", "XOM", "CVX", "BAC", "PFE",
        "ABBV", "KO", "PEP", "MRK", "AVGO", "TMO", "COST", "DIS", "CSCO", "ABT",
        "DHR", "ACN", "WFC", "MCD", "VZ", "NKE", "CMCSA", "ADBE", "PM", "TXN",
        "NFLX", "CRM", "LIN", "BMY", "ORCL", "AMD", "INTC", "QCOM", "UNP", "HON",
        "LOW", "UPS", "SBUX", "RTX", "IBM", "MDT", "GS", "CAT", "AMGN", "GE",
        "BLK", "T", "DE", "PLD", "NOW", "LMT", "ELV", "SYK", "MMM", "GILD",
        "INTU", "ADI", "ISRG", "AMT", "CB", "SPGI", "SCHW", "DUK", "SO", "CI",
        "ZTS", "MO", "BSX", "BDX", "PYPL", "APD", "REGN", "CME", "ADP", "NEE",
        "ICE", "EQIX", "SHW", "CL", "ITW", "FIS", "HUM", "PNC", "USB", "ETN",
        "MMC", "AON", "TGT", "CSX", "FDX", "EMR", "NSC", "TJX", "COP", "VRTX",
        "PSA", "AIG", "EW", "ROP", "ECL", "DOW", "KLAC", "SNPS", "SRE", "MCO",
        "IDXX", "CDNS", "ANET", "DXCM", "MCHP", "APH", "ROST", "AEP", "WELL", "CTAS",
        "TDG", "FTNT", "FAST", "MTD", "OKE", "WEC", "PCAR", "AME", "VRSK", "TRV",
        "EXC", "PAYX", "EBAY", "ALGN", "ES", "STZ", "KMB", "OTIS", "WAB", "EFX",
        "BIIB", "DHI", "KEYS", "CHTR", "CEG", "FANG", "MSCI", "VLO", "RSG", "WST",
        "ED", "NEM", "HCA", "HPQ", "MPWR", "ON", "GPN", "CTSH", "WBD", "DAL",
        "DFS", "VICI", "TT", "IR", "LYV", "GRMN", "ULTA", "MTCH", "CZR", "BKR",
        "XYL", "HRL", "IFF", "PKI", "WRB", "CPRT", "GL", "LW", "NDAQ", "MGM",
        "EXR", "CF", "HIG", "RCL", "BBWI", "IP", "LVS", "BRO", "PKG", "JCI",
        "SWKS", "POOL", "TECH", "BXP", "WAT", "AKAM", "UDR", "ETSY", "MAA", "ARE",
        "STE", "CBOE", "LEN", "EQR", "FITB", "RF", "NTRS", "HBAN", "INCY", "HPE",
        "CMS", "VMC", "WDC", "KEY", "TAP", "APA", "LUV", "BALL", "AES", "KMI",
        "DG", "CFG", "WY", "DOV", "BR", "HOLX", "AVY", "LDOS", "TSN", "CLX",
        "MAS", "LKQ", "CINF", "TXT", "ROL", "TER", "BWA", "FRT", "CPT", "JNPR",
        "KMX", "PFG", "MRO", "DRI", "AIZ", "SNA", "UHS", "HWM", "PNW", "TFC",
        "AAL", "L", "BEN", "IVZ", "EMN", "RHI", "FMC", "NCLH", "PNR", "TPR",
        "NWSA", "FOXA", "PARA", "DISH", "LNC", "NWL", "VTR", "HST", "PEAK",
        "VTRS", "FFIV", "HII", "RL", "JAZZ", "WHR", "LEG", "IPG", "ALK", "TPX",
        "BHF", "AAP", "TREX", "SEE", "ROL", "OGN", "TAP", "DXC", "NOV", "LUMN",
        "ZBRA", "HAS", "MHK", "PVH", "CCL", "RLGY", "FOX", "BF.B", "NWSA", "NWS",
        "CAR", "GT", "MOS", "VNO", "BXP", "WU", "COG", "DVA", "UAA",
        "UA", "XRX", "NYT", "GPS", "DISH", "IRM", "KSS", "M", "AMCR", "RRR",
        "CNP", "NI", "BLL", "FRC", "SLG", "JWN", "AOS", "CMA", "FHN", "PBCT",
        "REG", "AGNC", "NLY", "PMT", "RRC", "VNO", "HRB", "TSN", "BF.B", "WHR",
        "LEVI", "KIM", "CPB", "HSY", "COTY", "PVH", "HBI", "KSS", "M", "JWN",
        "GPS", "ANF", "URBN", "RL", "LB", "CHRW", "EXPD", "JBHT", "LSTR", "ODFL",
        "SAIA", "SNDR", "KNX", "ARCB", "HUBG", "WERN", "MRTN", "POWI", "SWAV", "ICUI",
        "ITGR", "PENN", "BYD", "CHDN", "PLAY", "RRR", "FUN", "SEAS", "EPR",
        "AMC", "CNK", "IMAX", "MGM", "PENN", "RCL", "NCLH", "CCL", "AAL", "DAL",
        "LUV", "UAL", "ALK", "JBLU", "SAVE", "SNCY", "SKYW", "ALGT", "ATSG",
        "MAT", "JAKK", "FUN", "PLNT", "PTON", "NLS", "SCHL", "LRN", "STRA",
        "APEI", "LAUR", "GHC", "CHGG", "TAL", "EDU", "VSTA", "LOPE", "GWRE", "TWLO",
        "ZS", "CRWD", "OKTA", "PANW", "NET", "FTNT", "CYBR", "QLYS", "TENB", "SAIC",
        "LDOS", "BAH", "CACI", "PSN", "KBR", "FLR", "J", "PWR", "ACM", "DY",
        "PRIM", "APG", "GVA", "STN", "TRC", "TNET", "AGX", "ASGN", "KFRC", "RCMT",
        "HAYN", "HSII", "KELYA", "KELYB", "LAIX", "LXRX", "MEI", "MLAB", "MOD", "MOG.A",
        "MOG.B", "NATH", "NRC", "NSYS", "NVEC", "NVEE", "NVT", "OB", "OIS", "OMCL",
        "OMER", "ONTO", "OPY", "ORGO", "OSIS", "OSTK", "OTEX", "PAHC", "PETS", "PFMT",
        "PGTI", "PHUN", "PKBK", "PLAB", "PLCE", "PLPC", "PLPM", "PLXS", "POWL", "PRAA",
        "PRDO", "PRTH", "PTEN", "PTSI", "PUMP", "QADA", "QADB", "QCRH", "QNST", "QUAD",
        "RADA", "RAMP", "RBCAA", "RCII", "RDNT", "RELL", "RES", "REXI", "RGCO", "RICK",
        "RMBI", "RMR", "RNET", "RNST", "ROIC", "RUSHA", "RUSHB", "SASR", "SAVA",
        "SBCF", "SBFG", "SBGI", "SBLK", "SBNY", "SBSI", "SCSC", "SCVL", "SENEA", "SENEB",
        "SFBC", "SFST", "SGC", "SGMA", "SHBI", "SHEN", "SHLS", "SHOO", "SIGA", "SIGI",
        "SILC", "SIX", "SKYW", "SLM", "SLP", "SMBC", "SMMF", "SMPL", "SNBR", "SNCR",
        "SONM", "SP", "SPFI", "SPKE", "SPOK", "SPRO", "SPSC", "SPTN", "SPWH",
        "SQBG", "SRLP", "SSB", "SSP", "SSSS", "STBA", "STCN", "STKL", "STLD", "STRA",
        "STXB", "SUPN", "SVC", "SVRA", "SWBI", "SWKH", "SXC", "SXI", "SYBT", "SYKE",
        "TAST", "TBBK", "TBI", "TCBK", "TCX", "TDS", "TESS", "TFSL", "TGH", "THFF",
        "TIPT", "TITN", "TMP", "TOWN", "TPB", "TRST", "TRUP", "TSBK", "TTMI", "TUSK",
        "UBCP", "UBFO", "UBNK", "UBOH", "UBSI", "UCBI", "UEIC", "UFCS", "UFPI",
        "UFPT", "UG", "UHAL", "ULBI", "UMBF", "UNB", "UNTY", "UVSP", "VBTX", "VC",
        "VCRA", "VCTR", "VECO", "VICR", "VIRT", "VLY", "VNDA", "VPG", "VRA",
        "VREX", "VRTS", "VSAT", "VSEC", "VSH", "WABC", "WAFD", "WASH", "WBS", "WDFC",
        "WERN", "WETF", "WEYS", "WFD", "WINA", "WING", "WIRE", "WRLD", "WSBC", "WSBF",
        "WSC", "WTBA", "WTFC", "WTI", "WTS", "WVE", "WVFC", "WW", "WWD", "WYNN",
        "XBIO", "XENE", "XERS", "XFOR", "XGN", "XLRN", "XNCR", "XOMA", "XPER", "XPL",
        "YORW", "YRCW", "ZION", "ZUMZ", "ZYXI"
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
