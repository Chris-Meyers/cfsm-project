#  Lalr(1) with lookahead.
#
from basics import prettyProds, prettyProd, prettyDict, prettySet

class State :
    def __init__ (self, stateNo, parent, kernel, lahs, tables) :
        self.stateNo = stateNo
        self.parent  = parent
        self.kernel  = tuple(kernel)
        self.tables  = tables
        self.items   = list(kernel)
        self.lahs    = lahs     # lookahead dict (set per item)
        self.trans   = {}       # transition table for sym-lah pairs
        self.reducs  = set([])  # sym to reduce with
        self.bgColor = "white"

    def prettyPrint(self,msg="") :
        import re
        lines = []
        msg = prettySet(self.reducs)
        banner = "State %s Reduce=%s" % (self.stateNo,msg)
        lines.append(banner)
        # Get shift symbols and target states
        shifts = self.trans.items(); shifts.sort(); shiftStr=''
        for tup in shifts : shiftStr += " %s:%s" % tup
        if shifts : lines.append("Shifts: %s" % shiftStr)
        # Each item with production and lookahead
        for item in self.items :
            lahs = self.lahs.get(item)
            lines.append("%s   %s" % (prettyProd(item),prettySet(lahs)))
        # right justify lahs in the item lines
        targLen = max(20, max(map(lambda x:len(x), lines)))
        for i in range(len(lines)) :
            need = targLen-len(lines[i])
            lines[i] = re.sub(" {"," "*need+" {",lines[i])
        return "\n".join(lines)

    def completeState(self) :
        self.items = completeState(self.kernel, self.lahs, self.tables)

    def makeTranKernels(self) :
        return makeTranKernels(self.items)

def makeCfsm(startSym, tables) :
    # Implements Rule 4
    dbg = False
    stateNo = 0      # Prime the pump !
    states = {}
    startKern = []
    for head,tail in tables.rules :
        if head == startSym : startKern.append((head, ((".",) + tail)))
    todo = [(None, tuple(startKern),{})] # No parent. lookahead empty
    countDown = 444
    while todo :
        countDown -= 1
        if countDown == 0 : break
        # Pop off a kernel w parent, and lah dict (basis for new state)
        parent, kernel, lahs = todo.pop(0)        # process breadth first
        if dbg:
            print kernel, lahs
            print prettyProds(kernel, "=== Pop parent=%s" % parent, lahs)

        # Need to build a new state and complete it
        state = State(stateNo, parent, kernel, lahs, tables)
        if dbg: print state.prettyPrint("Kernel")
        state.completeState()  # this will iterate updating items and lah
        if dbg: print state.prettyPrint("Complete")
        
        if dbg: print "===1", kernel
        dupState = states.get(kernel)
        if dupState :
            # merge lah for each item into the original (that we keep)        
            if dbg: print "Dup ===2", prettyDict(dupState.lahs,"dupState.lahs")
            if dbg: print "Dup ===3", prettyDict(state.lahs, "state.lahs")
            for (key,value) in state.lahs :
                if dupState.lahs.get(key) == None :
                    dupState.lahs[key] = set([])
                dupState.lahs[key].update(state.lahs.get(key,set([])))
        else :
            # Keep this new state in the network
            states[kernel] = state  # two ways to look it up
            states[stateNo] = state
            stateNo += 1
            
            # Adding Transitions ------
            newKernels, newLahs = makeTranKernels(state.items,state.lahs)
            syms = newKernels.keys(); syms.sort()
            state.trans = newKernels  # temp, later map to state #
            for sym in syms :
                if dbg:
                    msg = "New kernel for sym %s" % sym,
                    print prettyProds(newKernels[sym], msg, newLahs)
                todo.append( (state, tuple(newKernels[sym]), newLahs) )

    # Build list of states and remap their transitions to state numbers
    stateList = []
    fmt = "State=%s. Symbol %s maps to %s and %s"
    for st in range(stateNo) :
        state = states[st]
        tranMap = state.trans
        tranSyms = tranMap.keys()
        for sym in tranSyms :
            tKernel = tranMap[sym] # lookup target state by kernel
            tState  = states[tuple(tKernel)]
            prev = state.trans.get(sym)
            # the following is a bit edgy
            if prev and type(prev) == type(5) :  # dup mapping
                print fmt % (state.stateNo,sym,prev,tState.stateNo)
            state.trans[sym] = tState.stateNo
            ###print prettyDict(state.trans, "Trans for state %s" % st)
        stateList.append(state)
    return stateList

def makeTranKernels(items, prev_lahs) :
    # return dict by transition symbol of new kernels
    kernels = {}        # for each transistion symbol
    lahs    = {}
    for item in items :
        head,rhs = item
        nxtTok = nextToken(rhs)
        if nxtTok :
            nxtRhs = shiftItem(rhs)         # create new item w dot shifted
            nxtItem = (head,nxtRhs)
            kern = kernels.get(nxtTok,[])   # One kernel for each token
            kern.append(nxtItem)
            kernels[nxtTok] = kern
            # lookaheads just copied to new items
            lahs[nxtItem] = prev_lahs.get(item,set([]))
    return kernels,lahs

def completeState (kernel, lahs, tables) :
    "kernel is initial seq of dotted productions - return full seq"
    "lahs - set for the kernel already - will expand it"
    dbg = False
    already = {}
    for item in kernel : already[item] = True
    items = list(kernel)   # leave kernel unmodified
    changed = True
    while changed :
        changed = False
        if dbg : print prettyProds(items,"Top of Loop",lahs)
        for item in items :
            lahL = lahs.get(item,set([]))  # lookaheads so far for item
            newProds,newLahs = expandItem(item,lahs,tables)
            if dbg :
                msg = "===4 Complete state mid"
                if dbg: print prettyProds(newProds,msg,newLahs)

            for prod in newProds :
                if not already.get(prod) :
                    already[prod] = True
                    items.append(prod)
                    lahs[prod] = set([])  # start w/o lah
                    changed = True
                    if dbg : print "Add prod", prettyProd(prod,newLahs)
            if newLahs :
                for itm,nlah in newLahs.items() :
                    if not nlah.issubset(lahs[itm]) :
                        changed = True               # or if lahs changed
                        lahs[itm].update(nlah)
    return items

def expandItem(item,lahs,tables) :
    # from a dotted righthand side, return productions and lookaheads
    newProds = []; newLahs={}
    head,rhs = item
    nsym = len(rhs)
    for p in range(nsym) :
        if rhs[p] == '.' :
            break
            
    if p < nsym-1 :
        sym = rhs[p+1]
        if not tables.terminal[sym] :
            alpha = rhs[p+2:]
            lahL = lahs.get(item, set([]))
            lahM = getLookaheads (alpha, tables, lahL)
            for head,tail in tables.rules :
                if head == sym :
                    newProd = (sym,(('.',)+tail))
                    newProds.append(newProd)
                    newLahs[newProd] = lahM
    return newProds, newLahs

def getLookaheads (alpha, tables, lahL=set([])) :
    # generate a set of lookaheads for alpha seq. Include
    # lahL included if alpha is nullable
    
    lahM = set([])         # M set 
    alphaNullable = True   # well, maybe - if alpha empty or nullable
    for sym in alpha :
        # keep adding Firsts[sym] till non-null stops us
        lahM.update(tables.firsts[sym]) #  See Rule 4
        if sym not in tables.nullables :
            alphaNullable = False
            break
    if alphaNullable :
        lahM.update(lahL)
    return lahM

#--------------------- Helpers -------------

def findDot(rhs) :
    for i in range(len(rhs)) :
        if rhs[i] == '.' : return i
    print "Where is the dot in ", rhs

def shiftItem(rhs) :  
    over = nextToken(rhs)  # token to take
    assert over # Make sure there is a token to shift over
    p = findDot(rhs)
    return rhs[:p] + (over,".") + rhs[p+2:]

def finalItem (rhs) :
    return rhs[-1:] == '.'

def nextToken(rhs) :
    if finalItem(rhs) : return None
    p = findDot(rhs)
    if p < len(rhs)-1 : return rhs[p+1]
    else              : return None
