#  basics.py  
#
import sys, copy, re

def parseRules(gram) :
    "converts grammar in text to list of productions (head,tail)"
    rules = []
    lines = gram.split("\n")
    for line in lines :
        line = re.sub("#.*","",  line)   # ignore comments
        line = re.sub("->","::=",line)   # alt syntax
        parts = line.split()
        if not parts : continue   # ignore blank lines
        assert parts[1] == '::=', "Syntax error in %s" % line 
        head = parts[0]
        tail = tuple(parts[2:])
        rules.append ((head,tail))
    return rules

#--------------------- Terminals - Rule 1

def getTerminals(prods) :
    "Return a set of symbols who are the head of a prod"
    terminal = {}
    for head,tail in prods :
        for sym in tail : terminal[sym] = True
    for head,tail in prods :
        terminal[head] = False
    return terminal

#--------------------- Nullables - Rule 1

def getNullables(prods) :
    "Implements Rule 1 in CFSM. Returns set of nullable nonterms"
    nullables = set([])   # e is the empty epsilon char
    changed = True
    while changed :
        changed = False
        for head,tail in prods :
            if head not in nullables :
                mightBe = True
                for symb in tail :
                    if symb not in nullables : mightBe=False
                    if not mightBe : break
                if mightBe :
                    nullables.add(head)
                    changed = True
                    #print "%s is now nullable from %s" % (head, tail)
    return nullables

#----------------------- First Sets - Iterative - Rule 2

def getFirsts(tables) :
    "Implements Rule 2 in CFSM iteratively. Return First set for each sym"
    firsts = {}
    for sym in tables.terminal.keys() :
        # for all symbols
        if tables.terminal[sym] : firsts[sym] = set([sym])
        else                    : firsts[sym] = set([])

    while True :
        changed = False
        before = copy.deepcopy(firsts)
        for head,rhs in tables.rules :
            for sym in rhs :
                before = set(firsts[head]) # force a copy
                firsts[head] = firsts[head].union(firsts[sym])
                if firsts[head] != before : changed=True
                if sym not in tables.nullables : break
        if not changed : return firsts

#----------------------------- Useful defs

def prettyDict(dict, msg) :
    lines = ["------- %s" % msg]
    key = dict.keys(); key.sort()
    for f in key :
        lines.append("%-5s -> %s" % (f,dict[f]))
    return "\n".join(lines)

def prettyProds(prods, msg, lahs={}, lterm="\n") :
    lines = ["%s" % msg]
    for prod in prods :
        lines.append(prettyProd(prod,lahs))
    return lterm.join(lines)

def prettyProd(prod, lahs={}) :
    head,tail = prod
    lah = prettySet(lahs.get(prod,set([])))
    return "%s ::= %s  %s " % (head," ".join(tail), lah)

def prettySet(aset) :
    if not aset : return "{}"
    return "{%s}" % (" ".join(tuple(aset)))

