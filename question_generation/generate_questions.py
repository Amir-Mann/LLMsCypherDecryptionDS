import os
import sys
import random
import argparse


BASE_QUESTION_TEMPLATE = """I have a secret message.
I used the following encryption methods:
{encryption_methods}
And finally got this encrypred result:
{encrypted_msg}
Can you help me decypher the original message?
"""

BASE_ANSWER_TEMPLATE = """Let's decrypt it step by step:
{step_by_step_decryption}
So the original message was:
{original_message}
"""

STEP_BY_STEP_DECRYPTION_FORMAT = "After the decrypting the {i}. step, we get:\n{decryption_step}"

BASE_FOR_MSG_LENGTH = 1.35
MIN_EXP_FOR_MSG_LENGTH = 4
MAX_EXP_FOR_MSG_LENGTH = 13

def random_gibberish_message():
    num_chars = int(BASE_FOR_MSG_LENGTH ** random.randint(MIN_EXP_FOR_MSG_LENGTH, MAX_EXP_FOR_MSG_LENGTH))
    if num_chars % 2:
        num_chars += 1
    msg = ""
    for _ in range(num_chars):
        msg += chr(random.randint(ord("a"), ord("z")))
    return msg
    

class EncryptionMethod:
    
    def __init__(self, description, func, inv_func, charecterwise=False, assertions_to_make=5):
        self.description = description
        self.func = func
        self.inv_func = inv_func
        self.charecterwise = charecterwise 
        for _ in range(assertions_to_make):
            test_msg = random_gibberish_message()
            if self.decrypt_msg(self.encrypet_msg(test_msg)) != test_msg:
                print(self)
                print(f"Failed sanety check for {test_msg=}, {self.encrypet_msg(test_msg)=}, {self.decrypt_msg(self.encrypet_msg(test_msg))=}.")
    
    def encrypet_msg(self, msg):
        if self.charecterwise:
            encrypted = ""
            for c in msg:
                encrypted += self.func(c)
        else:
            encrypted = self.func(msg)
        return encrypted
    
    def decrypt_msg(self, msg):
        if self.charecterwise:
            decrypted = ""
            for c in msg:
                decrypted += self.inv_func(c)
        else:
            decrypted = self.inv_func(msg)
        return decrypted
    
    def __str__(self):
        return f"{self.description} For example abcioeuzxy becomes {self.encrypet_msg('abcioeuzxy')}"

ENCRYPTION_METHODS_GROUPS = [
    [
        EncryptionMethod(
            f"Caesar cipher or shift cipher with a distance of {i}, shifting every letter to the one {i} after her cyclically.",
            lambda char: chr(ord("a") + ((ord(char) - ord("a") + i ) % 26 )),
            lambda char: chr(ord("a") + ((ord(char) - ord("a") - i ) % 26 )),
            charecterwise=True
        )
        for i in range(-12, 14)
    ],
    [
        EncryptionMethod(
            "Swapping adjaset charecters, First one swaps with second one, third with forth and so on. ",
            lambda string: "".join(string[i + (-1) ** i] for i in range(2*int(len(string)/2))) + (string[-1] if len(string) % 2 else ""),
            lambda string: "".join(string[i + (-1) ** i] for i in range(2*int(len(string)/2))) + (string[-1] if len(string) % 2 else "")
        ),
        EncryptionMethod(
            "Inverse order, reading the message from end to start. ",
            lambda string: string[::-1],
            lambda string: string[::-1]
        ),
        EncryptionMethod(
            "Swapping first half of the message with the second half. ",
            lambda string: string[int(len(string) / 2):] + string[:int(len(string) / 2)],
            lambda string: string[int(len(string) / 2):] + string[:int(len(string) / 2)]
        )
    ]
]
""",
    [
        EncryptionMethod(
            f"Swapping all '{char_1}' with '{char_2}' and all '{char_2}' with '{char_1}'",
            lambda string: string.replace(char_1, "\127").replace(char_2, char_1).replace("\127", char_1),
            lambda string: string.replace(char_1, "\127").replace(char_2, char_1).replace("\127", char_1)
        )
        for char_1 in "aouiey" for char_2 in "aouiey" if char_1 != char_2
    ]"""

def generate_question(args):
    amount_of_cyphers = args.cyphers_per_question + random.randint(0,  args.cyphers_ammount_variation)
    cyphers = [random.choice(random.choice(ENCRYPTION_METHODS_GROUPS)) 
               for _ in range(amount_of_cyphers)]
    if args.message_mode == "gibberish":
        msg = random_gibberish_message()
    
    encrypted_stages = [msg]
    for cypher in cyphers:
        encrypted_stages.append(cypher.encrypet_msg(encrypted_stages[-1]))
    
    question = BASE_QUESTION_TEMPLATE.format(
        encryption_methods="\n".join([f"{i+1}. {cypher}" for i, cypher in enumerate(cyphers)]),
        encrypted_msg=encrypted_stages[-1]
    )
    answer = BASE_ANSWER_TEMPLATE.format(
        step_by_step_decryption="\n".join([STEP_BY_STEP_DECRYPTION_FORMAT.format(i=i+1, decryption_step=msg) for i, msg in
                                           list(enumerate(encrypted_stages))[-2::-1]]), # [a, b, c, d] -> [(2, c), (1, b), (0, a)]
        original_message=msg
    )
    print(f"QUESTION:\n{question}\n\nANSWER:\n{answer}")


def main():
    parser = argparse.ArgumentParser(prog='Children cypher decryption Dataset Question generator')
    parser.add_argument('--cyphers_per_question', type=int, default=2,
                        help='Base amount of cyphers per question')
    parser.add_argument('--cyphers_ammount_variation', type=int, default=0,
                        help='Maximum amount of cyphers to add on the base amount')
    parser.add_argument('--questions_to_generate', type=int, default=80,
                        help='Amount of questions to generate')
    parser.add_argument('--message_mode', type=str, default="gibberish",
                        help='Which mode to generate message in', choices=["gibberish"])
    args = parser.parse_args()
    for question_num in range(args.questions_to_generate):
        generate_question(args)

if __name__ == "__main__":
    main()