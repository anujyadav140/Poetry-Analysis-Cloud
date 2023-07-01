import json
import os
from flask import Flask, jsonify, request
import syllapy as spy
import nltk
import pronouncing as pro
from nltk.corpus import cmudict, wordnet as wn
from flask_cors import CORS
import poetrytools

app = Flask(__name__)
CORS(app)
nltk.download('cmudict')
d = cmudict.dict()    
def syllable(word):
    try:
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except KeyError:
        #if word not found in cmudict
        return spy.count(word)

def rhyme(inp, level):
    entries = nltk.corpus.cmudict.entries()
    syllables = [(word, syl) for word, syl in entries if word == inp]
    rhymes = []
    for (word, syllable) in syllables:
             rhymes += [word for word, pron in entries if pron[-level:] == syllable[-level:]]
    return set(rhymes)

def doTheyRhyme(word1, word2):
    # first, we don't want to report 'glue' and 'unglue' as rhyming words
    # those kind of rhymes are LAME
    if word1.find(word2) == len(word1) - len(word2):
        return False
    if word2.find(word1) == len(word2) - len(word1): 
        return False

    return word1 in rhyme(word2, 1)

def doesItRhyme(word1, word2):
    if word1 in pro.rhymes(word2):
        return True
    else:
        return False

prondict = cmudict.dict()

def strip_letters(ls):
    #print "strip_letters"
    nm = ''
    for ws in ls:
        #print "ws",ws
        for ch in list(ws):
            #print "ch",ch
            if ch.isdigit():
                nm=nm+ch
                #print "ad to nm",nm, type(nm)
    return nm


def defineMetre(line):
    metre = ""
    tokens = [words.lower() for words in nltk.word_tokenize(line)] 
    punct = set([".", ",", "!", ":", ";", "'", ")", "(", "?"])
    word_list = []
    for t in tokens:
        if t not in punct:
            word_list.append(t)
    for word in word_list:
        if word in prondict:
            for s in prondict[word]:
                if strip_letters(s):
                    metre = metre + str(strip_letters(s))
                    break
        else:
            metre = metre + "x"
    return metre

@app.route('/', methods = ['GET', 'POST'])
def home():
    if(request.method == 'GET'):

        data = "keep grinding brah!!!"
        return jsonify({'data': data})

@app.route('/home/<int:num>', methods = ['GET'])
def disp(num):

    return jsonify({'data': num**2}) 

@app.route('/sylcount', methods = ['GET'])
def syllable_count():
    syl_check = str(request.args['query'])
    count = syllable(syl_check)
    return jsonify({'count': count})

# @app.route('/count/<string:word>', methods = ['GET'])
# def calculate_syllables(word):
#     count = spy.count(word)
#     return jsonify({'count': count})


@app.route('/rhyme/<string:word1>/<string:word2>', methods = ['GET'])
def rhymeOrNot(word1, word2):
    check1 = doTheyRhyme(word1, word2)
    check2 = doesItRhyme(word1, word2)
    isRhyme = False
    if check1 or check2:
        isRhyme = True
        return jsonify({'rhyme': isRhyme})
    else:
        return jsonify({'rhyme': isRhyme})

@app.route('/rhymes', methods = ['GET'])
def rhymes():
    word1 = request.args.get('word1')
    word2 = request.args.get('word2')
    isRhyme = doesItRhyme(word1, word2)
    return jsonify({'rhyme': isRhyme})


@app.route('/meanings', methods = ['GET'])
def meanings():
    word_token = request.args.get('word')
    meanings = []
    for m in wn.synsets(word_token):
        list_of_meanings = m.definition()
        meanings.append(list_of_meanings)
    return jsonify({'meanings': meanings})


@app.route('/meter', methods = ['GET'])
def findMetre():
    poem = request.args.get('lines')
    meter = defineMetre(poem)
    if meter:
        return jsonify({'meter': meter})
    else:
        return jsonify({'meter': 'empty ...'})

def guessForm(line):
    lines = poetrytools.tokenize(line)
    form = poetrytools.guess_form(lines, verbose=True)
    return form

@app.route('/analysis', methods = ['POST'])
def findAnalysis():
    lines = request.get_json()
    poem = '\n'.join(lines)
    form = guessForm(poem)
    if form:
        return jsonify({'form': form})
    else:
        return jsonify({'form': 'empty form ...'})
    

@app.route('/poetry-analysis', methods = ['POST'])
def poetryAnalysis():
    poem = request.get_json()
    form = guessForm(poem)
    if form:
        return jsonify({'form': form})
    else: 
        return jsonify({'form': 'empty form ...'})

if __name__ == "__main__":

    app.run(host="127.0.0.1", port=8080, debug=True)