#!/usr/bin/env python3

# AUTHOR      :  ALAN COLLINS
# VERSION     :  v1
# DATE        :  2021-8-3
# DESCRIPTION :  Process BLAST output of spacers against a blastdb. For results that have cut off due to mismatches, extend the hit to the full length and report mismatches. Report up- and down-stream bases for PAM analysis.

import sys
import argparse
import subprocess

class blast_result():
	"""
	A class to store column contents from a blast result in an easily retrieved form.
	Allows improved code readability when interacting with blast result lines

	Attributes:
		qseqid (str):   query (e.g., unknown gene) sequence id
		sseqid (str):   subject (e.g., reference genome) sequence id
		pident (float): percentage of identical matches
		length (int):   alignment length (sequence overlap)
		mismatch (int): number of mismatches
		gapopen (int):  number of gap openings
		qstart (int):   start of alignment in query
		qend (int): end of alignment in query
		sstart (int):   start of alignment in subject
		send (int): end of alignment in subject
		evalue (str):   expect value
		bitscore (float):   bit score
		qlen (int)  length of query sequence
		slen (int)  length of subject sequence
		strand (str)	Whether the blast hit was on the top (plus) or bottom (minus) strand of the DNA
		trunc (bool)	Whether match might be truncated (i.e. blast result wasn't full qlen)
		sstart_mod (bool/int)   If match appears tuncated, store revised genome locations here
		send_mod (bool/int) If match appears tuncated, store revised genome locations here
	"""
	def __init__(self, blast_line):
		bits = blast_line.split('\t')
		self.qseqid = bits[0]
		self.sseqid = bits[1]
		self.pident = float(bits[2])
		self.length = int(bits[3])
		self.mismatch = int(bits[4])
		self.gapopen = bits[5]
		self.qstart = int(bits[6])
		self.qend = int(bits[7])
		self.sstart = int(bits[8])
		self.send = int(bits[9])
		self.evalue = bits[10]
		self.bitscore = bits[11]
		self.qlen = int(bits[12])
		self.slen = int(bits[13])
		self.strand = 'plus' if self.sstart < self.send else 'minus'
		self.trunc = False 
		self.sstart_mod = False 
		self.send_mod = False


def run_blastcmd(db, fstring, batch_locations):
	"""
	function to call blastdbcmd in a shell and process the output. Uses a batch query of the format provided in
	the blastdbcmd docs. e.g.
	printf "%s %s %s %s\\n%s %s %s\\n" 13626247 40-80 plus 30 14772189 1-10 minus | blastdbcmd -db GPIPE/9606/current/all_contig -entry_batch -
	
	Args:
		db (str): path to the blast db you want to query.
		fstring (str):  The string to give to printf
		batch_locations (str):  the seqid, locations, and strand of all the spacers to be retrieved
	
	Returns:
		(list) List of the sequences of regions returned by blastdbcmd in response to the query locations submitted
	
	Raises:
		ERROR running blastdbcmd: Raises an exception when blastdbcmd returns something to stderr, 
		prints the error as well as the information provided to blastdbcmd and aborts the process.
	"""
	x = subprocess.run('printf "{}" {}| blastdbcmd -db {} -entry_batch -'.format(fstring, batch_locations, db), 
						shell=True, universal_newlines = True, capture_output=True) 
	if x.stderr:
		print("ERROR running blastdbcmd on {} :\n{}".format(db, batch_locations, x.stderr))
		sys.exit()
	else:
		return [i for i in x.stdout.split('\n') if '>' not in i and len(i) > 0]



def run_blastn(args):
	"""
	Runs blastn of provided spacers against provided blastdb. Processes the blast output to find hits and if the hits don't cover the whole length, the hits are extended using the provided blastdb.
	Args:
		args (argparse class): All of the argparse options given by the user.

	
	Returns:
		(list):  List of lines of a blast output file.
	
	Raises:
		ERROR running blast.
	"""	
	blastn_command = "blastn -query {} -db {} -task blastn-short -outfmt '6 std qlen slen' -num_threads {} -max_target_seqs {} -evalue {} {}".format(args.spacer_file, args.blast_db_path, args.num_threads, args.max_target_seqs, args.evalue, args.other_blast_options)
	blast_run = subprocess.run(blastn_command, shell=True, universal_newlines = True, capture_output=True)
	# blast_lines = [blast_result(i) for i in subprocess.run(blastn_command, shell=True, universal_newlines = True, capture_output=True).stdout.split('\n') if len(i) > 0]
	if blast_run.stderr:
		print("ERROR running blast on {}:\n{}".format(args.blast_db_path, blast_run.stderr))
		sys.exit()
	blast_lines = [blast_result(i) for i in blast_run.stdout.split('\n') if len(i) > 0]
	return blast_lines


parser = argparse.ArgumentParser(
	description="Process BLAST output of spacers against a blastdb. For results that have cut off due to mismatches, extend the hit to the full length and report mismatches. Report up- and down-stream bases for PAM analysis."
	)
parser.add_argument(
	"-d", dest="blast_db_path", required = True,
	help="path to blast db files (not including the file extensions). The blastdb must have been made with the option '-parse_seqids' for this script to function."
	)
parser.add_argument(
	"-s", dest="spacer_file", required = True,
	help="The file with your spacers in fasta format."
	)
parser.add_argument(
	"-o", dest="outfile", required = True,
	help="path to output file."
	)
parser.add_argument(
	"-e", dest="evalue", required = False, default='10',
	help="DEFAULT: 10. set the evalue cutoff below which blastn will keep blast hits when looking for CRISPR repeats in your blast database. Useful for reducing inclusion of low quality blast hits with big databases in combination with the -m option."
	)
parser.add_argument(
	"-m", dest="max_target_seqs", required = False, default='10000',
	help="DEFAULT: 10000. Set the max_target_seqs option for blastn when looking for CRISPR repeats in your blast database. Blast stops looking for hits after finding and internal limit (N_i) sequences for each query sequence, where N_i=2*N+50. These are just the first N_i sequences with better evalue scores than the cutoff, not the best N_i hits. Because of the nature of the blast used here (small number of queries with many expected hits) it may be necessary to increase the max_target_seqs value to avoid blast ceasing to search for repeats before all have been found. The blast default value is 500. The default used here is 10,000. You may want to reduce it to increase speed or increase it to make sure every repeat is being found. If increasing this value (e.g. doubling it) finds no new spacers then you can be confident that this is not an issue with your dataset."
	)
parser.add_argument(
	"-t", dest="num_threads", required = False, default=1, type=int,
	help="DEFAULT: 1. Number of threads you want to use for the blastn step of this script."
	)
parser.add_argument(
	"-x", dest="other_blast_options", required = False, default='',
	help="DEFAULT: none. If you want to include any other options to control the blastn command, you can add them here. Options you should not provide here are: blastn -query -db -task -outfmt -num_threads -max_target_seqs -evalue"
	)


args = parser.parse_args(sys.argv[1:])

blast_output = run_blastn(args)



