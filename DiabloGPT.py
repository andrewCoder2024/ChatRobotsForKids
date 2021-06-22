from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer_dialogue = AutoTokenizer.from_pretrained("microsoft/DialoGPT-large")
dialogue = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")


class Chat:
    def __init__(self):
        self.step = 0
        self.txt_input = ""
        self.bot_input_ids = ""
        self.chat_history_ids = ""
        self.generated_text = ""

    def raw(self, text):
        self.txt_input = text
    def new_user_input(self):
        return tokenizer_dialogue.encode(self.txt_input + tokenizer_dialogue.eos_token, return_tensors='pt')

    def bot_input_id(self):
        self.bot_input_ids = torch.cat([self.chat_history_ids, Chat.new_user_input(self)],
                                       dim=-1) if self.step > 0 else Chat.new_user_input(self)

    def chat_history_id(self):
        self.chat_history_ids = dialogue.generate(self.bot_input_ids, max_length=1000,
                                                  pad_token_id=tokenizer_dialogue.eos_token_id)

    def generate_text(self):
        Chat.new_user_input(self)
        Chat.bot_input_id(self)
        Chat.chat_history_id(self)
        self.step+=1
        return "DialoGPT: {}".format(tokenizer_dialogue.decode(self.chat_history_ids[:, self.bot_input_ids.shape[-1]:][0], skip_special_tokens=True))

    step = 0
    txt_input = ""
    # Let's chat for 5 lines
    while txt_input != "bye":
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        txt_input = input(">> User:")
        new_user_input_ids = tokenizer_dialogue.encode(txt_input + tokenizer_dialogue.eos_token, return_tensors='pt')

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([chat_history_ids, new_user_input_ids], dim=-1) if step > 0 else new_user_input_ids

        # generated a response while limiting the total chat history to 1000 tokens,
        chat_history_ids = dialogue.generate(bot_input_ids, max_length=100000000,
                                             pad_token_id=tokenizer_dialogue.eos_token_id)
        # pretty print last ouput tokens from bot
        print("DialoGPT: {}".format(tokenizer_dialogue.decode(chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)))
        step += 1
