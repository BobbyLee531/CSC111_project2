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
tickers = [
        "AAPL", "AMZN", "GOOGL", "META", "TSLA", "JPM", "WMT", "MA", "PG", "UNH",
        "JNJ", "HD", "XOM", "CVX", "BAC", "PFE", "ABBV", "KO", "PEP", "MRK",
        "AVGO", "TMO", "COST", "DIS", "CSCO", "ABT", "DHR", "ACN", "WFC", "MCD",
        "NKE", "CMCSA", "ADBE", "PM", "TXN", "NFLX", "CRM", "LIN", "BMY", "ORCL",
        "AMD", "INTC", "QCOM", "UNP", "HON", "LOW", "UPS", "SBUX", "RTX", "IBM",
        "MDT", "GS", "CAT", "AMGN", "GE", "BLK", "T", "DE", "PLD", "NOW", "ELV",
        "SYK", "MMM", "GILD", "INTU", "ADI", "ISRG", "AMT", "CB", "SPGI", "SCHW",
        "SO", "CI", "ZTS", "MO", "BSX", "BDX", "PYPL", "APD", "REGN", "CME",
        "ADP", "NEE", "ICE", "EQIX", "SHW", "CL", "ITW", "FIS", "HUM", "PNC",
        "USB", "ETN", "MMC", "AON", "TGT", "CSX", "FDX", "EMR", "NSC", "TJX",
        "COP", "VRTX", "PSA", "AIG", "EW", "ROP", "ECL", "DOW", "KLAC", "SNPS",
        "SRE", "MCO", "IDXX", "CDNS", "ANET", "DXCM", "MCHP", "APH", "ROST",
        "AEP", "WELL", "CTAS", "TDG", "FTNT", "FAST", "MTD", "OKE", "WEC", "PCAR",
        "AME", "VRSK", "TRV", "EXC", "PAYX", "EBAY", "ALGN", "ES", "STZ", "KMB",
        "OTIS", "WAB", "EFX", "BIIB", "DHI", "KEYS", "CHTR", "CEG", "FANG",
        "MSCI", "VLO", "RSG", "WST", "ED", "HCA", "HPQ", "MPWR", "ON", "GPN",
        "CTSH", "WBD", "DAL", "DFS", "VICI", "TT", "IR", "LYV", "GRMN", "ULTA",
        "MTCH", "CZR", "BKR", "XYL", "HRL", "IFF", "WRB", "CPRT", "GL", "LW",
        "NDAQ", "MGM", "EXR", "CF", "HIG", "RCL", "BBWI", "IP", "LVS", "BRO",
        "PKG", "JCI", "SWKS", "POOL", "TECH", "WAT", "AKAM", "UDR", "ETSY",
        "ARE", "STE", "CBOE", "LEN", "EQR", "FITB", "RF", "NTRS", "HBAN", "INCY",
        "HPE", "VMC", "WDC", "APA", "LUV", "BALL", "AES", "KMI", "DG", "WY",
        "DOV", "BR", "HOLX", "AVY", "LDOS", "TSN", "CLX", "MAS", "LKQ", "CINF",
        "TXT", "ROL", "TER", "BWA", "FRT", "CPT", "JNPR", "KMX", "PFG", "DRI",
        "AIZ", "UHS", "HWM", "PNW", "TFC", "AAL", "L", "BEN", "IVZ", "EMN",
        "RHI", "FMC", "NCLH", "PNR", "TPR", "NWSA", "FOXA", "PARA", "LNC",
        "NWL", "VTR", "HST", "VTRS", "FFIV", "HII", "RL", "JAZZ", "WHR", "LEG",
        "IPG", "ALK", "TPX", "BHF", "AAP", "TREX", "SEE", "OGN", "DXC", "NOV",
        "ZBRA", "HAS", "MHK", "PVH", "FOX", "CAR", "GT", "MOS", "VNO",
        "WU", "DVA", "UAA", "UA", "XRX", "NYT", "IRM", "KSS", "M", "AMCR",
        "CNP", "NI", "SLG", "JWN", "AOS", "CMA", "FHN", "REG", "AGNC", "PMT",
        "RRC", "HRB", "LEVI", "KIM", "CPB", "HSY", "COTY", "HBI", "ANF",
        "URBN", "LB", "CHRW", "EXPD", "JBHT", "LSTR", "ODFL", "SAIA", "SNDR",
        "KNX", "ARCB", "HUBG", "WERN", "MRTN", "POWI", "ICUI", "ITGR", "PENN",
        "BYD", "CHDN", "PLAY", "EPR", "AMC", "CNK", "IMAX", "JBLU", "SNCY",
        "ALGT", "ATSG", "MAT", "JAKK", "PLNT", "PTON", "SCHL", "LRN", "STRA",
        "APEI", "LAUR", "GHC", "CHGG", "TAL", "EDU", "VSTA", "LOPE", "GWRE",
        "TWLO", "ZS", "CRWD", "OKTA", "PANW", "NET", "CYBR", "QLYS", "TENB",
        "SAIC", "BAH", "CACI", "KBR", "FLR", "J", "PWR", "ACM", "DY", "PRIM",
        "APG", "GVA", "STN", "TRC", "TNET", "AGX", "ASGN", "KFRC", "RCMT",
        "HSII", "KELYA", "KELYB", "LXRX", "MEI", "MLAB", "MOD", "NATH", "NRC",
        "NSYS", "NVEC", "NVEE", "NVT", "OB", "OIS", "OMCL", "OMER", "ONTO",
        "OPY", "ORGO", "OSIS", "OTEX", "PAHC", "PETS", "QNST", "QUAD", "RAMP",
        "RBCAA", "RDNT", "RELL", "RES", "RGCO", "RICK", "RMBI", "RMR", "RNST",
        "ROIC", "SASR", "SAVA", "SBCF", "SBFG", "SBGI", "SBLK", "SBNY", "SBSI",
        "SCSC", "SCVL", "SENEA", "SENEB", "SFBC", "SFST", "SGC", "SGMA", "SHBI",
        "SHEN", "SHLS", "SHOO", "SIGA", "SIGI", "SILC", "SLM", "SLP", "SMBC",
        "SMPL", "SNBR", "SNCR", "SONM", "SPFI", "SPRO", "SPSC", "SPTN", "SPWH",
        "SSB", "SSP", "SSSS", "STBA", "STKL", "STLD", "SUPN",
        "SVRA", "SWBI", "SWKH", "SXC", "SXI", "SYBT", "TCBK", "TCX", "TDS",
        "TFSL", "THFF", "TIPT", "TMP", "TOWN", "TPB", "TRST", "TRUP", "TSBK",
        "TTMI", "UBCP", "UBFO", "UBOH", "UBSI", "UEIC", "UFCS", "UFPI", "UFPT",
        "UHAL", "ULBI", "UMBF", "UNB", "UNTY", "UVSP", "VBTX", "VC", "VICR",
        "VNDA", "VPG", "VREX", "VRTS", "VSAT", "WABC", "WWD", "WYNN", "XBIO",
        "XENE", "XERS", "XFOR", "XGN", "XNCR", "XOMA", "XPER", "XPL", "YORW",
        "ZION", "ZUMZ", "ZYXI"
    ]

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
