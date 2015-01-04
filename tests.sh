:
# tests.sh
#
# If you send the stdout to a file it can be nicely diff'ed with a
# stable earlier one to see what changed

python testAll.py gram_aAb.txt   first

python testAll.py gram_aAb.txt   nullable

python testAll.py gram_nulls.txt nullable

python testAll.py gram_aAb.txt   terminal

python testAll.py gram_aAb.txt   complete "S ::= . A $"

python testAll.py gram_aAb.txt   item "a . A b"

python testAll.py gram_nulls.txt cfsm S 

python testAll.py gram_ETF.txt cfsm S

#
echo ""
echo "Tests are complete"

