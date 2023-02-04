import sys

def Look():							
	global pc						
	if source[pc] == '#':
		while source[pc] != '\n' and source[pc] != '\0': pc += 1
	return source[pc]

def Take():						
	global pc; c = Look(); pc += 1; return c

def TakeString(word):		
	global pc; copypc = pc
	for c in word:
		if Take() != c: pc = copypc; return False
	return True

def Next():							
	while Look() == ' ' or Look() == '\t' or Look() == '\n' or Look() == '\r': Take()
	return Look()

def TakeNext(c):				
	if Next() == c: Take(); return True
	else: return False

def IsDigit(c): return (c >= '0' and c <= '9')								
def IsAlpha(c): return ((c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or (c == ':'))
def IsAlNum(c): return (IsDigit(c) or IsAlpha(c))
def IsAddOp(c): return (c == '+' or c == '-')
def IsMulOp(c): return (c == '*' or c == '/')

def TakeNextAlNum():
	alnum = ""
	if IsAlpha(Next()):
		while IsAlNum(Look()): alnum += Take()
	return alnum

def BooleanFactor(act):
	inv = TakeNext('!'); e = Expression(act); b = e[1]; Next()
	if (e[0] == 'i'): 																		
		if TakeString("=="): b = (b == MathExpression(act))
		elif TakeString("!="): b = (b != MathExpression(act))
		elif TakeString("<="): b = (b <= MathExpression(act))
		elif TakeString("<"): b = (b < MathExpression(act))
		elif TakeString(">="): b = (b >= MathExpression(act))
		elif TakeString(">"): b = (b > MathExpression(act))
	else:
		if TakeString("=="): b = (b == StringExpression(act))
		elif TakeString("!="): b = (b != StringExpression(act))
		else: b = (b != "")
	return act[0] and (b != inv)										

def BooleanTerm(act):
	b = BooleanFactor(act)
	while TakeNext('&'): b = b & BooleanFactor(act)		
	return b

def BooleanExpression(act):
	b = BooleanTerm(act)
	while TakeNext('|'): b = b | BooleanTerm(act)			
	return b

def MathFactor(act):
	m = 0
	if TakeNext('('):
		m = MathExpression(act)
		if not TakeNext(')'): Error("missing ')'")
	elif IsDigit(Next()):
		while IsDigit(Look()): m = 10 * m + ord(Take()) - ord('0')
	elif TakeString("val("):
		s = String(act)
		if act[0] and s.isdigit(): m = int(s)
		if not TakeNext(')'): Error("missing ')'")
	else:
		ident = TakeNextAlNum()
		if ident not in variable or variable[ident][0] != 'i': Error("unknown variable")
		elif act[0]: m = variable[ident][1]
	return m

def MathTerm(act):
	m = MathFactor(act)
	while IsMulOp(Next()):
		c = Take(); m2 = MathFactor(act)
		if c == '*': m = m * m2											
		else: m = m / m2														
	return m

def MathExpression(act):
	c = Next()																			
	m = MathTerm(act)
	if c == '-': m = -m
	while IsAddOp(Next()):
		c = Take(); m2 = MathTerm(act)
		if c == '+': m = m + m2										
		else: m = m - m2														
	return m

def String(act):
	s = ""
	if TakeNext('\"'):															
		while not TakeString("\""):
			if Look() == '\0': Error("unexpected EOF")
			if TakeString("\\n"): s += '\n'
			else: s += Take()
	elif TakeString("str("):												
		s = str(MathExpression(act))
		if not TakeNext(')'): Error("missing ')'")
	elif TakeString("std::input()"):
		if act[0]: s = input()
	else: 
		ident = TakeNextAlNum()
		if ident in variable and variable[ident][0] == 's':	s = variable[ident][1]
		else: Error("not a string")
	return s

def StringExpression(act):
	s = String(act)
	while TakeNext('+'): s += String(act)					
	return s

def Expression(act):
	global pc; copypc = pc; ident = TakeNextAlNum(); pc = copypc			
	if Next() == '\"' or ident == "str" or ident == "std::input" or (ident in variable and variable[ident][0] == 's'):
		return ('s', StringExpression(act))
	else: return ('i', MathExpression(act))

def DoWhile(act):
	global pc; local = [act[0]]; pc_while = pc			
	while BooleanExpression(local): Block(local); pc = pc_while
	Block([False])													

def DoIfElse(act):
	b = BooleanExpression(act)
	if act[0] and b: Block(act)											
	else: Block([False])
	Next()
	if TakeString("else"):													
		if act[0] and not b: Block(act)
		else: Block([False])

def DoGoTo(act):
	global	 pc
	ident = TakeNextAlNum()
	if ident not in variable or variable[ident][0] != 'p': Error("unknown subroutine")
	ret = pc; pc = variable[ident][1]; Block(act); pc = ret		

def DoVoidDef():
	global pc
	ident = TakeNextAlNum()
	if ident == "": Error ("missing subroutine identifier")
	variable[ident] = ('p', pc); Block([False])

def DoAssign(act):																					
	ident = TakeNextAlNum()
	print(ident)
	if not TakeNext('=') or ident == "": Error("unknown statement")
	e = Expression(act)
	if act[0] or ident not in variable: variable[ident] = e		

def DoBreak(act):
	if act[0]: act[0] = False	

def DoImport(act):
    while True:																		
        e = Expression(act)
        if act[0]: packages.append(e[1]);
        if not TakeNext(','): return True
		
def Statement(act):
	if RunPackages(act): return
	elif TakeString("if"): DoIfElse(act)
	elif TakeString("while"): DoWhile(act)
	elif TakeString("break"): DoBreak(act) 
	elif TakeString("goto"): DoGoTo(act)
	elif TakeString("void"): DoVoidDef()
	elif TakeString("using"): DoImport()
	else: DoAssign(act)	

def Block(act):
	if TakeNext('{'):
		while not TakeNext('}'): Block(act)
	else: Statement(act)

def Program():
	act = [True]
	while Next() != '\0': Block(act)

def Error(text):
	s = source[:pc].rfind("\n") + 1; e = source.find("\n", pc)
	print("\nERROR: " + text + " in line " + str(source[:pc].count("\n") + 1) + ": '" + source[s:pc] + "_" + source[pc:e] + "'\n")
	exit(1)

########## Packages ##########

def RunPackages(act):
	if TakeString("std::printf >> "):
		if "std" in packages:
			while True:																		
				e = Expression(act)
				if act[0]: print(e[1], end="");
				if not TakeNext(','): return True
		else:
			Error("package 'std' not imported")
		
	else:
		return False

##############################

pc = 0; variable = {}; packages = []								

if len(sys.argv) < 2: print('USAGE: int.py <sourcefile>'); exit(1)
try: f = open(sys.argv[1], 'r')																				
except: print("ERROR: Can't find source file \'" + sys.argv[1] + "\'."); exit(1)
source = f.read() + '\0'; f.close()																			

Program()