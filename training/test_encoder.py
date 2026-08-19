import torch

from seq2seq_model import Encoder


VOCAB_SIZE = 2000

encoder = Encoder(
    input_dim=VOCAB_SIZE,
    embedding_dim=128,
    hidden_dim=256,
)

sample = torch.randint(
    0,
    VOCAB_SIZE,
    (2, 7)
)

hidden, cell = encoder(sample)

print("Input Shape :", sample.shape)
print("Hidden Shape:", hidden.shape)
print("Cell Shape  :", cell.shape)