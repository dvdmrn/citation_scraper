l = [{'a':1,'p':0},{'b':0,'p':4},{'c':-1,'p':2},{'asdf':33,'p':2},{'asdf':33,'p':99},{'asdf':33,'p':2},{'asdf':36,'p':99}]


res = max(l,key=lambda x:x['p'])

print res