#!/usr/bin/env python
# -*- coding: utf-8 -*-
#@Time: 2018/6/30 21:51
#@Authore : gzq
#@File: test.py.py

dict1 = [{"upload":{"prot":"11"}}, {"upload1":{"port":"123"}}, {"uplaod2":{"port":"123"}}]
s = "uplaod2"
#print(dict1)
def t(s):
    for i in dict1:
        for se,d in i.items():
            if se == s:
                print(i)
            else:
                print("33")
                pass
t(s)