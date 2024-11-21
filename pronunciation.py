import subprocess
import sys
import random
import pandas as pd

# Function to decompose a Hangul syllable into its parts
def decompose_hangul(char):
    base = ord(char) - 0xAC00
    initial = base // 588
    medial = (base % 588) // 28
    final = base % 28
    return initial, medial, final

# Function to recompose the parts into a Hangul syllable
def recompose_hangul(initial, medial, final):
    return chr(0xAC00 + initial * 588 + medial * 28 + final)

# Define groups for allowed changes
initial_final_groups = [
    ['ㄱ', 'ㄲ', 'ㅋ', 'ㅇ', 'ㅎ'],
    ['ㅂ', 'ㅃ', 'ㅍ', 'ㅁ'],
    ['ㄷ', 'ㄸ', 'ㅌ', 'ㅅ', 'ㅆ'],
    ['ㅅ', 'ㅆ', 'ㅈ', 'ㅉ', 'ㅊ'],
    ['ㅈ', 'ㅉ', 'ㅊ'],
    ['ㄴ', 'ㄹ', 'ㅁ'],
    ['ㄷ', 'ㅂ'],
    ['ㅋ', 'ㅌ'],
    ['ㅍ', 'ㅋ', 'ㅌ'],
# 추가된 그룹들(단방향 패턴): ㅌ -> ㅊ / ㅍ -> ㅎ...
    ['ㅌ', 'ㅊ'],
    ['ㅍ', 'ㅎ'],
    ['ㄷ', 'ㄴ', 'ㄹ'],
]

medial_final_groups = [
    ['ㅣ', 'ㅟ', 'ㅡ', 'ㅜ'],
    ['ㅔ', 'ㅚ', 'ㅓ', 'ㅗ'],
    ['ㅐ', 'ㅏ']
]

# Comprehensive lists of initial, medial, and final sounds
initial_sounds = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
medial_sounds = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
final_sounds = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# 단방향 패턴인 4개 그룹 예외처리
def get_random_in_group(current_value, groups):
    # Check all groups the current_value belongs to
    matching_groups = [group for group in groups if current_value in group]

    if not matching_groups:
        return current_value  # Return original if no matching groups found

    # Randomly select one of the matching groups
    chosen_group = random.choice(matching_groups)

    # Check if the group is a one-way pattern
    if chosen_group in [['ㅌ', 'ㅊ'], ['ㅎ', 'ㄲ', 'ㅋ', 'ㅇ'], ['ㅍ', 'ㅎ'], ['ㄷ', 'ㄴ', 'ㄹ']]:
        # Ensure one-way behavior: change only if current_value is the first element
        if current_value == chosen_group[0]:
            group_without_current = chosen_group[1:]  # Exclude the current value from choices
            return random.choice(group_without_current)
        else:
            return current_value  # Return original if not allowed to change back
    else:
        # Regular behavior: pick a random value from the group, excluding current_value
        group_without_current = [item for item in chosen_group if item != current_value]
        if group_without_current:
            return random.choice(group_without_current)

    return current_value  # Default to original if no changes can be made

# Function to add noise to a selected component in a syllable using allowed groups
def add_noise_to_component(initial, medial, final, component_to_modify):
    try:
        if component_to_modify == 'initial':
            initial_char = initial_sounds[initial]
            initial_char = get_random_in_group(initial_char, initial_final_groups)
            initial = initial_sounds.index(initial_char)
        elif component_to_modify == 'medial':
            medial_char = medial_sounds[medial]
            medial_char = get_random_in_group(medial_char, medial_final_groups)
            medial = medial_sounds.index(medial_char)
        elif component_to_modify == 'final' and final > 0:
            final_char = final_sounds[final]
            final_char = get_random_in_group(final_char, initial_final_groups)
            final = final_sounds.index(final_char)
    except ValueError:
        pass  # If the component is not in the list, leave it unchanged
    return initial, medial, final

# Function to generate noisy variations of each word with a retry limit
def generate_noisy_variations(word_list, num_variations=15, max_retries=20):
    all_variations = {}
    cnt = 0
    for word in word_list:
        cnt += 1
        variations_set = set()
        retries = 0
        while len(variations_set) < num_variations and retries < max_retries:
            new_word = list(word)  # Convert to list for mutable syllables
            # Set number of syllables to modify, capped by the number of syllables in the word
            syllables_to_modify = random.sample(range(len(word)), k=min(random.choice([1, 2]), len(word)))
            for syllable_index in syllables_to_modify:
                char = new_word[syllable_index]
                if '가' <= char <= '힣':  # Only modify Hangul characters
                    initial, medial, final = decompose_hangul(char)
                    # Randomly choose which component to modify
                    component_to_modify = random.choice(['initial', 'medial', 'final'])
                    initial, medial, final = add_noise_to_component(initial, medial, final, component_to_modify)
                    new_word[syllable_index] = recompose_hangul(initial, medial, final)
            variations_set.add(''.join(new_word))
            retries += 1

        # Ensure we have exactly `num_variations` by duplicating existing variations if needed
        variations_list = list(variations_set)
        while len(variations_list) < num_variations:
            variations_list.append(random.choice(variations_list))

        # Add the variations to the output dictionary
        all_variations[f"{word}_{cnt}"] = variations_list

    return all_variations

#--------------------------------------------------------------------------------------------

# 발음 데이터 CSV 파일 생성 함수
def create_df(result, right_keywords, initial, output_filename="word_variations.csv"):
    word_variations = generate_noisy_variations(result)
    num_of_rows = min(len(word_variations), len(result))
    num_of_variations = 16

    # 데이터프레임 생성
    data = {'target': right_keywords[:num_of_rows], '발음1': result[:num_of_rows]}
    for i in range(1, num_of_variations):
        data[f'발음{i+1}'] = [variations[i-1] for variations in list(word_variations.values())[:num_of_rows]]
    
    df = pd.DataFrame(data)
    df['length'] = df['발음1'].str.len()
    df['initial'] = initial[:num_of_rows]

    # CSV 파일로 저장
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
