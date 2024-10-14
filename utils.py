import os
import numpy as np
from scipy.io.wavfile import read
import torch


def get_mask_from_lengths(lengths):
    max_len = torch.max(lengths).item()
    ids = torch.arange(0, max_len, out=torch.cuda.LongTensor(max_len))
    mask = (ids < lengths.unsqueeze(1)).bool()
    return mask


def load_wav_to_torch(full_path):
    # Verificar si el archivo existe
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Archivo no encontrado: {full_path}")

    sampling_rate, data = read(full_path)
    return torch.FloatTensor(data.astype(np.float32)), sampling_rate


def load_filepaths_and_text(filename, split="|"):
    with open(filename, encoding='utf-8') as f:
        filepaths_and_text = [line.strip().split(split) for line in f]
    
    # Comprobar que cada línea contenga la ruta del archivo y el texto
    for filepath, text in filepaths_and_text:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Archivo no encontrado en la ruta: {filepath}")

    return filepaths_and_text


def to_gpu(x):
    x = x.contiguous()

    if torch.cuda.is_available():
        x = x.cuda(non_blocking=True)
    return torch.autograd.Variable(x)

