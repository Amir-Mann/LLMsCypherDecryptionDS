import os
import sys
import random
import argparse

BASE_QUESTION_TEMPLATE = """I have a secret message.
I used the following encryption methods:
{encryption_methods}
And finally got this encrypted result:
{encrypted_msg}
Can you help me decipher the original message?
"""

BASE_ANSWER_TEMPLATE = """Let's decipher it step by step:
{step_by_step_decryption}
So the original message was:
{original_message}
"""

STEP_BY_STEP_DECRYPTION_FORMAT = "After the decrypting the {i}. step, we get:\n{decryption_step}"

LENGTHS_ALLOWED = [
    6, 12
]
global_add_spaces_between_chars = []


def random_gibberish_message():
    num_chars = random.choice(LENGTHS_ALLOWED)
    msg = ""
    for _ in range(num_chars):
        msg += chr(random.randint(ord("a"), ord("z")))
    return msg


class EncryptionMethod:

    def __init__(self, description, func, inv_func, param=None, characterwise=False, assertions_to_make=5):
        self.description = description
        self.func = func
        self.inv_func = inv_func
        self.param = param
        self.characterwise = characterwise
        for _ in range(assertions_to_make):
            test_msg = random_gibberish_message()
            if self.decrypt_msg(self.encrypt_msg(test_msg)) != test_msg:
                print(self)
                print(f"Failed sanity check for {test_msg=}, {self.encrypt_msg(test_msg)=}, {self.decrypt_msg(self.encrypt_msg(test_msg))=}.")

    def encrypt_msg(self, msg):
        if self.characterwise:
            encrypted = ""
            for c in msg:
                encrypted += self.func(c) if self.param is None else self.func(c, self.param)
        else:
            encrypted = self.func(msg) if self.param is None else self.func(msg, self.param)
        return encrypted

    def decrypt_msg(self, msg):
        if self.characterwise:
            decrypted = ""
            for c in msg:
                decrypted += self.inv_func(c) if self.param is None else self.inv_func(c, self.param)
        else:
            decrypted = self.inv_func(msg) if self.param is None else self.inv_func(msg, self.param)
        return decrypted

    def __str__(self):
        sample = ' '.join(list("abciotgeuzxy")) if global_add_spaces_between_chars else "abciotgeuzxy"
        encrypted = self.encrypt_msg('abciotgeuzxy')
        if global_add_spaces_between_chars:
            encrypted = ' '.join(list(encrypted))
        return f"{self.description} For example {sample} becomes {encrypted}"




ORDERS = [
    [0, 2, 1],
    [1, 0, 2],
    [1, 2, 0],
    [2, 0, 1],
    [2, 1, 0]
]

def permutations_cipher(string, order):
    order = ORDERS[order]
    reorderd = [c for c in string]
    for base in range(0, len(string), len(order)):
        for old, new in enumerate(order):
            reorderd[base + new] = string[base + old]
    return "".join(reorderd)

def permutations_cipher_revese(string, order):
    for _ in range(5):
        string = permutations_cipher(string, order)
    return string

ENCRYPTION_METHODS_GROUPS = [
    [
        EncryptionMethod(
            f"Permutation cipher in which charceters (0, 1, 2) move to positions ({', '.join(map(str, ORDERS[order]))}) respectively.",
            permutations_cipher,
            permutations_cipher_revese,
            param=order
        )
        for order in range(5)
    ],
    [
        EncryptionMethod(
            f"Shift and increment cipher with a base of {i}, shifting every letter to the one ({i} + position) after it in the ABC cyclically.",
            lambda string, offset: "".join([chr(ord("a") + ((ord(char) - ord("a") + offset + pos) % 26 )) for pos, char in enumerate(string)]),
            lambda string, offset: "".join([chr(ord("a") + ((ord(char) - ord("a") - offset - pos) % 26 )) for pos, char in enumerate(string)]),
            param=i
        )
        for i in range(0, 10)
    ],
    [
        EncryptionMethod(
            f"Caesar cipher or shift cipher with a distance of {i}, shifting every letter to the one {i} after it in the ABC cyclically.",
            lambda char, offset: chr(ord("a") + ((ord(char) - ord("a") + offset) % 26 )),
            lambda char, offset: chr(ord("a") + ((ord(char) - ord("a") - offset) % 26 )),
            param=i,
            characterwise=True
        )
        for i in range(1, 25)
    ],
    [
        EncryptionMethod(
            "Swapping adjacent characters, first one swaps with second one, third with forth and so on.",
            lambda string: "".join(string[i + (-1) ** i] for i in range(2*int(len(string)/2))) + (string[-1] if len(string) % 2 else ""),
            lambda string: "".join(string[i + (-1) ** i] for i in range(2*int(len(string)/2))) + (string[-1] if len(string) % 2 else "")
        ),
        EncryptionMethod(
            "Inverse order, reading the message from end to start.",
            lambda string: string[::-1],
            lambda string: string[::-1]
        ),
        EncryptionMethod(
            "Swapping first half of the message with the second half.",
            lambda string: string[int(len(string) / 2):] + string[:int(len(string) / 2)],
            lambda string: string[int(len(string) / 2):] + string[:int(len(string) / 2)]
        )
    ]
]
"""
UNUSED ENCRYPTIONS:
,
    [
        EncryptionMethod(
            f"Swapping all '{char_1}' with '{char_2}' and all '{char_2}' with '{char_1}'",
            lambda string: string.replace(char_1, "\127").replace(char_2, char_1).replace("\127", char_2),
            lambda string: string.replace(char_1, "\127").replace(char_2, char_1).replace("\127", char_2)
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
        encrypted_stages.append(cypher.encrypt_msg(encrypted_stages[-1]))
    
    #Question
    encryption_methods = "\n".join([f"{i+1}. {cypher}" for i, cypher in enumerate(cyphers)])

    question = BASE_QUESTION_TEMPLATE.format(
        encryption_methods=encryption_methods,
        encrypted_msg=' '.join(list(encrypted_stages[-1])) if args.add_spaces_between_chars else encrypted_stages[-1]
    )
    
    #Answer
    step_by_step_decryption = "\n".join([
        STEP_BY_STEP_DECRYPTION_FORMAT.format(i=i+1, decryption_step=(' '.join(list(msg)) if args.add_spaces_between_chars else msg)) 
        for i, msg in list(enumerate(encrypted_stages))[-2::-1] # [a, b, c, d] -> [(2, c), (1, b), (0, a)]
    ])
    
    answer = BASE_ANSWER_TEMPLATE.format(
        step_by_step_decryption=step_by_step_decryption,
        original_message=(' '.join(list(msg)) if args.add_spaces_between_chars else msg)
    )
    print(f"QUESTION:\n{question}\n\nANSWER:\n{answer}")


def main():
    parser = argparse.ArgumentParser(prog='Children cipher decipherment Dataset Question generator')
    parser.add_argument('--cyphers_per_question', type=int, default=2,
                        help='Base amount of cyphers per question')
    parser.add_argument('--cyphers_ammount_variation', type=int, default=0,
                        help='Maximum amount of cyphers to add on the base amount')
    parser.add_argument('--questions_to_generate', type=int, default=80,
                        help='Amount of questions to generate')
    parser.add_argument('--message_mode', type=str, default="gibberish",
                        help='Which mode to generate message in', choices=["gibberish"])
    parser.add_argument('--add_spaces_between_chars', type=bool, default=True,
                        help='Should we have spaces between chars in the message / decryption (for transformers ease): "abc" vs "a b c"')
    args = parser.parse_args()
    if args.add_spaces_between_chars:
        global_add_spaces_between_chars.append(None)
    for question_num in range(args.questions_to_generate):
        generate_question(args)

if __name__ == "__main__":
    main()
