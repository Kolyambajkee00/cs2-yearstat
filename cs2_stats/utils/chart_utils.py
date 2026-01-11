# cs2_stats/utils/chart_utils.py
import plotly.graph_objects as go
import plotly.offline as opy


def create_kd_chart(monthly_stats):
    """Создать график K/D ratio"""
    months = [f"{stat.year}/{stat.month}" for stat in monthly_stats]
    kd_ratios = [stat.kd_ratio for stat in monthly_stats]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=kd_ratios,
        mode='lines+markers',
        name='K/D Ratio',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title='K/D Ratio Over Time',
        xaxis_title='Month',
        yaxis_title='K/D Ratio',
        template='plotly_white',
        height=400
    )

    return opy.plot(fig, auto_open=False, output_type='div')


def create_winrate_chart(monthly_stats):
    """Создать график Win Rate"""
    months = [f"{stat.year}/{stat.month}" for stat in monthly_stats]
    win_rates = [stat.win_rate for stat in monthly_stats]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months,
        y=win_rates,
        name='Win Rate %',
        marker_color='#2ecc71'
    ))

    fig.update_layout(
        title='Win Rate Over Time',
        xaxis_title='Month',
        yaxis_title='Win Rate %',
        template='plotly_white',
        height=400
    )

    return opy.plot(fig, auto_open=False, output_type='div')


def create_matches_chart(monthly_stats):
    """Создать график сыгранных матчей"""
    months = [f"{stat.year}/{stat.month}" for stat in monthly_stats]
    matches = [stat.matches_played for stat in monthly_stats]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=matches,
        mode='lines+markers',
        name='Matches Played',
        fill='tozeroy',
        line=dict(color='#9b59b6', width=3),
        marker=dict(size=10)
    ))

    fig.update_layout(
        title='Matches Played Per Month',
        xaxis_title='Month',
        yaxis_title='Number of Matches',
        template='plotly_white',
        height=400
    )

    return opy.plot(fig, auto_open=False, output_type='div')


def calculate_total_stats(monthly_stats):
    """Рассчитать общую статистику"""
    total = {
        'matches': sum(stat.matches_played for stat in monthly_stats),
        'kills': sum(stat.kills for stat in monthly_stats),
        'deaths': sum(stat.deaths for stat in monthly_stats),
        'wins': sum(stat.wins for stat in monthly_stats),
    }

    if total['deaths'] > 0:
        total['kd'] = round(total['kills'] / total['deaths'], 2)
    else:
        total['kd'] = 0

    if total['matches'] > 0:
        total['win_rate'] = round((total['wins'] / total['matches']) * 100, 1)
    else:
        total['win_rate'] = 0

    return total


def prepare_all_charts(monthly_stats):
    """Создать все графики"""
    if not monthly_stats:
        return []

    charts = []
    charts.append(('📈 K/D Ratio Over Time', create_kd_chart(monthly_stats)))
    charts.append(('✅ Win Rate Over Time', create_winrate_chart(monthly_stats)))
    charts.append(('🎮 Matches Played', create_matches_chart(monthly_stats)))

    return charts