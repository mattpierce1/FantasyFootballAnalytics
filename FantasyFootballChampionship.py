import pandas
import numpy
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as plio
import seaborn


# Function to Quickly Build Data Frames
def dataBuilder(df, newColumns):
    df = df[['Player', 'Tm', 'Age', 'G'] + newColumns + ['FL']]
    return df


# Calculating touches per game for Receivers and Running Backs, tight ends is defined as only receptions
def touchesCalculator(df):
    touchesPerGame = (df['RushingAttempt'] + df['Targets'])/df['G']
    touchesPerGame = touchesPerGame.round(2)
    return touchesPerGame


# Calculating Fantasy Points Per Game (ffpg) for Quarterbacks
def fppgQB(df):
    pointsPerGame = (df['PassingYD']*.04 + df['PassingTD']*4 - df['Int']*2 + df['RushingYD']*.1 + df['RushingTD']*6 -
                    df['FL']*2)/df['G']
    return pointsPerGame


# Calculating Fantasy Points Per Game (ffpg) for Running Backs and Receivers
def fppgR(df):
    pointsPerGame = (df['ReceivingYD']*.1 + df['ReceivingTD']*6 + df['Receptions']*.5 + df['RushingYD']*.1 +
                    df['RushingTD']*6 - df['FL']*2)/df['G']
    return pointsPerGame


# Calculating Fantasy Points Per Game (ffpg) for Tight Ends
def fppgTE(df):
    pointsPerGame = (df['ReceivingYD']*.1 + df['ReceivingTD']*6 + df['Receptions']*.5 - df['FL']*2)/df['G']
    return pointsPerGame


# Calculation Touchdowns Per game for Receivers, Running Backs and Tight Ends
def touchdownsPerGameCalculator(df):
    touchdownsPerGame = (df['RushingTD'] + df['ReceivingTD'])/df['G']
    touchdownsPerGame = touchdownsPerGame.round(2)
    return touchdownsPerGame


#Top Players on Each Team
def topPlayersOnTeams(df, n):
    return df.groupby("Tm").apply(lambda x: x.nlargest(n, ['Fantasy Points Per Game']).min()).reset_index(drop=True)

# Importing data from 2019 ProFootballReference
dataImport = pandas.read_csv('2019.csv')

# Dropping Unnecessary Columns
dataImport.drop(['Rk', '2PM', '2PP', 'FantPt', 'DKPt', 'FDPt', 'VBD', 'PosRank', 'OvRank', 'PPR', 'PPR', 'Fmb', 'GS'], axis=1, inplace=True)

# Dropping Players With 4 or Less Games Played
dataImport = dataImport[dataImport['G'] >= 5]

# Formatting
dataImport['Player'] = dataImport['Player'].apply(lambda x: x.split("*")[0]).apply(lambda x: x.split('\\')[0])

# Renaming Columns to Common Terms
dataImport.rename({
    'TD': 'PassingTD', 'TD.1': 'RushingTD', 'TD.2': 'ReceivingTD', 'TD.3': 'TotalTD',
    'Yds': 'PassingYD', 'Yds.1': 'RushingYD', 'Yds.2': 'ReceivingYD', 'Yds.3': 'TotalYD',
    'Att': 'PassingAttempt',  'Att.1': 'RushingAttempt',
    'Tgt': 'Targets', 'Rec': 'Receptions'
}, axis=1, inplace=True)

# Eliminating if they played on multiple teams in a year for simplicity
dataImport = dataImport[dataImport['Tm'] != '2TM']
dataImport = dataImport[dataImport['Tm'] != '3TM']

# Splitting By Position
runningBacks = dataImport[dataImport['FantPos'] == 'RB']
quarterBacks = dataImport[dataImport['FantPos'] == 'QB']
wideReceivers = dataImport[dataImport['FantPos'] == 'WR']
tightEnds = dataImport[dataImport['FantPos'] == 'TE']

# Sorting Columns
rushingColumns = ['RushingYD', 'RushingAttempt', 'Y/A', 'RushingTD']
receivingColumns = ['ReceivingYD', 'Targets', 'Receptions', 'Y/R', 'ReceivingTD']
passingColumns = ['PassingYD', 'PassingAttempt', 'PassingTD', 'Int']

# Creating new dataframes by Position
runningBacks = dataBuilder(runningBacks, rushingColumns+receivingColumns)
wideReceivers = dataBuilder(wideReceivers, rushingColumns+receivingColumns)
quarterBacks = dataBuilder(quarterBacks, passingColumns+rushingColumns)
tightEnds = dataBuilder(tightEnds, receivingColumns)

# Adding Columns to Running Back Data Frame
runningBacks['Usage Per Game'] = touchesCalculator(runningBacks)
runningBacks['Fantasy Points Per Game'] = fppgR(runningBacks)
runningBacks['Touchdowns Per Game'] = touchdownsPerGameCalculator(runningBacks)

# Adding Columns to Wide Receiver Data Frame
wideReceivers['Usage Per Game'] = touchesCalculator(wideReceivers)
wideReceivers['Fantasy Points Per Game'] = fppgR(wideReceivers)
wideReceivers['Touchdowns Per Game'] = touchdownsPerGameCalculator(wideReceivers)

# Adding Columns to Tight End Data Frame
tightEnds['Usage Per Game'] = tightEnds['Receptions']
tightEnds['Fantasy Points Per Game'] = fppgTE(tightEnds)
tightEnds['Touchdowns Per Game'] = tightEnds['ReceivingTD']/tightEnds['G']

# Basic Data Filtering
wideReceivers = wideReceivers[wideReceivers['Receptions'] > 20]
runningBacks = runningBacks[runningBacks['RushingAttempt'] > 20]
tightEnds = tightEnds[tightEnds['Receptions'] > 10]
quarterBacks = quarterBacks[quarterBacks['PassingAttempt'] > 20]

# RUNNING BACKS
# DATA PLOTTING Fantasy Points Per Game vs Usage
# Line of Best Fit
mRBFPPG, bRBFPPG = numpy.polyfit(runningBacks['Usage Per Game'], runningBacks['Fantasy Points Per Game'], 1)
# Creating and Formatting Plot
figRBFPPG = go.Figure()
figRBFPPG.add_trace(go.Scatter(x=runningBacks['Usage Per Game'], y=runningBacks['Fantasy Points Per Game'],
                                mode='markers', name='Running Back Data Points', text=runningBacks['Player']))
figRBFPPG.add_trace(go.Scatter(x=runningBacks['Usage Per Game'], y=mRBFPPG*runningBacks['Usage Per Game'] + bRBFPPG,
                               mode='lines', name='Regression Line'))
figRBFPPG.layout.update(title="Running Back Usage vs Fantasy Points", xaxis_title="Usage Per Game",
                    yaxis_title="Fantasy Points Per Game", showlegend=False)

# DATA PLOTTING Touchdowns Per Game vs Usage
# Line of best fit
mRBTDPG, bRBTDPG = numpy.polyfit(runningBacks['Usage Per Game'], runningBacks['Touchdowns Per Game'], 1)
# Creating anf Formatting Plots
figTDPG = go.Figure()
figTDPG.add_trace(go.Scatter(x=runningBacks['Usage Per Game'], y=runningBacks['Touchdowns Per Game'], mode='markers',
                             name='Running Backs Touchdown vs Usage', text=runningBacks['Player']))
figTDPG.add_trace(go.Scatter(x=runningBacks['Usage Per Game'], y=mRBTDPG*runningBacks['Usage Per Game'] + bRBTDPG,
                             mode='lines', name='Regression Line'))
figTDPG.layout.update(title="Running Back Usage vs Touchdowns Per Game", xaxis_title="Usage Per Game",
                    yaxis_title="Touchdowns Per Game", showlegend=False)

# WIDE RECEIVERS
# DATA Plotting Fantasy Points and Usage Rates
# Line of Best Fit
mWRFPPG, bWRFPPG = numpy.polyfit(wideReceivers['Usage Per Game'], wideReceivers['Fantasy Points Per Game'], 1)
# Creating and Formatting Plot
figWRFPPG = go.Figure()
figWRFPPG.add_trace(go.Scatter(x=wideReceivers['Usage Per Game'], y=wideReceivers['Fantasy Points Per Game'],
                                mode='markers', name='Wide Receiver Data Points', text=wideReceivers['Player']))
figWRFPPG.add_trace(go.Scatter(x=wideReceivers['Usage Per Game'], y=mWRFPPG*wideReceivers['Usage Per Game'] + bWRFPPG,
                               mode='lines', name='Regression Line'))
figWRFPPG.layout.update(title="Wide Receiver Usage vs Fantasy Points", xaxis_title="Usage Per Game",
                    yaxis_title="Fantasy Points Per Game", showlegend=False)

# Heat Map for Stacking PLayers (two players on same team)
# Eliminating if they played on multiple teams in a year for simplicity
dataImportHeat = dataImport[dataImport['Tm'] != '2TM']
dataImportHeat = dataImport[dataImport['Tm'] != '3TM']

# Adding Column
dataImportHeat.loc[dataImportHeat['FantPos'] == 'QB', 'Fantasy Points Per Game'] = fppgQB(dataImportHeat)
dataImportHeat.loc[dataImportHeat['FantPos'] == 'RB', 'Fantasy Points Per Game'] = fppgR(dataImportHeat)
dataImportHeat.loc[dataImportHeat['FantPos'] == 'WR', 'Fantasy Points Per Game'] = fppgR(dataImportHeat)
dataImportHeat.loc[dataImportHeat['FantPos'] == 'TE', 'Fantasy Points Per Game'] = fppgTE(dataImportHeat)

# Creating new
dataImportHeat = dataImportHeat[['Tm', 'FantPos', 'Fantasy Points Per Game']]

# Splitting By Position Again
runningBacksHeat = dataImportHeat[dataImportHeat['FantPos'] == 'RB']
quarterBacksHeat = dataImportHeat[dataImportHeat['FantPos'] == 'QB']
wideReceiversHeat = dataImportHeat[dataImportHeat['FantPos'] == 'WR']
tightEndsHeat = dataImportHeat[dataImportHeat['FantPos'] == 'TE']

# Splitting PLayers into Position Rank on Team
qb1 = topPlayersOnTeams(quarterBacksHeat, 1)
rb1 = topPlayersOnTeams(runningBacksHeat, 1)
rb2 = topPlayersOnTeams(runningBacksHeat, 2)
wr1 = topPlayersOnTeams(wideReceiversHeat, 1)
wr2 = topPlayersOnTeams(wideReceiversHeat, 2)
wr3 = topPlayersOnTeams(wideReceiversHeat, 3)
te1 = topPlayersOnTeams(tightEndsHeat, 1)

# More Conventional Naming
names = {'QB1': qb1,
         'RB1': rb1, 'RB2': rb2,
         'WR1': wr1, 'WR2': wr2, 'WR3': wr3,
         'TE1': te1
         }

# Renaming and dropping columns
for name, new_df in names.items():
    new_df.rename({'Fantasy Points Per Game': name}, axis=1, inplace=True)
    new_df.drop(['FantPos'], axis=1, inplace=True)
    new_df.set_index('Tm', inplace=True)

# Concatonating everything
dataImportHeat = pandas.concat([qb1, rb1, rb2, wr1, wr2, wr3, te1], axis=1)

# Correlation Matrix
correlationMatrix = dataImportHeat.corr()

# Figure creation from Matrix
figHeatMat = px.imshow(correlationMatrix, color_continuous_scale=px.colors.sequential.ice,
                       labels=dict(x='Position', y='Position', color='Correlation'),
                       x=['QB1', 'RB1', 'RB2', 'WR1', 'WR2', 'WR3', 'TE1'],
                       y=['QB1', 'RB1', 'RB2', 'WR1', 'WR2', 'WR3', 'TE1'])

# Showing all plots
figRBFPPG.show()
figTDPG.show()
figWRFPPG.show()
figHeatMat.show()
