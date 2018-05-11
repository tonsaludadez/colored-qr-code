from PIL import Image
from pyzbar.pyzbar import decode
import base64
import errno
import segno
import os
import sys
import textwrap
import time

script, path, action = sys.argv

ACTIONS = ['encode', 'decode']

class ColorQRCode:
	MAX_BYTES = 2953
	# FILE_TYPES_CODE = ['11111111', '11111110', '11111100','11111000','11110000']
	FILE_TYPES = ['png', 'txt', 'mid', 'jpg', 'gif']

	def __init__(self, path):
		print "Initializing......................",
		start_time = time.time()

		self.path = path
		self.filename, self.filetype = self.path.split('\\')[-1].split('.')
		self.filetype = self.filetype.lower()
		self.data = ""
		self.max_bin = 0
		self.qr_codes = []
		self.folder_path = str(self.path) + '-files/'
		self.qr_codes_filename = []

		print "Done: ",
		print("%s seconds" % (time.time() - start_time))

	def get_data(self):
		print "Converting data...................",
		start_time = time.time()

		if not os.path.exists(os.path.dirname(self.folder_path)):
		    try:
		        os.makedirs(os.path.dirname(self.folder_path))
		    except OSError as exc:
		        if exc.errno != errno.EEXIST:
		            raise

		with open(self.path, 'rb') as file:
			# temp = ColorQRCode.FILE_TYPES_CODE[ColorQRCode.FILE_TYPES.index(self.filetype)]
			if self.filetype in ColorQRCode.FILE_TYPES:
				temp = '{0:b}'.format(ColorQRCode.FILE_TYPES.index(self.filetype)).zfill(8)
			else:
				return -1
			temp += file.read()
			if self.filetype != 'txt':
				# print len(temp)
				temp = base64.b64encode(temp)
		self.data = temp
		print "Done: ",
		print("%s seconds" % (time.time() - start_time))

	def encode_to_qr_codes(self):
		print "Encoding data to QR codes.........",
		start_time = time.time()

		size = len(self.data)
		# data = textwrap.wrap(self.data, ColorQRCode.MAX_BYTES)
		data = [self.data[i:i+ColorQRCode.MAX_BYTES] for i in range(0, len(self.data), ColorQRCode.MAX_BYTES)]
		# print "SIZE: ",
		# print size
		# print "ARRAY: ",
		# print len(data)
		if len(data) > 24:
			return -1

		for i in range(len(data)):
			self.qr_codes.append(segno.make(str(data[i]), version = 40, error = 'l', mask=0))

		self.max_bin = '1' * len(data)
		print "Done: ",
		print("%s seconds" % (time.time() - start_time))

	def generate_color_qr_code(self):
		print "Generating color QR code..........",
		start_time = time.time()

		ctr = 0
		for code in self.qr_codes:
			fn = self.folder_path + 'qcode' + str(ctr+1) + '.png'
			self.qr_codes_filename.append(fn)
			code.save(fn, scale=2)
			ctr += 1

		qr_codes = []
		for code_filename in self.qr_codes_filename:
			qr_codes.append(Image.open(code_filename).convert('RGB'))

		qr_code_data = []
		for qr_code in qr_codes:
			qr_code_data.append(qr_code.getdata())

		qr_code_color = []															#
		for i in range(len(qr_code_data[0])):										
			qr_code_color.append('')												#	Initializing qr_code_data list

		for qr_data in qr_code_data:
			ctr = 0
			for pixel in qr_data:
				if pixel == (255, 255, 255):
					qr_code_color[ctr] += '1'
				else:
					qr_code_color[ctr] += '0'
				ctr += 1

		qr_code_color_data = []
		for code_color in qr_code_color:
			if int(code_color) == int(self.max_bin):
				qr_code_color_data.append((255, 255, 255))
			else:
				color = textwrap.wrap(code_color.zfill(24), 8)
				qr_code_color_data.append((int(color[0],2), int(color[1],2), int(color[2],2)))

		color_qr_code = Image.new('RGB', (555, 555))
		color_qr_code.putdata(qr_code_color_data)
		color_qr_code.save(str(self.filename) + str(self.filetype) + '-colorqr.png')
		
		print "Done: ",
		print("%s seconds" % (time.time() - start_time))
	
	def encode_color_qr_code(self):
		if self.get_data() != -1:
			if self.encode_to_qr_codes() != -1:
				self.generate_color_qr_code()
			else:
				print "Invalid file size. Cannot encode data to qr code."
		else:
			print "Invalid file type. Cannot encode data to qr code."

	def decode_color_qr_code(self):
		print "Demultiplexing color QR code......",
		start_time = time.time()

		cqr = Image.open(self.path)
		cqr_data = cqr.getdata()

		if not os.path.exists(os.path.dirname(self.folder_path)):
		    try:
		        os.makedirs(os.path.dirname(self.folder_path))
		    except OSError as exc:
		        if exc.errno != errno.EEXIST:
		            raise

		qr_data = []
		for i in xrange(24):
			qr_data.append('')

		for pixel in cqr_data:
			r, g, b = pixel
			r = '{0:08b}'.format(r)
			g = '{0:08b}'.format(g)
			b = '{0:08b}'.format(b)

			ctr = 0
			for i in xrange(0, 8):
				qr_data[i] += r[ctr]
				ctr += 1
				
			ctr = 0
			for i in xrange(8, 16):
				qr_data[i] += g[ctr]
				ctr += 1

			ctr = 0
			for i in xrange(16, 24):
				qr_data[i] += b[ctr]
				ctr += 1 
		

		ctr = 0
		for data in qr_data:
			img_data =[]
			for pixel in data:
				if pixel == '0':
					img_data.append((0, 0, 0))
				else:
					img_data.append((255, 255, 255))
			
			color_qr_code = Image.new('RGB', (555, 555))
			color_qr_code.putdata(img_data)
			color_qr_code.save(str(self.folder_path) + "decoded" + str(ctr+1) + ".png")
			ctr += 1
		
		print "Done: ",
		print("%s seconds" % (time.time() - start_time))

		print "Decoding QR codes.................",
		start_time = time.time()

		data = ""
		path = self.folder_path.replace('/', '\\')
		for i in xrange(1, 25):
			decoded_data = decode(Image.open(path + 'decoded' + str(i) + '.png'))
			if decoded_data:
				data += str(decoded_data[0].data)

		if not data:
			return -1;

		filetype = ""
		if not data.startswith('{0:b}'.format(ColorQRCode.FILE_TYPES.index('txt')).zfill(8)):
			data = base64.b64decode(data)

		print "Done: ",
		print("%s seconds" % (time.time() - start_time))

		print "Producing encoded file............",
		start_time = time.time()

		ft = data[:8]
		data = data[8:]
		filetype = ColorQRCode.FILE_TYPES[int(ft, 2)]

		with open('DECODED' + str(self.filename) + '.' + filetype, 'wb') as file:
			file.write(data)

		print "Done: ",
		print("%s seconds" % (time.time() - start_time))

def main():
	if action in ACTIONS:
		print "----RUNNING PROGRAM: " + action
		start_time = time.time()
		if action == 'encode':
			cqr1 = ColorQRCode(path)
			cqr1.encode_color_qr_code()
		elif action == 'decode':
			cqr2 = ColorQRCode(path)
			if cqr2.decode_color_qr_code() == -1:
				print "Image is not a QR code"
		print("----END TIME: %s seconds" % (time.time() - start_time))
	else:
		print str(action) + " is not a valid action"

if __name__ == '__main__':
	main()
