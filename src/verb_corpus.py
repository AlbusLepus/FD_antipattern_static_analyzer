#!/usr/bin/python
from nltk.corpus import wordnet as wn

def main():
  verbs = {x.name().split('.', 1)[0] for x in wn.all_synsets('v')}
  wf = open('verbs.txt', 'w')
  for word in verbs:
    wf.write(word + '\n')
  wf.close()

if __name__ == '__main__':
  main()