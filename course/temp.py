
words = {'one':'num','two':'num','coutch':'furnature','three':'num','apple':'fruit'}

for word,type in words.copy().items():
    if type != 'num':
        print('found ',type)
        del words[word]

print(words)
