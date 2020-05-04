class ReviewStrategy:
    """Class of representing the review strategy"""
    def __init__(self, propQ, propA, ph, wQsd, wQtd, wQrep,
                 pa, wAsd, wAtd, wArep):
        self.propQ = propQ
        self.propA = propA
        self.ph = ph
        self.wQsd = wQsd
        self.wQtd = wQtd
        self.wQrep = wQrep
        self.pa = pa
        self.wAsd = wAsd
        self.wAtd = wAtd
        self.wArep = wArep

    def printReviewStrategy(self):
        print("PropQ is ", self.propQ, " and PropA is ", self.propA)
        print("ph is ", self.ph, " and pa is ", self.pa)
        print("wQsd: ", self.wQsd, " wQtd: ", self.wQtd, " wQrep: ", self.wQrep)
        print("wAsd: ", self.wAsd, " wAtd: ", self.wAtd, " wQrep: ", self.wQrep)
