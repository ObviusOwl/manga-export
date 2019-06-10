# Export Manga

This little wrapper script around ghostscript can be used to downsize digital 
manga PDF files. 

So I purchased high resolution DRM-free manga as PDF files and I thought, what about 
reading them on my e-reader. However, the images embedded in the PDF file were simply too
big and the reader app crashed on some pages. 

The complexity of the images can be reduced, by downscaling the images embedded in 
the PDF to a resolution, the e-reader can handle. Also converting color images 
(such as cover pages) to grayscale images reduces further the amount of data. 
Needless to say, that a 1200 PPI color image displayed on a 300 PPI grayscale 
e-ink display is overkill and wasted memory and processing resources. One thing 
to keep in mind is, that the images in such PDF files fill the entire page.

Manga is traditionally printed black and white. For shades and textures a technique 
called screentone is applied. Patterns of black dots are applied to the 
areas, and depending on the distance between two dots (frequency) the desired 
gradient of gray is visible as a result of an optical illusion.

When downscaling such black and white images moiré patterns appear when the 
resolution is not high enough (according to the Nyquist-Shannon sampling theorem,
the sampling frequency of the pixels must exceed two times the frequency of the pattern).
Downscaling real grayscale images and color images is no problem, until they look 
too blurred. Normally moiré patterns are handled with blurring the image 
(low pass) before downscaling it. Sadly such features are out of the scope of 
ghostscript.

Thus there is a lower bound for the resolution of the black and white images.
It is a bit of trial and error to find the best resolution between overloading
the e-reader and producing moiré patterns. For my device I use 600 PPI for the 
black and white images and 300 PPI for color and grayscale images. My e-reader
then handles downscaling to it's native resolution and produces a nice solid 
gray tone. (btw., PPI or DPI in this context doesn't matter)

Obviously the input PDF files must not be encrypted with DRM and the files 
produced must be used for **personal use only**. 

## Usage

```
usage: export_manga.py [-h] [-o OUTPUT.PDF] [-p PAGES] [--dpi DPI]
                       [--dpi-mono DPI] [--no-gray] [-A AUTHOR] [-T TITLE]
                       INPUT.PDF

Exports digital manga PDF files for eReaders using ghostscript. Images are
converted to grayscale and downsampled. Moire patterns cannot be avoided nor
hidden (blured). If the eReader's reading app crashes on too complex pages,
lower the image resolution. The PDF files must not be encrypted with DRM.

positional arguments:
  INPUT.PDF             Input PDF file.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT.PDF, --output OUTPUT.PDF
                        Output file. If not specified, the directory of the
                        input file is used and the suffix "_export" is added
                        to the input filename.
  -p PAGES, --pages PAGES
                        Process only specified pages. See the documentation of
                        ghostscript's PageList for details. Example: 1,2,10-15
  --dpi DPI             Target DPI for grayscale and color images, default
                        300.
  --dpi-mono DPI        Target DPI for monochrome images, default 600.
  --no-gray             Do not convert color to grayscale.
  -A AUTHOR, --author AUTHOR
                        Set the PDF author metadata. Must be ASCII.
  -T TITLE, --title TITLE
                        Set the PDF title metadata. Must be ASCII.
```

To export multiple files we do some shell scripting and use GNU parallel.
Ghostscript is single threaded and converting the complete file takes a while.

Beware, that the following steps most probably need to be adapted and are only 
provided as more advanced usage example. 

In this example we use the fact that the PDF files are named following the pattern manga_volN.pdf

```sh
sudo apt install parallel
```

Next, we create the script `export_file.sh`:

```sh
#!/bin/bash
VOLUME=$( echo "$1" | sed -E 's/^.*_vol0*([0-9]+).pdf$/\1/g' )
export_manga.py -A "Some Author" -T "My Manga Volume $VOLUME" --dpi 300 --dpi-mono 600 "$1"
```

Finally, we call the script in parallel:

```sh
find . -regex "\./.*_vol[0-9]+\.pdf" | parallel bash ./export_file.sh {}
```

To only export the first 10 volumes and then the next 5:

```sh
find . -regex "\./.*_vol[0-9]+\.pdf" | sort -h | head -n 10 | parallel bash ./export_file.sh {}
find . -regex "\./.*_vol[0-9]+\.pdf" | sort -h | tail -n +11 | head -n 5 | parallel bash ./export_file.sh {}
```

