#!/usr/bin/env python3

from PIL import Image, ImageDraw
from gc import collect
import os
import re
import argparse

PAGE_GROUP_SIZE = 4  # don't change
logger = print

class ImageProcessor:
	def __init__(self, output_dir: str, manga_mode: bool = False) -> None:
		self.index = -1
		self.output_dir = output_dir
		self.manga_mode = manga_mode
	
	def process_images(self, images: list[Image.Image | None]) -> None:
		self.index += 1
		filename = os.path.join(self.output_dir, f'p-{self.index:03}.png')

		non_null_images = [img for img in images if img is not None]

		if len(non_null_images) == 1:
			non_null_images[0].save(filename)
			logger(f'Saved: {filename}')
			return non_null_images[0]

		base_img = non_null_images[0]
		width, height = base_img.size
		new_size = (width // 2, height // 2)

		result_img = Image.new('RGB', (width, height), (255, 255, 255))
		draw = ImageDraw.Draw(result_img)

		if self.manga_mode: positions = [(width // 2, 0), (0, 0), (0, height // 2), (width // 2, height // 2)]
		else: positions = [(0, 0), (width // 2, 0), (0, height // 2), (width // 2, height // 2)]

		for img, pos in zip(non_null_images, positions):
			resized_img = img.resize(new_size)
			result_img.paste(resized_img, pos)

		if len(non_null_images) > 1:
			draw.line([(width // 2, 0), (width // 2, height)], fill='black', width=2)
		if len(non_null_images) > 2:
			draw.line([(0, height // 2), (width, height // 2)], fill='black', width=2)

		result_img.save(filename)
		logger(f'Saved: {filename}')

	def loader(self, fp: str) -> Image.Image | None:
		try:
			return Image.open(fp)
		except Exception as e:
			logger(f'Failed to read {fp}: {e}')
			return None

	def unloader(self, img: Image.Image) -> None:
		if not img: return
		img.close()
		logger('Image unloaded successfully')

def get_sorted_filenames(directory: str) -> list[str]:
	logger('Sorting filenames')
	files = [f for f in os.listdir(directory) if f.endswith('.png')]
	sorted_files = sorted(files, key=lambda f: int(re.search(r'-(\d+)\.png$', f).group(1)))
	return [os.path.join(directory, f) for f in sorted_files]

def paginate_list(items: list, page_size: int) -> list[list]:
	logger(f'Paginating pages into groups of {page_size}')
	pages = [items[i:i + page_size] for i in range(0, len(items), page_size)]
	
	if pages and len(pages[-1]) < page_size:
		pages[-1].extend([None] * (page_size - len(pages[-1])))
	
	return pages

def process_files(pages: list[list[str]], img_processor: ImageProcessor) -> None:
	logger(f'Processing {len(pages)} page groups')

	for i, page in enumerate(pages):
		logger(f'Processing page #{i} with images: {page}')

		loaded_files = [img_processor.loader(filename) for filename in page]
		img_processor.process_images(loaded_files)

		for loaded_file in loaded_files:
			img_processor.unloader(loaded_file)
		
		collect()
		logger('Garbage collected')

def pagegroup(input_dir: str, output_dir: str, manga_mode: bool = False) -> None:
	os.makedirs(output_dir, exist_ok=True)

	sorted_filenames = get_sorted_filenames(input_dir)
	pages = paginate_list(sorted_filenames, PAGE_GROUP_SIZE)
	img_processor = ImageProcessor(output_dir, manga_mode)

	process_files(pages, img_processor)

def main():
	parser = argparse.ArgumentParser(description='convert sets of 4 pages into 1 page')
	parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
	parser.add_argument('-m', '--manga', action='store_true', help='Enable manga mode (pages are tiled right to left)')
	parser.add_argument('in', dest='input', type=str, help='Input directory')
	parser.add_argument('out', type=str, help='Output directory for grouped pages')
	args = parser.parse_args()

	if not args.verbose:
		global logger
		logger = lambda *args, **kwargs: None

	pagegroup(args.input, args.out, args.manga)

if __name__ == '__main__':
	main()
