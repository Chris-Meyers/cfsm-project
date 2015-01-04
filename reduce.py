#  reduce.py - now just check syntax of a program

def prettyReduceStack(stack, msg="Reduce Stack") :
    ans = []
    for item in stack :
        if type(item) == type("") : ans.append(item)
        else : ans.append("*S%d" % item.stateNo)
    return msg + ": " +  "--".join(ans)

def syntaxCheck(states, program) :
    # walk program from program thru the states
    #   states  - a list of State instances
    #   program - a list of symbols to walk thru
    #
    dbg = True 
    startState = states[0]
    startSymbol = startState.items[0][0]
    stack = [startState]
    sym = program.pop(0)   # get first program symbol
    while stack :
        if dbg : print prettyReduceStack(stack, "Top of loop"), "Sym=",sym
        state = stack[-1]
        if state.trans : # If this is a shift state
            if not sym : sym = program.pop(0) # get next program symbol
            ns = state.trans.get(sym)   # state to shift
            state = states[ns]
            stack.append(sym)
            stack.append(state)
            if dbg : print "shift stacks character", sym
            sym = None 
        else :
            # reduce state
            head,tail = state.items[0]
            walkBack = list(tail[:-1]); walkBack.reverse()
            if dbg : print "=== Ready to reduce", head,tail, walkBack
            stack.pop()              # get rid of term state
            for token in walkBack :
                if dbg : print prettyReduceStack(stack, "Reduced")
                assert (token == stack.pop())  # in sync
                state = stack.pop()            # and state before
            stack.append(state)      # resume sourec state w Nonterm sym
            sym = head               # proceed thru the maze
            if sym == startSymbol : break # we did it !
    return True

