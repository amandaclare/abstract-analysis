"""Counts word frequencies in titles and abstracts in a CSV file downloaded from Web Of Science""" 
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import nltk
import io
import csv

def read_abs_csv(filename, abss):
    """Read titles and abstracts from a CSV file, adding them to the given list"""
    with io.open(filename, encoding='utf-8') as fi:
        csvreader = csv.reader(fi, delimiter='\t')
        next(csvreader) # skip header line
        for row in csvreader:
            title = row[8].strip()
            abstract = row[21].strip()
            year = int(row[44].strip())
            abss.append((title, abstract, year))


def get_tag_type(tagtype, pairs): 
    """
    Given a list of (word,tag) pairs, return a list of words which are tagged as nouns/verbs/etc
    The tagtype could be 'NN', 'JJ', 'VB', etc
    """
    return [w for (w, tag) in pairs if tag.startswith(tagtype)]            


def count_freqs(tagtype, texts, outfile):
    """Count words and stems from the texts and output them into outfile"""
    word_dict = {}
    stem_dict = {}
    for text in texts:
        if text is None:
            continue
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        nouns = get_tag_type(tagtype, tagged)
        stemmer = nltk.stem.PorterStemmer()
        # Collect stems and their orginal words, as pairs
        stems = [(stemmer.stem(token).lower(), token.lower()) for token in nouns]
        
        # Count them into a dictionary
        for (stem, word) in stems:
            if len(word) == 1:
                continue  # ignore 1-char words
            if stem in stem_dict:
                stem_dict[stem] += 1
                word_dict[stem].append(word)
            else:
                stem_dict[stem] = 1
                word_dict[stem] = [word]

    # Sort all stems by freq, largest first
    freqs = sorted(stem_dict.items(), key = lambda x: x[1], reverse = True)

    # Output stems and words
    fo = open(outfile, mode="w")
    for (stem, count) in freqs:
        fo.write(stem)
        fo.write("\t")
        fo.write(str(count))
        fo.write("\t")
        fo.write(u",".join(list(set(word_dict[stem]))))
        fo.write("\n")
    fo.close()


def main():
    filename = sys.argv[1]

    abss = []
    read_abs_csv(filename, abss)

    # Titles
    count_freqs('JJ', [t for (t, a, y) in abss], "titlesAdjs_"+filename)

    # Abstracts
    count_freqs('JJ', [a for (t, a, y) in abss], "abstractsAdjs_"+filename)



if __name__ == "__main__":
    main()
