#! /usr/bin/env python
# -*- coding: utf-8 -*-
from vad import sec2samples, get_segments_energy, get_vad_mask, compress_mask, get_vad_segments, get_max_duration
import numpy as np
import os
import subprocess
import telebot
import config
import shutil

from scipy.io.wavfile import read, write

import librosa
import pickle

bot = telebot.TeleBot(config.TOKEN)
root = os.getcwd() + "/dataset/"

PATH = 'inference'
PATH_OGG = 'inference/ogg'
PATH_WAV = 'inference/wav'
PATH_SPLITTED = 'inference/splitted'

#my_dict = { 0: 'нөл', 1: 'бір', 2: 'екі', 3: 'үш', 4: 'төрт', 5: 'бес', 6: 'алты', 7: 'жеті', 8: 'сегіз', 9: 'тоғыз' }

def save_ogg(ogg_data, ogg_path):
    with open(ogg_path, "wb") as file:
        file.write(ogg_data)


def convert_ogg_wav(ogg_path, dst_path):
    rate = 48000
    cmd = f"ffmpeg -i {ogg_path} -ar {rate} {dst_path} -y -loglevel panic"
    with subprocess.Popen(cmd.split()) as p:
        try:
            p.wait(timeout=2)
        except:
            p.kill()
            p.wait()
            return "timeout"

def vad(wav_file_path, file_name):
	segment_hop_sec = 0.1
	vad_threshold = 0.02
	sample_rate, audio = read(wav_file_path)

	segment_duration_samples = sec2samples(segment_hop_sec, sample_rate)
	segments = get_vad_segments(audio, sample_rate, segment_hop_sec, vad_threshold)
	print(len(segments))
	max_duration_sec = get_max_duration(segments, sample_rate, segment_hop_sec)
	if max_duration_sec > 0.8:
		print(f"max_duration_sec={max_duration_sec:.3f}")
	position = 0
	answer = []
	for segment in segments:
		wav_path_after_vad = f"{PATH_SPLITTED}/{file_name}#{position}.wav"
		start_samples = segment.start * segment_duration_samples
		stop_samples = segment.stop * segment_duration_samples
		print(wav_path_after_vad, start_samples, stop_samples)
		write(wav_path_after_vad, sample_rate, audio[start_samples:stop_samples])
		position += 1
		answer.append(predict(wav_path_after_vad))
	return answer

def predict(wav_path_after_vad):
    filename = "models/model.pkl"
    with open(filename, 'rb') as f:
    	model_pickled = f.read()
    model = pickle.loads(model_pickled)
    sample_rate, audio = read(wav_path_after_vad)
    max_duration_sec = 0.8
    max_duration = int(max_duration_sec * sample_rate + 1e-6)
    if len(audio) < max_duration:
    	audio = np.pad(audio, (0, max_duration - len(audio)), constant_values=0)
    feature = librosa.feature.melspectrogram(audio.astype(float), sample_rate, n_mels=16, fmax=1000)
    features_flatten = feature.reshape(-1)
    answer = model.predict([features_flatten])[0]
    return answer


@bot.message_handler(commands = ['start'])
def welcome(message):
	bot.send_message(message.from_user.id, 'Сәлем, дос! Мен - {1.first_name}!, сандарды ажырататын бот. \n Жалғастыру үшін /alga бас \n'.format(message.from_user, bot.get_me()),
		parse_mode = 'html')


@bot.message_handler(content_types=['text'], commands=['alga'])
def get_text_messages(message):
    user = message.from_user.id
    text = message.text

    bot.send_message(user,
        f"Say numbers")

@bot.message_handler(content_types=['voice'])
def get_voice_messages(message):
	user = message.from_user.id
	voice = message.voice
	tele_file = bot.get_file(voice.file_id)
	ogg_data = bot.download_file(tele_file.file_path)
	file_name = user
	ogg_path = PATH_OGG + "/" + str(file_name) + ".ogg"
	wav_path = PATH_WAV + "/" + str(file_name) + ".wav"
	save_ogg(ogg_data, ogg_path)
	convert_ogg_wav(ogg_path, wav_path)
	answer = vad(wav_path, file_name)
	number = 0

	while os.path.isfile("{PATH_SPLITTED}/{file_name}#{number}.wav"):
		os.remove("{PATH_SPLITTED}/{file_name}#{position}.wav")
		number += 1
	# shutil.rmtree(PATH_SPLITTED)
	bot.send_message(user, "Your numbers " + str(answer) + ". One more?")


if __name__ == "__main__":
	if not os.path.exists(PATH_OGG):
		os.makedirs(PATH_OGG)
	if not os.path.exists(PATH_WAV):
		os.makedirs(PATH_WAV)
	if not os.path.exists(PATH_SPLITTED):
		os.makedirs(PATH_SPLITTED)
	bot.polling(none_stop=True, interval=0)
