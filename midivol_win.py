import sys
import time
from subprocess import call	
import pygame.midi

class NircmdMixer():
	"""
	Set system volume, val =[0, 65535]
	"""
	def __init__(self):
		self.current_volume = 0
		
	def volume_to_int(self, volume):
		"""
		Convert 0-100 volume value to [0, 65535] range
		"""
		result = 0
		try:
			result = int(65535 * volume / 100)
		except Exception:
			pass		
		return result
		
	def setvolume(self, vol, verbose=False):	
		if vol != self.current_volume:			
			volume = self.volume_to_int(vol)
			call(["nircmd", "setsysvolume", str(volume)])			
			self.current_volume = vol
			if verbose:
				print 'Midivol: Volume set to {}'.format(self.current_volume)
			# print str(volume)

class Midivol():
	'''
	Class used to control master volume mixer (using nircmd) from midi input (pygame.midi) on windows systems
	'''
	system_mixer = NircmdMixer()
	tag ='Midivol: ' 

	def __init__(self, device='', max_volume=30, channel=None, control=None, verbose=False):
		self.device = device
		self.max_volume = max_volume
		self.channel = channel
		self.control = control
		self.verbose = verbose
		self.inputs = pygame.midi
		self.inputs.init()
		self.devices = self.get_device_list()

	def start(self):
		'''
		Finalize midivol and run main listening loop
		'''
		if not self.device:	
			if self.inputs.get_count() == 0:
				raise Exception('No available MIDI devices')
			else:				
				for d in self.devices:
					if d[2] == 1: #input
						self.device = self.devices.index(d)
						break					
		else:
			try:
				self.device = int(self.device)
			except ValueError:
				raise Exception("Incorrect device parameter")	 	

		if self.device < len(self.devices):
			# list of gates functions attribute to determine 
			# if msg should be passed (processed volume change) 
			self.funky_list = []
			if self.channel != None:
				self.funky_list.append(self.channel_gates)	
			if self.control != None:
				self.funky_list.append(self.control_gates)
			
			input = self.inputs.Input(self.device, 0)
			self.log_msg('Running using MIDI device: {}, max_vol: {}, filters: channel {} control {}'.format(
				self.devices[self.device][1], self.max_volume, self.channel, self.control))	

			# main loop for MIDI msg listening
			while True:				
				if input.poll():
					msg = input.read(1)
					self.set_volume_from_midi_msg(msg)
					if self.verbose:			
						self.log_msg(msg)
				time.sleep(0.005)
		else:
			raise Exception('"{}" input device not found'.format(self.device))
			
	def get_device_list(self):
		devices = []
		for dev in xrange(0, self.inputs.get_count()):
			devices.append(self.inputs.get_device_info(dev))	
		return devices

	def set_volume(self, val): #dev
		'''
		Sets volume of self.system_mixer
		'''
		if val > self.max_volume:
			val = self.max_volume	
		self.system_mixer.setvolume(val)

	def channel_gates(self, msg):
		'''
		Msg passes gates if channel is as needed
		'''
		return self.channel == msg[0][0][0]

	def control_gates(self, msg):
		'''
		Msg passes gates if control id is as needed
		'''
		return self.control == msg[0][0][1]

	def set_volume_from_midi_msg(self, msg):
		'''
		Set volume for main mixer from mido midi msg object
		'''	
		for funk in self.funky_list:
			if not funk(msg):
				return

		val = self.midi_to_volume(msg[0][0][2])
		self.set_volume(val)

	def log_msg(self, msg):
		'''
		Log msg with tag to console
		'''
		print '{} {}'.format(self.tag, str(msg))

	def midi_to_volume(self, value):
		'''
		Convert midi 0-127 values to 0-99 volume values
		'''
		volume = 0
		try:
			volume = int(value // 1.28)
		except Exception:
			print Exception
		return volume	

def assign_param(argv, param_name, param_value, convert_to_int=False):
	'''
	Return param value [idx + 1] if found in list, if not found returns unchanged
	Converts result to int if parameter supplied
	'''
	idx = None
	try:
		idx = argv.index(param_name)
	except ValueError:
		return param_value
	try:
		param_value = argv[idx + 1]
		if convert_to_int:
			try:
				param_value = int(param_value)
			except ValueError:
				pass
	except IndexError:
		pass
	return param_value

def display_help():
	'''
	Displays help info in the console for -h parameter
	'''
	help_content = []
	help_content.append('----------------------------------------------\n')
	help_content.append('Control system volume tool using MIDI messages\n')
	help_content.append('  Available parameters:\n')
	help_content.append('    -h Display help info\n')
	help_content.append('    -d MIDI device name or id  (default first available MIDI device)\n')
	help_content.append('       Can be integer value, which means # of available midi devices\n')
	help_content.append('    -l Returns list of all available MIDI devices\n')
	help_content.append('    -ch MIDI channel listen to 0-15 (default all)\n')
	help_content.append('    -ct MIDI control id to process, type int (default all ids)\n')
	help_content.append('    -m Max volume threshold 0-99 (default 30)\n')
	help_content.append('    -v Run in verbose mode\n')
	print ''.join(help_content)
	quit()

def display_devices():
	'''
	Displays all available MIDI devices seen by mido
	'''
	midi = pygame.midi
	midi.init()
	print 'List of available MIDI devices:'
	print '(interf, name, input, output, opened)'
	for dev in xrange(0, midi.get_count()):
		print midi.get_device_info(dev)
	quit()

def assign_params(midivol):
	'''
	Assign sys.argv params to midivol atrrbutes
	'''
	help_par = '-h'
	device_par = '-d'
	list_par = '-l'
	channel_par = '-ch'
	control_par = '-ct'
	maxvolume_par = '-m'
	verbose_par = '-v'

	if help_par in sys.argv:
		display_help()
	if list_par in sys.argv:
		display_devices()
	midivol.device = assign_param(sys.argv, device_par, midivol.device)
	midivol.channel = assign_param(sys.argv, channel_par, midivol.channel, True)
	midivol.control = assign_param(sys.argv, control_par, midivol.control, True)
	midivol.max_volume = assign_param(sys.argv, maxvolume_par, midivol.max_volume, True)
	if verbose_par in sys.argv:
		midivol.verbose = True

def main():
	'''
	Main method
	'''
	midivol = Midivol()
	assign_params(midivol)
	midivol.start()

if __name__ == "__main__":	
	main()

	