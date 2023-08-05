 
_heuristic(xreaction(R,N),level,1) :- ireaction(R,N).
_heuristic(xreaction(R,N),sign,-1) :- ireaction(R,N).

#hide.
#show _heuristic/3.
#show  xreaction/2.
