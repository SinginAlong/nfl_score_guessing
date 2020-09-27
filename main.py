"""
    NFL Score Guessing
    This is not a guesser, simply using this to see if there is a better way to make guesses based on pure math.
    I also want to develop a plotter for each of the games.

"""
import pandas as pd
from bokeh.plotting import figure, output_file, show
from bokeh.models.mappers import LinearColorMapper
from bokeh.models import ColumnDataSource, ColorBar, BoxZoomTool, HoverTool, Select, CustomJS, Range1d
from bokeh.layouts import layout, column
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral3

# things that need to be done
# load data
# clean data?
# plot data

def load(file):
    """
    loads csv file of score guesses and results
    :param file:
    :return:
    """

    df = pd.read_csv(file)
    df.columns = ["AwayTeam", "HomeTeam", "AwayResult", "HomeResult",
                  "SumPt", "Winner", "ABWinner",
                  "AAwayGuess", "AHomeGuess", "ASumPts", "AOffby", "AWinner",
                  "BAwayGuess", "BHomeGuess", "BSumPts", "BOffby", "BWinner"]
    df['Game'] = [a + " at " + h for a,h in zip(df['AwayTeam'], df['HomeTeam'])]
    return df


def plot(df, plot_file="plot.html", ais="Carter", bis="Kyle"):
    """
    takes in a df that includes scores, cart's guess, and Kyle's guess for away and home teams
    plots (x - away, y - home) and draws a line for the final score
    must handle having or not having results score
    :param df:
    :return:
    """

    # TODO:
    #   show who won
    #   say what dot is who
    #   plot line
    #   scale bounds to match score?
    #   display score
    #   plot game win line
    #   add title
    #   make better hover

    '''
    def x_point(x1, x2):
        return (x2 - x1) / 2 + x1

    def y_point(y1, y2):
        return (y2 - y1) / 2 + y1

    def div_slope(x1, y1, x2, y2):  # m
        return -1 * (x2 - x1) / (y2 - y1)

    def mid_point(x1, y1, x2, y2):
        # mx - y
        return div_slope(x1, y1, x2, y2) * x_point(x1, x2) - y_point(y1, y2)

    div_lines = pd.DataFrame()
    div_lines['Game'] = df['Game']
    div_lines['m'] = div_slope(df['AAwayGuess'].values,
                               df['AHomeGuess'].values,
                               df['BAwayGuess'].values,
                               df['BHomeGuess'].values)
    '''

    output_file(plot_file)

    plot_tools = "hover,pan,wheel_zoom,zoom_in,zoom_out,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
    p = figure(
        tools=plot_tools,
        plot_width=7,
        plot_height=3,
        match_aspect=True,
        x_axis_label="Away",
        y_axis_label="Home",
    )
    p.add_tools(BoxZoomTool(match_aspect=True))
    p.sizing_mode = "scale_width"
    max_away = max([df['AwayResult'].max(), df['AAwayGuess'].max(), df['BAwayGuess'].max()])
    max_home = max([df['HomeResult'].max(), df['AHomeGuess'].max(), df['BHomeGuess'].max()])
    p.x_range = Range1d(0, max_away + 5)
    p.y_range = Range1d(0, max_home + 5)

    dareas = dict()
    curr_dareas = dict()
    target_game = df['Game'].iloc[0]
    for aag, ahg, bag, bhg, game in zip(df['AAwayGuess'], df['AHomeGuess'], df['BAwayGuess'], df['BHomeGuess'], df['Game']):
        for x in range(max_away):
            for y in range(max_home):
                if abs(x-aag) + abs(y-ahg) < abs(x-bag) + abs(y-bhg):
                    w = 'A'
                elif abs(x-aag) + abs(y-ahg) > abs(x-bag) + abs(y-bhg):
                    w = 'B'
                else:
                    w = 'Tie'
                dareas['xs'] = dareas.get('xs', []) + [[x-0.5, x-0.5, x+0.5, x+0.5]]
                dareas['ys'] = dareas.get('ys', []) + [[y-0.5, y+0.5, y+0.5, y-0.5]]
                dareas['game'] = dareas.get('game', []) + [game]
                dareas['winner'] = dareas.get('winner', []) + [w]

                if game == target_game:
                    curr_dareas['xs'] = curr_dareas.get('xs', []) + [[x-0.5, x-0.5, x+0.5, x+0.5]]
                    curr_dareas['ys'] = curr_dareas.get('ys', []) + [[y-0.5, y+0.5, y+0.5, y-0.5]]
                    curr_dareas['game'] = curr_dareas.get('game', []) + [game]
                    curr_dareas['winner'] = curr_dareas.get('winner', []) + [w]

    patch_color_map = factor_cmap('winner', palette=Spectral3, factors=['A', 'B', 'Tie'])
    p_areas = ColumnDataSource(dareas)
    curr_areas = ColumnDataSource(curr_dareas)
    p.patches('xs', 'ys', source=curr_areas, color=patch_color_map)

    # ColumnDataSource(df)
    data = ColumnDataSource(df)
    curr = ColumnDataSource(df[df['Game'] == df['Game'].iloc[0]])  # select to game
    # gonna go simple first
    p.scatter("AwayResult", "HomeResult", source=curr, color="Black", radius=0.5)
    p.scatter("AAwayGuess", "AHomeGuess", source=curr, color="Orange", radius=0.5)
    p.scatter("BAwayGuess", "BHomeGuess", source=curr, color="Teal", radius=0.5)

    p_callback = CustomJS(args=dict(
        source=data,
        sc=curr,
        p_sc=p_areas,
        p_curr=curr_areas,
    ), code="""
        var f = cb_obj.value;  // this should be the column selection
        sc.data['AwayResult']=[]
        sc.data['HomeResult']=[]
        sc.data['AAwayGuess']=[]
        sc.data['AHomeGuess']=[]
        sc.data['BAwayGuess']=[]
        sc.data['BHomeGuess']=[]
        p_curr.data['xs'] = []
        p_curr.data['ys'] = []
        p_curr.data['winner'] = []
        for(var i = 0; i <= source.get_length(); i++){
	        if (source.data['Game'][i] == f){
		        sc.data['AwayResult'].push(source.data['AwayResult'][i])
		        sc.data['HomeResult'].push(source.data['HomeResult'][i])
		        sc.data['AAwayGuess'].push(source.data['AAwayGuess'][i])
		        sc.data['AHomeGuess'].push(source.data['AHomeGuess'][i])
		        sc.data['BAwayGuess'].push(source.data['BAwayGuess'][i])
		        sc.data['BHomeGuess'].push(source.data['BHomeGuess'][i])
	        }
        }
        for( var i = 0; i <= p_sc.get_length(); i++){
            if(p_sc.data['game'][i] == f) {
                p_curr.data['xs'] = p_sc.data['xs']
                p_curr.data['ys'] = p_sc.data['ys']
                p_curr.data['winner'] = p_sc.data['winner']
            }
        }
        sc.change.emit();
        p_curr.change.emit();
        """)

    # drop down menu
    menu = Select(options=list(df['Game']), value=list(df['Game'])[0], title='Game')
    menu.js_on_change('value', p_callback)

    # show(p)
    show(layout(column(p, menu), sizing_mode='scale_width'))



week2 = load("Week2.csv")

plot(week2)

print("done")
