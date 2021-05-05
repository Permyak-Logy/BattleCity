from pydub import AudioSegment

# files
src = './bonus_created.mp3'
dst = src.replace(".mp3", ".wav")

# convert wav to mp3
sound = AudioSegment.from_mp3(src)
sound.export(dst, format="wav")
