class RsiAlphaModelJGG(AlphaModel):

    def __init__(self, period = 14, resolution = Resolution.Daily):
        self.period = period
        self.resolution = resolution
        self.symbolDataBySymbol = {}
        self.closeWindows = {}
        self.rsiWindows = {}
        resolutionString = Extensions.GetEnumString(resolution, Resolution)
        self.Name = '{}({},{})'.format(self.__class__.__name__, period, resolutionString)
        
    def Update(self, algorithm, data):
        insights = []
        for symbol, symbolData in self.symbolDataBySymbol.items():
            timeDateString = format(algorithm.Time)
            timeString = timeDateString.split()            
            if data.ContainsKey(symbol) and data[symbol] is not None and timeString[1] == "16:00:00":
                self.closeWindows[symbol].Add(data[symbol].Close)
            rsi = symbolData.RSI
            if rsi.IsReady and timeString[1] == "09:31:00":
                #try:
                    self.rsiWindows[symbol].Add(rsi.Current.Value)
                    self.blip = self.rsiWindows[symbol][0] - self.rsiWindows[symbol][1]
                    volatility=(max(self.closeWindows[symbol])-min(self.closeWindows[symbol]))/(max(self.closeWindows[symbol])+min(self.closeWindows[symbol]))*2/self.period
                    if self.rsiWindows[symbol][1] < 30 and self.blip >= 5:
                        for periodIter in [5]:
                            closeList = list(self.closeWindows[symbol])
                            recentMax = max(closeList[0:periodIter-1])
                            recentMin = min(closeList[0:periodIter-1])
                            Mag = (recentMax - recentMin)/recentMin
                            self.insightPeriod = Time.Multiply(Extensions.ToTimeSpan(self.resolution), periodIter)
                            insights.append(Insight.Price(symbol, self.insightPeriod, InsightDirection.Up,Mag,None,None,None))
                    if self.rsiWindows[symbol][1] > 70 and self.blip <= -5:
                        for periodIter in [5]:
                            closeList = list(self.closeWindows[symbol])
                            recentMax = max(closeList[0:periodIter-1])
                            recentMin = min(closeList[0:periodIter-1])
                            Mag = -1*(recentMax - recentMin)/recentMax
                            self.insightPeriod = Time.Multiply(Extensions.ToTimeSpan(self.resolution), periodIter)
                            insights.append(Insight.Price(symbol, self.insightPeriod, InsightDirection.Down,Mag,None,None,None))
                #except:
                    #algorithm.Log(timeDateString)
        return insights

    def OnSecuritiesChanged(self, algorithm, changes):
        
        # clean up data for removed securities
        symbols = [ x.Symbol for x in changes.RemovedSecurities ]
        if len(symbols) > 0:
            for subscription in algorithm.SubscriptionManager.Subscriptions:
                if subscription.Symbol in symbols:
                    self.symbolDataBySymbol.pop(subscription.Symbol, None)
                    subscription.Consolidators.Clear()
                
        # initialize data for added securities
        
        addedSymbols = [ x.Symbol for x in changes.AddedSecurities if x.Symbol not in self.symbolDataBySymbol]
        if len(addedSymbols) == 0: return
        
        history = algorithm.History(addedSymbols, self.period + 20, self.resolution)
        
        for symbol in addedSymbols:
            rsi = algorithm.RSI(symbol, self.period, MovingAverageType.Wilders, self.resolution)
            self.rsiWindows[symbol] = RollingWindow[float](20)
            self.closeWindows[symbol] = RollingWindow[float](self.period)
            for tuple in history.loc[symbol].itertuples():
                self.closeWindows[symbol].Add(tuple.close)
                rsi.Update(tuple.Index, tuple.close)
                if rsi.IsReady:
                    self.rsiWindows[symbol].Add(rsi.Current.Value)
            self.symbolDataBySymbol[symbol] = SymbolData(symbol, rsi)

class SymbolData:
    def __init__(self, symbol, rsi):
        self.Symbol = symbol
        self.RSI = rsi