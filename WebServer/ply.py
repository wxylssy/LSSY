from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.io as pio
from plotly import graph_objs as go
from plotly.subplots import make_subplots

pio.templates.default = "plotly_dark"

def write_html_tol(fpath, df_sell, trade_tol_yl, max_huice, annualized, sharperatio):
    if len(df_sell) == 0:
        return
    m_data = df_sell[len(df_sell) - 1]
    datetime_x = [d['datetime'] for d in df_sell]
    datediff = relativedelta(m_data['datetime'], df_sell[0]['datetime'])
    datediff = "历经{}年{}个月{}天".format(datediff.years, datediff.months, datediff.days)
    labels = ["盈利", "亏损"]
    trade_days = len(df_sell)
    trade_ex_sz = m_data['ex_sz_count']
    trade_ex_xd = m_data['ex_xd_count']
    trade_num = m_data['ex_sell_count']
    fig = make_subplots(rows=3, cols=2,
                        row_heights=[0.5, 0.3, 0.2],
                        shared_xaxes=True,
                        vertical_spacing=0.1,
                        specs=[[{'type': 'xy', 'colspan': 2}, None],
                               [{'type': 'xy', 'colspan': 2}, None],
                                [{'type': 'domain'}, {'type': 'domain'}],
                               ],
                        subplot_titles=['收益（{:.2f}%）'.format(trade_tol_yl),
                                        '每日明细（{}）'.format(datediff),
                                        '次数（{})'.format(trade_num),
                                        '天数（{}）'.format(trade_days),
                                        ])
    fig.add_trace(
        go.Scatter(x=datetime_x, y=[d['zc'] for d in df_sell], mode='lines+markers', name="资金"),
        1, 1)
    #fig.add_trace(
    #    go.Scatter(x=datetime_x, y=[d['day_sj_zdf_count'] for d in df_sell], mode='markers', name="每日明细"),
    #    2, 1)
    fig.add_trace(
        go.Pie(labels=labels, values=[trade_ex_sz, trade_ex_xd], hole=.3, textinfo='label+percent+value', name='交易次数'),
        3, 1)
    fig.add_trace(
        go.Pie(labels=labels, values=[m_data['day_sz_count'], m_data['day_xd_count']], hole=.3, textinfo='label+percent+value', name='交易天数'),
        3, 2)
    fig.update_layout(showlegend=False, height=1000, title_text='总收益：{:.2f}% 最大回测：{:.2f}% 年化收益率：{:.2f}% 夏普率：{:.2f}'.format(trade_tol_yl, max_huice, annualized, sharperatio))
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightPink')
    fig.write_html(fpath, full_html=False)

def write_html_one(fpath, df, one_drs, code):
    df['date'] = pd.to_datetime(df['date'])
    name = df.iloc[len(df) - 1]["name"]
    # 买卖标记
    annotations = []
    zdfs = []
    dates_sell = []
    for dr in one_drs:
        s_date = datetime.strptime(dr.sellDate, "%Y%m%d")
        b_date = datetime.strptime(dr.buyDate, "%Y%m%d")
        zdfs.append(dr.zdf)
        dates_sell.append(s_date)
        annotations.append(go.layout.Annotation(
            x=b_date,
            y=dr.buyPrice,
            xref="x",
            yref="y",
            text="买",
            showarrow=True,
            arrowcolor="#ff7f0e",
            font=dict(
                color="#ff7f0e"
            ),
            arrowhead=6,
            ax=0,
            ay=-40
        ))
        annotations.append(go.layout.Annotation(
            x=s_date,
            y=dr.sellPrice,
            xref="x",
            yref="y",
            text="卖",
            showarrow=True,
            arrowcolor="red",
            font=dict(
                color="red"
            ),
            arrowhead=6,
            ax=0,
            ay=-40
        ))
    # 除权标记
    last_xdxr = -1
    for row in df.itertuples():
        xdxr = getattr(row, "xdxr")
        if xdxr != last_xdxr:
            annotations.append(go.layout.Annotation(
                x=getattr(row, "date"),
                y=getattr(row, "low"),
                xref="x",
                yref="y",
                text="除权除息",
                showarrow=True,
                arrowcolor="#ff7f0e",
                font=dict(
                    color="#ff7f0e"
                ),
                arrowhead=6,
                ax=0,
                ay=40
            ))
        last_xdxr = xdxr

    fig = make_subplots(rows=4, cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.06,
                        specs=[[{'type': 'xy'}],
                               [{'type': 'xy'}],
                               [{'type': 'xy'}],
                               [{'type': 'xy'}]],
                        subplot_titles=["", "成交额", "adf", "每日涨跌幅"]
                        )
    fig.add_trace(
        go.Candlestick(x=df["date"], open=df["open"], high=df["high"], low=df["low"], close=df["close"], increasing_line_color="red", decreasing_line_color="green"),
        1, 1)
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["amount"], mode="lines", name="成交额"),
        2, 1)
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["amount_abdr"], mode='lines+markers', name="adf"),
        3, 1)
    fig.add_trace(
        go.Scatter(x=dates_sell, y=zdfs, mode='markers', name="每日涨跌幅"),
        4, 1)

    fig.update_layout(showlegend=False, annotations=annotations, xaxis_rangeslider_visible=False)
    fig.update_yaxes(zeroline=True, zerolinewidth=2, zerolinecolor='LightPink')
    fig.write_html(fpath)
