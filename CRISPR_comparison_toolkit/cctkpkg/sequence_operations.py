import numpy as np

def rev_comp(string):
	"""Reverse complement a string of nucleotide sequence
	
	Args:
	  string (str):
		  Nucleotide sequence

	Returns:
	  str:
	    reverse complement of given nucleotide sequence
	
	Raises:
	  TypeError: If string is not str.

	"""
	if type(string) is not str:
		raise TypeError(
			"string must be str, not {}.".format(type(string).__name__))

	rev_str = ''
	rev_comp_lookup = {
	"A" : "T", 
	"T" : "A", 
	"C" : "G", 
	"G" : "C", 
	"a" : "t", 
	"t" : "a", 
	"c" : "g", 
	"g" : "c",
	}
	for i in reversed(string):
		if i in "ATCGatcg":
			rev_str += rev_comp_lookup[i]
		else:
			rev_str += i
	return rev_str


def hamming(string1, string2):
	"""Calculate hamming distance between two sequences. 

	Compare them as provided, and with one sequence	shifted one position
	to the left, and with the other sequence shifted one to the left.
	
	Args:
	  string1 (str):
	    First sequence to be compared
	  string2 (str):
	    Second sequence to be compared

	Returns:
	  tuple:
		dist (int): 
		  The hamming distance of the unadjusted sequences
		distplus1 (int):
		  The hamming distance of the first sequence shifted
		distminus1 (int):
		  The hamming distance of the econd sequence shifted

	Raises:
	  TypeError: If string1 and string2 are not str.

	"""
	if type(string1) is not str:
		raise TypeError(
			"Inputs must be str, not {}.".format(type(string1).__name__))
	if type(string2) is not str:
		raise TypeError(
			"Inputs must be str, not {}.".format(type(string2).__name__))
	dist, distplus1, distminus1 = 0,0,0
	string1plus1 = string1[1:]
	string2plus1 = string2[1:]
	for i in range(max(len(string1), len(string2))):
		if i < len(string1) and i < len(string2):
			if string1[i] != string2[i]:
				dist += 1
		else:
			dist += 1
	
	for i in range(max(len(string1plus1), len(string2))):
		if i < len(string1plus1) and i < len(string2):
			if string1plus1[i] != string2[i]:
				distplus1 += 1
		else:
			distplus1 += 1
	
	for i in range(max(len(string1), len(string2plus1))):
		if i < len(string1) and i < len(string2plus1):
			if string1[i] != string2plus1[i]:
				distminus1 += 1
		else:
			distminus1 += 1

	return dist, distplus1, distminus1


def needle(seq1, seq2, match = 100, mismatch = -1, gap = -2):
	"""
	Perform Needleman-Wunsch pairwise alignment of two sequences.
	Args:
	  seq1 (str, list, or tuple):
	    First sequence of items to align.
	  seq2 (str, list, or tuple):
	    Second sequence of items to align
	  match (int):
	    Score for match at a position in alignment.
	  mismatch(int):
	    Penalty for mismatch at a position in alignment.
	  gap (int):
	    Penalty for a gap at a position in alignment.
	
	Returns:
	  (tuple of str lists) Returns a tuple containing the input 
	  seq1 and seq2 aligned with '-' added as gaps.
	  If strings were given then strings are returned.
	  If lists were given then lists are returned.

	Raises:
	  TypeError: If seq1 and seq2 are not str, list, or tuple.
	  TypeError: If match, mismatch, and gap are not int or float.
	"""

	if type(seq1) not in [str, list, tuple]:
		raise TypeError(
			"Inputs must be str, list, or tuple, not {}.".format(
				type(seq1).__name__))
	if type(seq2) not in [str, list, tuple]:
		raise TypeError(
			"Inputs must be str, list, or tuple, not {}.".format(
				type(seq2).__name__))

	if type(match) not in [int, float]:
		raise TypeError(
			"match must be int or float, not {}.".format(
				type(match).__name__))
	if type(mismatch) not in [int, float]:
		raise TypeError(
			"mismatch must be int or float, not {}.".format(
				type(mismatch).__name__))
	if type(gap) not in [int, float]:
		raise TypeError(
			"gap must be int or float, not {}.".format(
				type(gap).__name__))


	# Make a list of lists of 0s with dimensions x by y: 
	# list containing x lists of y 0s each.
	grid = np.zeros((len(seq2)+1, len(seq1)+1))

	# Fill in grid with scores for all possible alignments
	# First score for no alignment (i.e. all gaps)
	for i in range(len(seq1)+1):
		grid[0][i] = gap*i
	for i in range(len(seq2)+1):
		grid[i][0] = gap*i

	# Then score for each cell if you came to it from the 
	# nearest best cell
	for i in range(len(seq1)):
		for j in range(len(seq2)):
			if seq1[i] == seq2[j]:
				score = match
			else:
				score = mismatch
			grid[j+1][i+1] = max([grid[j][i]+score,
				grid[j+1][i]+gap,
				grid[j][i+1]+gap])

	i = len(seq2)
	j = len(seq1)

	# Read back through the grid along the best path to create the
	# best alignment
	align1, align2 = [], []
	# end when it reaches the top or the left edge
	while i > 0 and j > 0:
		score_current = grid[i][j]
		score_diagonal = grid[i-1][j-1]
		score_up = grid[i][j-1]
		score_left = grid[i-1][j]
		if seq1[j-1] == seq2[i-1]:
			score = match
		else:
			score = mismatch
		# Check to figure out which cell the current score was 
		# calculated from, then update i and j to correspond to
		# that cell.
		if score_current == score_diagonal + score:
			align1.append(seq1[j-1])
			align2.append(seq2[i-1])
			i -= 1
			j -= 1
		elif score_current == score_up + gap:
			align1.append(seq1[j-1])
			align2.append('-')
			j -= 1
		elif score_current == score_left + gap:
			align1.append('-')
			align2.append(seq2[i-1])
			i -= 1

	# Finish tracing up to the top left cell
	while j > 0:
		align1.append(seq1[j-1])
		align2.append('-')
		j -= 1
	while i > 0:
		align1.append('-')
		align2.append(seq2[i-1])
		i -= 1
	
	# Since we traversed the score matrix backwards, need to
	# reverse alignments.
	align1 = align1[::-1]
	align2 = align2[::-1]

	if isinstance(seq1, str) and isinstance(seq2, str):
		align1 = ''.join(align1)
		align2 = ''.join(align2)
	
	return align1, align2


def find_indices(lst, element):
	"""Return all indices of list at which an specified element is found.
	
	Given a list and an element found in that list, return all of the 
	indices at which that element is found.
	e.g. for a list ['apple', 'tomatoe', 'apple', 'banana']
	Returns [0,2] for 'apple'

	lst.index() only returns the first instance by default. 
	The second argument provided to index is the position to start
	searching. This approach starts looking again from the index after
	the last found index.


	Args:
	  lst (list): 
	    a list of anything
	  element (any type):
	    An element you expect to find in the list
	
	returns:
	  result (list)
	    A list of indices at which the element was found in the list.
	    Returns an empty list if no indices were found.
	"""
	result = []
	offset = -1
	while True:
		try:
			offset = lst.index(element, offset+1) 
		except ValueError:
			return result
		result.append(offset)
