============================
pyjf3
============================

Utility functions to manipulate Japanese texts.

Requirements
============

* Python 3.3 or later

Functions
=============

guess(s)
-----------

文字列 s のエンコーディングを推測する。戻り値は UNKNOWN, ASCII, SJIS, EUC, JIS, UTF8, UTF16_LE, UTF16_BE のいずれかとなる。 UTF16_LE と UTF16_BE は、文字列の先頭にBOMが付与されている場合のみ検出される。

sjistojis(s), sjistoeuc(s), euctosjis(s), euctojis(s), jistosjis(s), jistoeuc(s)
--------------------------------------------------------------------------------

文字列 s を、異なるエンコーディングに変更する。

kanatohalf(ustr), kanatofull(ustr)
------------------------------------

Unicode文字列 ustr に含まれるカタカナ・句読点等を、半角<->全角に変換する。


tohalf(ustr), tofull(ustr)
------------------------------

Unicode文字列 ustr に含まれるカタカナ・句読点等以外の、cp932に含まれる文字を、半角<->全角に変換する。

getnengo(y, m, d, letter=False)
---------------------------------

y年m月d日の年号と年のタプルを返す。letter=Trueの場合は年号としてH/S/T/Mのいずれかを返す。

heiseitoyear(y), showatoyear(y), taishoyear(y), meijitoyear(y)
------------------------------------------------------------------

平成、昭和、大正、明治の年から、西暦を返す。

wrap(ustr, maxcol)
---------------------------

Unicode文字列 ustr を、maxcol桁の文字列に分割する。ワードラップ・行頭禁則対応。



Copyright 
=========================

Copyright (c) 2013 Atsuo Ishimoto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


