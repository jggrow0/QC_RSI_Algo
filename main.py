from Execution.ImmediateExecutionModel import ImmediateExecutionModel
from Execution.NullExecutionModel import NullExecutionModel
from Portfolio.EqualWeightingPortfolioConstructionModel import EqualWeightingPortfolioConstructionModel
from Portfolio.NullPortfolioConstructionModel import NullPortfolioConstructionModel
from Risk.MaximumDrawdownPercentPerSecurity import MaximumDrawdownPercentPerSecurity
from Selection.QC500UniverseSelectionModel import QC500UniverseSelectionModel
from RsiAlphaModelJGG import RsiAlphaModelJGG
#from PortfolioModelJGG import PortfolioModelJGG
#from AlgorithmImports import *

class SimpleRSITestQC500Universe(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021,9,1) # Set Start Date
        self.SetEndDate(2021,9,30) # Set End Date
        self.SetCash(100000) # Set Strategy Cash
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)
        self.SetExecution(ImmediateExecutionModel())
        #self.SetPortfolioConstruction(PortfolioModelJGG(Time.Multiply(Extensions.ToTimeSpan(Resolution.Minute), 1)))
        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel(Time.Multiply(Extensions.ToTimeSpan(Resolution.Minute), 1)))
        self.SetRiskManagement(NullRiskManagementModel())
        #symbols = [ Symbol.Create("SPY", SecurityType.Equity, Market.USA), Symbol.Create("GE", SecurityType.Equity, Market.USA), Symbol.Create("BA", SecurityType.Equity, Market.USA) ]
        #self.SetUniverseSelection(ManualUniverseSelectionModel(symbols))
        self.UniverseSettings.Resolution = Resolution.Minute
        self.AddUniverse(self.Universe.QC500)
        self.AddAlpha(RsiAlphaModelJGG())
        #self.Schedule.On(self.DateRules.EveryDay(), \
                 #self.TimeRules.At(16,00), \
                 #self.EveryDayBeforeMarketClose)
                 
    #def EveryDayBeforeMarketClose(self):
        #self.Log("EveryDay, 1 min before close: Fired at: {0}".format(self.Time))