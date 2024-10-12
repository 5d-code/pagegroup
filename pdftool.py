#!/usr/bin/env python3

import os
import argparse
from PIL import Image
from pdf2image import convert_from_path

logger = print

def from_images_to_pdf(image_dir: str, output_pdf: str) -> None:
	image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
	
	if not image_files:
		logger('No images found in the directory.')
		return
	
	image_files.sort()
	images = []
	
	for img_file in image_files:
		img_path = os.path.join(image_dir, img_file)
		with Image.open(img_path) as img:
			img = img.convert('RGB')
			images.append(img)

	if not images:
		logger('No valid images found to convert.')
		return
	
	images[0].save(output_pdf, save_all=True, append_images=images[1:])
	logger(f'Converted images in {image_dir} to PDF at {output_pdf}')

def from_pdf_to_images(pdf_path: str, output_folder: str, width: int, height: int) -> None:
	size = None if width == -1 else (width, height)

	if not os.path.exists(output_folder):
		os.makedirs(output_folder)
	
	convert_from_path(
		pdf_path=pdf_path,
		output_folder=output_folder,
		grayscale=False,
		paths_only=True,
		transparent=False,
		use_pdftocairo=True,
		output_file='p',
		size=size
	)
	
	logger(f'Converted {pdf_path} to images in {output_folder}')

def main() -> None:
	parser = argparse.ArgumentParser(description='Convert between images and PDF.')
	subparsers = parser.add_subparsers(dest='command', required=True)

	fromimgs_parser = subparsers.add_parser('fromimgs', help='Convert images to PDF')
	fromimgs_parser.add_argument('image_dir', help='Directory containing images to convert')
	fromimgs_parser.add_argument('output_pdf', help='Path to save the output PDF')

	toimgs_parser = subparsers.add_parser('toimgs', help='Convert PDF to images')
	toimgs_parser.add_argument('width', help='Page width', nargs='?', const=-1, type=int)
	toimgs_parser.add_argument('height', help='Page height', nargs='?', const=-1, type=int)
	toimgs_parser.add_argument('input_pdf', help='Path to the PDF file to convert')
	toimgs_parser.add_argument('output_dir', help='Directory to save the output images')

	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')

	args = parser.parse_args()
	
	if not args.verbose:
		global logger
		logger = lambda *args, **kwargs: None

	if args.command == 'fromimgs':
		from_images_to_pdf(args.image_dir, args.output_pdf)
	elif args.command == 'toimgs':
		from_pdf_to_images(args.input_pdf, args.output_dir, args.width, args.height)

if __name__ == '__main__':
	main()
