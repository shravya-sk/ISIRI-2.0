import torch
import torch.nn as nn


class Encoder(nn.Module):
    def __init__(
        self,
        input_dim,
        embedding_dim,
        hidden_dim,
        num_layers=1,
        dropout=0.2,
    ):
        super().__init__()

        self.embedding = nn.Embedding(input_dim, embedding_dim)

        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )

    def forward(self, src):

        embedded = self.embedding(src)

        outputs, (hidden, cell) = self.lstm(embedded)

        return hidden, cell


class Decoder(nn.Module):
    def __init__(
        self,
        output_dim,
        embedding_dim,
        hidden_dim,
        num_layers=1,
        dropout=0.2,
    ):
        super().__init__()

        self.embedding = nn.Embedding(output_dim, embedding_dim)

        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True,
        )

        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, input_token, hidden, cell):

        input_token = input_token.unsqueeze(1)

        embedded = self.embedding(input_token)

        output, (hidden, cell) = self.lstm(
            embedded,
            (hidden, cell)
        )

        prediction = self.fc(output.squeeze(1))

        return prediction, hidden, cell



class Seq2Seq(nn.Module):

    def __init__(self, encoder, decoder, device):
        super().__init__()

        self.encoder = encoder
        self.decoder = decoder
        self.device = device

    def forward(self, src, trg, teacher_forcing_ratio=0.5):

        batch_size = trg.shape[0]
        trg_len = trg.shape[1]
        vocab_size = self.decoder.fc.out_features

        outputs = torch.zeros(
            batch_size,
            trg_len,
            vocab_size
        ).to(self.device)

        hidden, cell = self.encoder(src)

        input_token = trg[:, 0]

        for t in range(1, trg_len):

            prediction, hidden, cell = self.decoder(
                input_token,
                hidden,
                cell
            )

            outputs[:, t] = prediction

            teacher_force = torch.rand(1).item() < teacher_forcing_ratio

            top1 = prediction.argmax(1)

            input_token = trg[:, t] if teacher_force else top1

        return outputs