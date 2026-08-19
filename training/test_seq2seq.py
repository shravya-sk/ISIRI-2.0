import torch

from seq2seq_model import Encoder, Decoder, Seq2Seq
from config import *


device = torch.device("cpu")

encoder = Encoder(
    input_dim=TULU_VOCAB_SIZE,
    embedding_dim=EMBEDDING_DIM,
    hidden_dim=HIDDEN_DIM,
)

decoder = Decoder(
    output_dim=ENGLISH_VOCAB_SIZE,
    embedding_dim=EMBEDDING_DIM,
    hidden_dim=HIDDEN_DIM,
)

model = Seq2Seq(
    encoder,
    decoder,
    device,
)

src = torch.randint(
    0,
    TULU_VOCAB_SIZE,
    (2, 8)
)

trg = torch.randint(
    0,
    ENGLISH_VOCAB_SIZE,
    (2, 8)
)

output = model(src, trg)

print("Source Shape :", src.shape)
print("Target Shape :", trg.shape)
print("Output Shape :", output.shape)