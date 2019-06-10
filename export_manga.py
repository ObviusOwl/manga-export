#!/usr/bin/env python3
import argparse
import subprocess
import os.path
import re

prog_desc ="""
Exports digital manga PDF files for eReaders using ghostscript. Images are
converted to grayscale and downsampled. Moire patterns cannot be avoided nor 
hidden (blur). If the eReader's reading app crashes on too complex 
pages, lower the image resolution. The PDF files must not be encrypted with DRM.
"""

def escape_ps_str( data ):
    # See the postscript language reference
    data = data.replace('\\','\\\\')
    data = data.replace('(','\(')
    data = data.replace(')','\)')
    return data

def validate_page_list( data ):
    # https://www.ghostscript.com/doc/9.26/Use.htm
    if re.fullmatch( "even|odd|[0-9\-,]+", data, re.IGNORECASE ) == None:
        raise ValueError("Invalid page list.")

def get_output_file( args ):
    if args.output == None:
        inputPath = os.path.realpath( args.input )
        outFile = os.path.basename( inputPath )
        outFile = os.path.splitext( outFile )[0] + "_export.pdf"
        return os.path.join( os.path.dirname( inputPath ), outFile )
    return args.output


parser = argparse.ArgumentParser( description=prog_desc )
parser.add_argument('input', metavar='INPUT.PDF', 
                    help='Input PDF file.')
parser.add_argument('-o','--output', dest='output', default=None, metavar='OUTPUT.PDF',
                    help='Output file. If not specified, the directory of the input file is used and the suffix "_export" is added to the input filename.')
parser.add_argument('-p','--pages', dest='pages', default=None, metavar='PAGES', 
                    help='Process only specified pages. See the documentation of ghostscript\'s PageList for details. Example: 1,2,10-15')
parser.add_argument('--dpi', dest='dpi', default=300, type=int, metavar='DPI', 
                    help='Target DPI for grayscale and color images, default 300.')
parser.add_argument('--dpi-mono', dest='dpi_mono', default=600, type=int, metavar='DPI', 
                    help='Target DPI for monochrome images, default 600.')
parser.add_argument('--no-gray', dest='no_gray', action='store_true',
                    help='Do not convert color to grayscale.')

parser.add_argument('-A','--author', dest='author', default=None, metavar='AUTHOR',
                    help='Set the PDF author metadata. Must be ASCII.')
parser.add_argument('-T','--title', dest='title', default=None, metavar='TITLE',
                    help='Set the PDF title metadata. Must be ASCII.')

args = parser.parse_args()

outPath = get_output_file( args )
print( "Output: {}".format( outPath ) )

pdfmark = ""
if args.title != None:
    pdfmark += "/Title ({})".format( escape_ps_str( args.title ) )
if args.author != None:
    pdfmark += "/Author ({})".format( escape_ps_str( args.author ) )
if pdfmark != "":
    pdfmark = "[ {} /DOCINFO pdfmark".format( pdfmark )

cmd = [ "gs", "-o", outPath, "-sDEVICE=pdfwrite" ]

if args.pages != None:
    validate_page_list( args.pages )
    cmd.append( "-sPageList={}".format( args.pages ) )

cmd_gray = [ 
    "-dProcessColorModel=/DeviceGray",
    "-dColorConversionStrategy=/Gray",
    "-dOverrideICC",
]

cmd_sample = [ 
    "-dMonoImageDepth=8",
    "-dColorImageDownsampleType=/Bicubic",
    "-dGrayImageDownsampleType=/Bicubic",
    "-dMonoImageDownsampleType=/Subsample",
    "-dDownsampleColorImages=true",
    "-dDownsampleGrayImages=true",
    "-dDownsampleMonoImages=true",
    "-dColorImageResolution={}".format( args.dpi ),
    "-dGrayImageResolution={}".format( args.dpi ),
    "-dMonoImageResolution={}".format( args.dpi_mono ),
    "-dColorImageDownsampleThreshold=1.0",
    "-dGrayImageDownsampleThreshold=1.0",
    "-dMonoImageDownsampleThreshold=1.0",
]

if not args.no_gray:
    cmd.extend( cmd_gray )
cmd.extend( cmd_sample )

# "-c" option must come after initial set up is done
if pdfmark != "":
    cmd.extend( ["-c", pdfmark] )

# use "-f" to terminate "-c"
cmd.extend( ["-f", args.input] )

subprocess.run( cmd, check=True )
