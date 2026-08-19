import torch

from seq2seq_model import Encoder, Decoder


VOCAB_SIZE = 2000

encoder = Encoder(
    input_dim=VOCAB_SIZE,
    embedding_dim=128,
    hidden_dim=256,
)

decoder = Decoder(
    output_dim=VOCAB_SIZE,
    embedding_dim=128,
    hidden_dim=256,
)

src = torch.randint(
    0,
    VOCAB_SIZE,
    (2, 7)
)

hidden, cell = encoder(src)

first_token = torch.tensor([1, 1])

prediction, hidden, cell = decoder(
    first_token,
    hidden,
    cell
)

print("Prediction Shape :", prediction.shape)
print("Hidden Shape     :", hidden.shape)
print("Cell Shape       :", cell.shape)