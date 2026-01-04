#이유성 연습장
#너희도 하나씩 만들어서 써

f , s, t = map(int,input().split())

if f == s == t:
    print(10000+f*1000)
if f == s != t or f == t != s or s == t != f:
    if f == s:
        d = f
    if f == t:
        d = f
    if s == t:
        d = s
    print(1000 + d*100)
if f != s and s != t and f != t:
    if f < s :
        n = s
    else:
        n = f
    if n < t:
        n = t
    print(100*n)
        
 
    
   