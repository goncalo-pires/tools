import sys, wave
from bitstring import *


def decompose(data):
    return list(map(lambda x: 1 if x else 0, list(BitArray(bytes=data))))


def disembed(audio_path, n_lsb, password, filename):
    audio = wave.open(audio_path, 'rb')
    audio_params = audio.getparams()
    n_frames = audio.getnframes()
    sample_width = audio.getsampwidth()
    sample_bits = sample_width * 8
    n_channels = audio.getnchannels()
    if n_channels != 1:
        print('[-] Currently, only wav files with one channel are supported. Try to convert your file.')
        exit()
    if n_lsb > sample_bits:
        print('[-] The sample width must not be smaller than the LSB to use.')
        sys.exit()
    usable_space = n_frames * n_lsb / 8 / 1024
    print('[*] Usable space in audio file: %.2f KB.' % usable_space)
    payload_bits = list()
    frames = audio.readframes(n_frames)
    audio.close()
    frames = [frames[i:i + sample_width] for i in range(0, len(frames), sample_width)]
    displacement = 0
    frame_id = 1
    stego_bits = []
    for frame in frames:
        frame_bits = decompose(frame)
        for j in range(n_lsb):
            if displacement < password:
                displacement += 1
                continue
            payload_bits.append(frame_bits[sample_bits - n_lsb + j])

        stego_bits += frame_bits
        frame_id += 1

    payload_bits = [str(i) for i in payload_bits]
    payload_bytes = [int(''.join(payload_bits[k:k+8]),2) for k in range(0, len(payload_bits), 8)]
    a = bytearray(payload_bytes)

    f=open(filename,"w+b")
    f.write(a)
    f.close()

    print('[+] Payload extracted successfully!')


def usage(prog_name):
    print(u'Ciber-Seguranc\u0327a Forense - Instituto Superior Te\u0301cnico / Universidade Lisboa')
    print('LSB steganography tool: hide files within least significant bits of mono (1 channel) wav sound files.\n')
    print('')
    print('Usage:')
    print('  %s  <wav_file> [password] [n_lsb] <outfile>' % prog_name)
    print('')
    print('  The password is optional and must be a number.')
    sys.exit()


if __name__ == '__main__':
    if len(sys.argv) < 5:
        usage(sys.argv[0])
    password = int(sys.argv[2]) % 13 if len(sys.argv) >= 3 else 0
    n_lsb = (int(sys.argv[3]) % 8) + 1
    file = sys.argv[4]
    disembed(sys.argv[1], n_lsb, password, file)
