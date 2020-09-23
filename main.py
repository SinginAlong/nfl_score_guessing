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

    output_file(plot_file)

    plot_tools = "hover,pan,wheel_zoom,zoom_in,zoom_out,undo,redo,reset,tap,save,box_select,poly_select,lasso_select,"
    p = figure(
        tools=plot_tools,
        plot_width=7,
        plot_height=3,
        match_aspect=True,
        x_axis_label="Home",
        y_axis_label="Away",
    )
    p.add_tools(BoxZoomTool(match_aspect=True))
    p.sizing_mode = "scale_width"
    p.x_range = Range1d(0, max([df['AwayResult'].max(), df['AAwayGuess'].max(), df['BAwayGuess'].max()])+5)
    p.y_range = Range1d(0, max([df['HomeResult'].max(), df['AHomeGuess'].max(), df['BHomeGuess'].max()]) + 5)

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
    ), code="""
        var f = cb_obj.value;  // this should be the column selection
        sc.data['AwayResult']=[]
        sc.data['HomeResult']=[]
        sc.data['AAwayGuess']=[]
        sc.data['AHomeGuess']=[]
        sc.data['BAwayGuess']=[]
        sc.data['BHomeGuess']=[]
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
        sc.change.emit();
        """)

    # drop down menu
    menu = Select(options=list(df['Game']), value=list(df['Game'])[0], title='Game')
    menu.js_on_change('value', p_callback)

    # show(p)
    show(layout(column(p, menu), sizing_mode='scale_width'))



week2 = load("Week2.csv")

plot(week2)

print("done")
