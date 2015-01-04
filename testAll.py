#!/usr/bin/env python
#
#  testAll.py
#
#  1st arg grammar file. 2nd arg test to run. more args as needed
#
tests = (
   'null',       # print nullables for grammar
   'rule',       # print rules for grammar
   'term',       # print terminal dictionary for grammar
   'firs',       # print firstSets for grammar
   'look',       # ahead. alpha like "b" for "a.Ab"
   'expa',       # expand item like "S ::= .A $" with dot
   'comp',       # complete kernel like "S -> E" "E -> A"
   'tran',       # prods like "E etc
   'cfsm',       # start symbol like "S"
   'json',       # start symbol like "S". Produce json dump
   'synt',       # gram syntax termSyms
)

class Tables : pass

def test () :
    import sys
    from basics import parseRules ,getNullables, getFirsts, getTerminals
    from basics import prettyDict, prettyProds, prettyProd
    from cfsm   import expandItem, completeState, getLookaheads
    from cfsm   import makeTranKernels, makeCfsm
    from reduce import syntaxCheck

    commandLine = " ".join(sys.argv)
    print
    print "---------------- TEST -------------------"
    print commandLine
    print

    tables = Tables()

    tables.grammar = open(sys.argv[1]).read()
    action  = sys.argv[2][:4].lower()   # match just 4 chars keep simple
    if action not in tests:
        print "action must be one of:", tests
        return
    
    print tables.grammar
    tables.rules = parseRules(tables.grammar)
    if action == 'rule' :
        print "Rules"
        for rule in tables.rules : print rule
        return

    tables.nullables = getNullables(tables.rules)
    if action == 'null' :
        print "Nulls are:", tables.nullables
        return

    tables.terminal = getTerminals(tables.rules)
    if action == 'term' :
        print "Symbols (True if terminal)"
        print tables.terminal
        return
    
    tables.firsts = getFirsts(tables)
    if action == 'firs' :
        print prettyDict(tables.firsts, 'First Sets (Iterative)')
        return
    
    if action == 'look' :
        # see Rule 4 - the symbols after a non-term after the dot
        alpha = tuple(sys.argv[3:])
        alpha = " ".join(sys.argv[3:]).split()  # with or w/o quotes
        print getLookaheads(alpha, tables, lahL=set(['Lset-included']))

    if action == 'expa' :
        # expand an item. New productions (Rule 4) also get lahM
        rule = " ".join(sys.argv[3:])      # with or w/o quotes
        item = parseRules(rule)[0]         # parseRules works w lists
        prods,lahs = expandItem(item,{},tables) # no prior lah
        print "---item '%s' expands to..." % rule
        for prod in prods :
            print " %s" % (prettyProd(prod,lahs))
        return

    if action == 'comp' :
        # complete a state.
        lahs = {}
        kernel = "\n".join(sys.argv[3:]) # each item must be quoted
        kernel = parseRules(kernel)
        items  = completeState(kernel, lahs, tables)
        print prettyProds(kernel,"kernel items",lahs)
        print prettyProds(items, "expand to",   lahs)
        return

    if action == 'cfsm' :
        startState = sys.argv[3]
        states = makeCfsm(startState, tables)
        print "States expanded from ", startState
        for state in states :
            print state.prettyPrint("Finished")
            print
        return

    if action == 'json' :
        import json
        startState = sys.argv[3]
        states = makeCfsm(startState, tables)
        jsonOutput = []
        fp = open("testAll.json","w")
        for state in states :
            jsonOutput.append(state.prettyPrint("Finished"))
        fp.write(json.dumps(jsonOutput))
        fp.close()
        return

    if action == 'synt' :
        startState = sys.argv[3]
        symbols = ' '.join(sys.argv[4:]).split()
        print "Input is ", symbols
        states = makeCfsm(startState, tables)
        ok = syntaxCheck(states,symbols)
        if ok : print "Syntax OK for grammar"
        else  : print "Syntax check failed"
        return

    if action in ('comp', 'tran')  :
        items = "\n".join(sys.argv[3:])
        items = parseRules(items)
        prods = completeState (items,tables)

        print "-- state kernel"
        for item in items : print "  ",item
        print "--- state completed"
        for prod in prods : print "  ", prod

        if action == 'tran' :
            kernels = makeTranKernels(prods)
            print prettyDict(kernels, "Transitions: Sym to new Kernels")
        return

if __name__ == "__main__" : test()

