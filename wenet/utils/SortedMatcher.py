import pywrapfst as fst


class SortedMatcher():
    """
    Sorted Matcher for fst::MATCH_INPUT
    """

    def __init__(self, graph: fst.Fst(), binary_label: int = 1):
        self.graph = graph
        self.state = -1
        self.aiter = None
        self.loop = fst.Arc(-1, 0, fst.Weight.One(self.graph.weight_type()), -1)
        self.label = -1
        self.binary_label = binary_label
        self.narcs = self.graph.num_arcs(0)
        self.exact_match = None
        self.current_loop = None
        self.kArcILabelValue = 0x01
        self.kArcValueFlags = 0x01 | 0x02 | 0x04 | 0x08

    def SetState(self, s: int):
        if self.state == s:
            return
        self.state = s
        self.aiter = fst.ArcIterator(self.graph, s)
        self.loop.nextstate = s
        self.narcs = self.graph.num_arcs(s)

    def Find(self, label: int):
        """
        returns true if label found or label is <eps>
        """
        self.exact_match: bool = True
        self.current_loop = label == 0
        if label == -1:
            self.label = 0
        else:
            self.label = label
        if self.Search():
            return True
        else:
            return self.current_loop

    def LinearSearch(self):
        self.aiter.reset()
        while not self.aiter.done():
            label = self.GetLabel()
            if label == self.label:
                return True
            if label > self.label:
                break
            self.aiter.next()
        return False

    def BinarySearch(self):
        size = self.narcs
        if size == 0:
            return False
        high = size - 1
        while size > 1:
            half = size // 2
            mid = high - half
            self.aiter.seek(mid)
            if self.GetLabel() >= self.label:
                high = mid
            size -= half
        self.aiter.seek(high)
        label = self.GetLabel()
        if label == self.label:
            return True
        if label < self.label:
            self.aiter.next()
        return False

    def Search(self):
        self.aiter.set_flags(self.kArcILabelValue, self.kArcValueFlags)
        if self.label >= self.binary_label:
            return self.BinarySearch()
        else:
            return self.LinearSearch()

    def GetLabel(self):
        arc = self.aiter.value()
        return arc.ilabel

    def Value(self):
        if self.current_loop:
            return self.loop
        self.aiter.set_flags(self.kArcValueFlags, self.kArcValueFlags)
        return self.aiter.value()
