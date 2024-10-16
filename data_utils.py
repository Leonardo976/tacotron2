import random
import numpy as np
import torch
import torch.utils.data
import layers
from utils import load_wav_to_torch, load_filepaths_and_text
from text import text_to_sequence
from torchaudio.transforms import Resample

class TextMelLoader(torch.utils.data.Dataset):
    def __init__(self, audiopaths_and_text, hparams):
        self.audiopaths_and_text = load_filepaths_and_text(audiopaths_and_text)  # Asegúrate de que esta función sea adecuada para español
        self.text_cleaners = hparams.text_cleaners
        self.max_wav_value = hparams.max_wav_value
        self.sampling_rate = hparams.sampling_rate
        self.load_mel_from_disk = hparams.load_mel_from_disk
        self.stft = layers.TacotronSTFT(
            hparams.filter_length, hparams.hop_length, hparams.win_length,
            hparams.n_mel_channels, hparams.sampling_rate, hparams.mel_fmin,
            hparams.mel_fmax)
        random.seed(hparams.seed)
        random.shuffle(self.audiopaths_and_text)

    def get_mel_text_pair(self, audiopath_and_text):
        audiopath, text = audiopath_and_text[0], audiopath_and_text[1]
        text = self.get_text(text)
        mel = self.get_mel(audiopath)
        return (text, mel)

    def get_mel(self, filename):
        try:
            # Cargar el archivo de audio y la tasa de muestreo
            audio, sampling_rate = load_wav_to_torch(filename)
            
            # Realizar resampling si la tasa de muestreo no es la esperada
            if sampling_rate != self.stft.sampling_rate:
                print(f"Resampleando {filename} de {sampling_rate}Hz a {self.stft.sampling_rate}Hz")
                resample_transform = Resample(orig_freq=sampling_rate, new_freq=self.stft.sampling_rate)
                audio = resample_transform(audio)
            
            # Normalizar el audio
            audio_norm = audio / self.max_wav_value
            audio_norm = torch.clamp(audio_norm, min=-1.0, max=1.0)  # Limitar a [-1, 1]
            audio_norm = audio_norm.unsqueeze(0)
            audio_norm = torch.autograd.Variable(audio_norm, requires_grad=False)
            
            # Generar el espectrograma Mel
            melspec = self.stft.mel_spectrogram(audio_norm)
            melspec = torch.squeeze(melspec, 0)
            
            return melspec

        except FileNotFoundError:
            print(f"Archivo no encontrado: {filename}")
            raise
        except IndexError as e:
            print(f"Error de índice al procesar {filename}: {e}")
            raise
        except Exception as e:
            print(f"Error al procesar el archivo {filename}: {e}")
            raise

    def get_text(self, text):
        # Normaliza el texto; asegúrate de que text_cleaners sea adecuado para español
        text_norm = torch.IntTensor(text_to_sequence(text, self.text_cleaners))
        return text_norm

    def __getitem__(self, index):
        return self.get_mel_text_pair(self.audiopaths_and_text[index])

    def __len__(self):
        return len(self.audiopaths_and_text)

class TextMelCollate():
    def __init__(self, n_frames_per_step):
        self.n_frames_per_step = n_frames_per_step

    def __call__(self, batch):
        input_lengths, ids_sorted_decreasing = torch.sort(
            torch.LongTensor([len(x[0]) for x in batch]),
            dim=0, descending=True)
        max_input_len = input_lengths[0]

        text_padded = torch.LongTensor(len(batch), max_input_len)
        text_padded.zero_()
        for i in range(len(ids_sorted_decreasing)):
            text = batch[ids_sorted_decreasing[i]][0]
            text_padded[i, :text.size(0)] = text

        num_mels = batch[0][1].size(0)
        max_target_len = max([x[1].size(1) for x in batch])
        if max_target_len % self.n_frames_per_step != 0:
            max_target_len += self.n_frames_per_step - max_target_len % self.n_frames_per_step
            assert max_target_len % self.n_frames_per_step == 0

        mel_padded = torch.FloatTensor(len(batch), num_mels, max_target_len)
        mel_padded.zero_()
        gate_padded = torch.FloatTensor(len(batch), max_target_len)
        gate_padded.zero_()
        output_lengths = torch.LongTensor(len(batch))
        for i in range(len(ids_sorted_decreasing)):
            mel = batch[ids_sorted_decreasing[i]][1]
            mel_padded[i, :, :mel.size(1)] = mel
            gate_padded[i, mel.size(1)-1:] = 1
            output_lengths[i] = mel.size(1)

        return text_padded, input_lengths, mel_padded, gate_padded, output_lengths
