# midivol
Program used to control OS master channel volume level using received MIDI messages

requirements:

    ++linux:
    mido https://github.com/olemb/mido

    ++windows:
    nircmd http://www.nirsoft.net/utils/nircmd.html
    pygame.midi
        +for service_win pywin32 https://sourceforge.net/projects/pywin32/
            +service usage:
            python service_win.py install
            python service_win.py start
            +Assign device_name in main() method of your desired midi input name
