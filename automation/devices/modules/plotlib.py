# encoding: utf-8
#
# Created on 5 févr. 2019
#
# @author: denis
#import re
#import collections
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import plotly.graph_objs as go
from plotly.offline import plot

#######################################
## plotly
#
class ScatterPlotConf:
    RANGE_SELECTOR = [1, 2, 3, 4, 5, 6, 7, 15, 30, 60, 90, 180] if not settings.RANGE_SELECTOR else settings.RANGE_SELECTOR
    LANGUAGE_CODE = 'en-US' if not settings.LANGUAGE_CODE else settings.LANGUAGE_CODE


    def plot_config(self, modebar=True, bbtn_rem=[]):
        #'modeBarButtonsToRemove': ['sendDataToCloud','toImage','autoScale2d','zoom2d', 'pan','pan2d','lasso2d','resetScale2d','hoverClosestCartesian','hoverCompareCartesian']
        return dict(
            displaylogo=False,
            displayModeBar=modebar,
            locale=self.LANGUAGE_CODE,
            modeBarButtonsToRemove=bbtn_rem,
        )

    def range_selector(self, intervals=RANGE_SELECTOR, bgcolor='LightSlateGray'):
        buttons = []
        step_label = str(_('d'))
        end_label = str(_('All'))
        for i in intervals:
            buttons.append(
                dict(count=i,
                    label='%s %s'% (i, step_label),
                    step='day',
                    stepmode='backward')
            )
        buttons.append(dict(step='all', label=end_label))
        return dict(bgcolor=bgcolor, buttons=buttons)

    def grid_conf(self, gridcolor='DimGray', zerolinecolor='Magenta', linecolor='SeaGreen'):
        return dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=gridcolor,

            zeroline=False,
            zerolinewidth=2,

            zerolinecolor=zerolinecolor,
            showline=True,
            linewidth=2,

            linecolor=linecolor,
            automargin=True,
            autorange=True,
        )

    def notation_conf(self, texts, colors, x=0, y=0):
        notes = []
        i=0
        for text in texts:
            notes.append(
                dict(
                    x=x,
                    y=y,
                    showarrow=False,
                    text=text,
                    xref='paper',
                    yref='paper',
                    font=dict(family='Courier New, monospace', size=16, color=colors[i]),
                ),
            )
            i+=1
        return notes


class ScatterPlot(ScatterPlotConf):

    def __init__(self, **params):
        super().__init__()
        self.title = params.get('title')
        self.xtitle = params.get('xtitle')
        self.slider = params.get('slider')
        self.rangeselector = self.range_selector() if params.get('range_selector') else None

    def simple_figure(self, df, figures=[], mode='lines+markers', interpolation='linear'):
        try:
            if df.empty:
                raise Exception('No datas for plotting')
            data = []
            notes = []
            colors = []
            anotation_colors = []
            for figure in figures:
                f, label, unit, color, anotation_color, gaps = figure

                colors.append(color)
                anotation_colors.append(anotation_color)
                notes.append('min:%.1f%s - max:%.1f%s - moy:%.1f%s'% (df[f].min(), unit, df[f].max(), unit, df[f].mean(), unit))
                data.append(go.Scatter(
                    x=df.index,
                    y=df[f],
                    mode=mode,
                    name=label,
                    opacity=0.8,
                    line=dict(color=color),
                    connectgaps=gaps,
                    line_shape=interpolation,
                    )
                )
            layout = go.Layout(
                xaxis=dict(
                    title=self.xtitle,
                    titlefont=dict(size=18),
                    rangeselector= self.rangeselector,
                    rangeslider=dict(visible=self.slider),
                    type='date',
                    **self.grid_conf(),
                ),
                yaxis=dict(
                    title='%s %s'% (label, unit),
                    titlefont=dict(size=18),
                    type='linear',
                    **self.grid_conf(),
                ),
                autosize=True,
                plot_bgcolor= '#111111',
                paper_bgcolor='#333333',
                font= { 'color': 'LightGreen'},
                margin={'l': 40, 'b': 40, 't': 10, 'r': 10, 'pad':4},
                legend={'x': 1, 'y': 1},
                hovermode='closest',
            )
            figure = dict(data=data, layout=layout)
            if not figure:
                raise Exception('No figure for plotting')
            graph = plot(figure, output_type='div', include_plotlyjs=False, config=self.plot_config())

            return graph

        except Exception as e:
            print("ScatterPlot::simple_figure error >>", e, flush=True)
            return  {}


#
