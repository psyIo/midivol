import sys
import time
import mido #python package for midi https://github.com/olemb/mido
from alsaaudio import Mixer

#linux using amixer (terminal command)
# from subprocess import call	
# call(["amixer", "-D", "pulse", "sset", "Master", "0%"])
# 'Launch Control MIDI 1'

class Midivol():
	'''
	Class used to control master volume mixer from midi input (mido) on linux alsa systems
	'''
	system_mixer = Mixer()
	tag ='Midivol: ' 

	def __init__(self, device_name='', max_volume=30, channel=None, control=None, verbose=False):
		self.device_name = device_name
		self.max_volume = max_volume
		self.channel = channel
		self.control = control
		self.verbose = verbose	

	def start(self):
		'''
		Finalize midivol and run main listening loop
		'''
		inputs = mido.get_input_names()			
		if not self.device_name:			
			if len(inputs) == 0:
				raise Exception('No available MIDI devices')
			else:
				self.device_name = inputs[0]
		else:
			try:
				dev_index = int(self.device_name)
				if len(inputs) >= dev_index:
					self.device_name = inputs[dev_index]
			except ValueError:
				pass		

		if self.device_name in inputs:					

			# list of gates functions attribute to determine 
			# if msg should be passed (processed volume change) 
			self.funky_list = [self.type_gates]
			if self.channel != None:
				self.funky_list.append(self.channel_gates)	
			if self.control != None:
				self.funky_list.append(self.control_gates)

			inport = mido.open_input(self.device_name)		
			self.log_msg('Running using MIDI device: {}, max_vol: {}, filters: channel {} control {}'.format(
				self.device_name, self.max_volume, self.channel, self.control))	

			# main loop for MIDI msg listening
			for msg in inport:
				self.set_volume_from_midi_msg(msg)
		else:
			raise Exception('"{}" input control not found'.format(self.control_name))

	def set_volume(self, val):
		'''
		Sets volume of self.system_mixer
		'''
		if val > self.max_volume:
			val = self.max_volume	
		if self.system_mixer.getvolume()[0] != val:
			self.system_mixer.setvolume(val)
			self.log_msg('Volume set to {}'.format(val))

	def type_gates(self, msg):
		'''
		Msg passes gates if type is as needed
		'''
		return msg.type == 'control_change'

	def channel_gates(self, msg):
		'''
		Msg passes gates if channel is as needed
		'''
		return self.channel == msg.channel

	def control_gates(self, msg):
		'''
		Msg passes gates if control id is as needed
		'''
		return self.control == msg.control

	def set_volume_from_midi_msg(self, msg):
		'''
		Set volume for main mixer from mido midi msg object
		'''	
		for funk in self.funky_list:
			if not funk(msg):
				return

		val = self.midi_to_volume(msg.value)
		self.set_volume(val)
		if self.verbose:			
			self.log_msg(msg)

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
	help_content.append('    -n MIDI device name (default first available MIDI device)\n')
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
	print 'List of available MIDI devices: ' + repr(mido.get_input_names())
	quit()

def assign_params(midivol):
	'''
	Assign sys.argv params to midivol atrrbutes
	'''
	help_par = '-h'
	name_par = '-n'
	list_par = '-l'
	channel_par = '-ch'
	control_par = '-ct'
	maxvolume_par = '-m'
	verbose_par = '-v'

	if help_par in sys.argv:
		display_help()
	if list_par in sys.argv:
		display_devices()
	midivol.device_name = assign_param(sys.argv, name_par, midivol.device_name)
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

	