from base64 import b64decode
from itertools import combinations

CHARACTER_FREQ = {
    'a': 0.0651738, 'b': 0.0124248, 'c': 0.0217339, 'd': 0.0349835, 'e': 0.1041442, 'f': 0.0197881, 'g': 0.0158610,
    'h': 0.0492888, 'i': 0.0558094, 'j': 0.0009033, 'k': 0.0050529, 'l': 0.0331490, 'm': 0.0202124, 'n': 0.0564513,
    'o': 0.0596302, 'p': 0.0137645, 'q': 0.0008606, 'r': 0.0497563, 's': 0.0515760, 't': 0.0729357, 'u': 0.0225134,
    'v': 0.0082903, 'w': 0.0171272, 'x': 0.0013692, 'y': 0.0145984, 'z': 0.0007836, ' ': 0.1918182
}

def repeating_key_xor(plaintext, key):
    """Implements the repeating-key XOR encryption."""
    ciphertext = b''
    i = 0

    for byte in plaintext:
        ciphertext += bytes([byte ^ key[i]])

        # Cycle i to point to the next byte of the key
        i = i + 1 if i < len(key) - 1 else 0

    return ciphertext

def get_english_score(input_bytes):
    """Returns a score which is the sum of the probabilities in how each letter of the input data
    appears in the English language. Uses the above probabilities.
    """
    score = 0

    for byte in input_bytes:
        score += CHARACTER_FREQ.get(chr(byte).lower(), 0)

    return score


def singlechar_xor(input_bytes, key_value):
    """XORs every byte of the input with the given key_value and returns the result."""
    output = b''

    for char in input_bytes:
        output += bytes([char ^ key_value])

    return output


def singlechar_xor_brute_force(ciphertext):
    """Tries every possible byte for the single-char key, decrypts the ciphertext with that byte
    and computes the english score for each plaintext. The plaintext with the highest score
    is likely to be the one decrypted with the correct value of key.
    """
    candidates = []

    for key_candidate in range(256):
        plaintext_candidate = singlechar_xor(ciphertext, key_candidate)
        candidate_score = get_english_score(plaintext_candidate)

        result = {
            'key': key_candidate,
            'score': candidate_score,
            'plaintext': plaintext_candidate
        }

        candidates.append(result)

    # Return the candidate with the highest English score
    return sorted(candidates, key=lambda c: c['score'], reverse=True)[0]


def hamming_distance(binary_seq_1, binary_seq_2):
    """Computes the edit distance/Hamming distance between two equal-length strings."""
    assert len(binary_seq_1) == len(binary_seq_2)
    dist = 0

    for bit1, bit2 in zip(binary_seq_1, binary_seq_2):
        diff = bit1 ^ bit2
        dist += sum([1 for bit in bin(diff) if bit == '1'])

    return dist


def break_repeating_key_xor(binary_data):
    """Breaks the repeating key XOR encryption statistically."""
    normalized_distances = {}

    # For each key_size (from the suggested range)
    for key_size in range(2, 41):

        # Take the first four key_size worth of bytes (as suggested as an option)
        chunks = [binary_data[i:i + key_size] for i in range(0, len(binary_data), key_size)][:4]

        # Sum the hamming distances between each pair of chunks
        distance = 0
        pairs = combinations(chunks, 2)
        for (x, y) in pairs:
            distance += hamming_distance(x, y)

        # And compute the average distance
        distance /= 6

        # Normalize the result by dividing by key_size
        normalized_distance = distance / key_size

        # Store the normalized distance for the given key_size
        normalized_distances[key_size] = normalized_distance

    # The key_sizes with the smallest normalized edit distances are the most likely ones
    possible_key_sizes = sorted(normalized_distances, key=normalized_distances.get)[:3]
    possible_plaintexts = []

    # Now we can try which one is really the correct one among the top 3 most likely key_sizes
    for d in possible_key_sizes:
        key = b''

        # Break the ciphertext into blocks of key_size length
        for i in range(d):
            block = b''

            # Transpose the blocks: make a block that is the i-th byte of every block
            for j in range(i, len(binary_data), d):
                block += bytes([binary_data[j]])

            # Solve each block as if it was single-character XOR
            key += bytes([singlechar_xor_brute_force(block)['key']])

        # Store the candidate plaintext that we would get with the key that we just found
        possible_plaintexts.append((repeating_key_xor(binary_data, key), key))

    # Return the candidate with the highest English score
    return max(possible_plaintexts, key=lambda k: get_english_score(k[0]))


def main():

    # Check that the hamming distance function works properly
    assert hamming_distance(b'hello world!!', b'hacktheplanet') == 36

    with open("cipher.txt") as input_file:
        data = b64decode(input_file.read())

    # Compute and print the result of the attack
    result = break_repeating_key_xor(data)
    print("Key =", result[1].decode())
    print("---------------------------------------")
    print(result[0].decode().rstrip())


if __name__ == "__main__":
    main()