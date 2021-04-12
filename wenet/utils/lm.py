import pywrapfst as fst
from wenet.utils.SortedMatcher import SortedMatcher


class LmFst():

    def __init__(self, fst_file: str, symbol_table_file: str):
        self.graph: fst.Fst() = fst.Fst.read(fst_file)
        #print("INFO: Checking fst ILabel Sorted", fst.properties(fst.I_LABEL_SORTED, True) == fst.I_LABEL_SORTED)
        self.symbol_table: fst.SymbolTable() = fst.SymbolTable.read_text(symbol_table_file)
        self.sos: int = -1
        self.eos: int = -1
        self.start: int = -1
        self.sos = self.symbol_table.find("<s>")
        self.eos = self.symbol_table.find("</s>")
        weight, self.start = self.Step(self.graph.start(), self.sos, self.start)
        print("INFO: Start id step by <s> is ", self.start)

    def Step(self, state: int, ilabel: int, next_state: int):
        """
        start from state and find ilabel among all outgoing arcs, if present.
        else traverse to next state via an <eps> ilabel arc and repeat
        return that arcs next_state and weight (sum)
        """
        sm = SortedMatcher(self.graph)
        sm.SetState(state)
        if sm.Find(ilabel):
            arc = sm.Value()
            next_state = arc.nextstate
            return -float(arc.weight), next_state
        aiter = fst.ArcIterator(self.graph, state)
        if not aiter.done() and aiter.value().ilabel == 0:
            arc = aiter.value()
            return -float(arc.weight) + self.Step(arc.nextstate, ilabel, next_state)[0], next_state
        else:
            next_state = self.start
            # something small enough
            return -1e5, next_state

    def StepEos(self, state: int, next_state: int):
        return self.Step(state, self.eos, next_state)

    def StepTokenArray(self, strs: list):
        state: int = self.start
        next_state: int = 0
        sentence_weight: float = 0.0
        strs_add_eos = strs.copy()
        strs_add_eos.append("</s>")
        for i in range(len(strs_add_eos)):
            ilabel: int = self.symbol_table.find(strs_add_eos[i])
            weight, next_state = self.Step(state, ilabel, next_state)
            sentence_weight += weight
            print("INFO:", state, next_state, ilabel, "(", strs_add_eos[i], ")", weight, sentence_weight)
            state = next_state
        return sentence_weight
