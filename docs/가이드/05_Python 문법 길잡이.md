---
name: Python 문법 길잡이
purpose: 이 프로젝트를 코드로 짤 때 쓰는 Python 문법과 함수만 모아, C와 다른 점을 중심으로 예시와 함께 설명
type: 참고
applies_to: [fft-perfect-reconstruction]
maturity: experimental
tags: [python, 문법, 자료형, 리스트, 복소수, bytes, wave, struct, deque, pytest, 예시]
---

# Python 문법 길잡이

**TL;DR**: 이 프로젝트를 짤 때 쓰는 문법과 함수만 모았다. C와 다른 점(자료형 선언이 없다, 정수가 넘치지 않는다, 들여쓰기로 블록을 나눈다)부터 적었다. 맨 앞의 목차와 "하고 싶은 일로 찾기" 표에서 찾는다. 예시는 모두 실행해 확인했고, FFT·윈도우·겹쳐 더하기를 구현한 코드는 없다.

> [!NOTE]
> 예시의 출력은 [첨부_이력_문법 예시 실행 출력.txt](../tasks/가이드/20260928_1728_pr-guide-and-setup/첨부_이력_문법%20예시%20실행%20출력.txt)에 있다. 일반 문법(§1 ~ §11)의 예시는 과제와 무관한 값으로 적었다. 라이브러리 함수(§12 ~ §23)는 부르는 법까지만 보여 준다. 절차는 [04_구현 가이드라인.md](04_구현%20가이드라인.md)를 보고 직접 짠다. 막히는 문법이 있으면 대화로 물어보면 된다.

---

## 목차

**기초** — C와 다른 점부터

- [1. 실행, 출력, 주석, 들여쓰기](#1-실행-출력-주석-들여쓰기)
- [2. 자료형](#2-자료형)
  - [2.1 이 프로젝트에서 쓰는 자료형](#21-이-프로젝트에서-쓰는-자료형)
  - [2.2 선언 없이 정해지고, 다시 넣으면 바뀐다](#22-선언-없이-정해지고-다시-넣으면-바뀐다)
  - [2.3 자료형 바꾸기](#23-자료형-바꾸기)
  - [2.4 C와 다른 곳 — 넘침과 나눗셈](#24-c와-다른-곳--넘침과-나눗셈)
  - [2.5 크기가 정해진 리스트 — C의 배열 선언 자리](#25-크기가-정해진-리스트--c의-배열-선언-자리)
  - [2.6 자료형 적어 두기 (선택)](#26-자료형-적어-두기-선택)
- [3. 숫자와 연산](#3-숫자와-연산)
- [4. 리스트](#4-리스트)
  - [4.1 만들기와 꺼내기](#41-만들기와-꺼내기)
  - [4.2 슬라이싱, 일부 잘라 내기](#42-슬라이싱-일부-잘라-내기)
  - [4.3 만들기, 잇기, 붙이기](#43-만들기-잇기-붙이기)
  - [4.4 주의, 복사가 아니라 같은 리스트](#44-주의-복사가-아니라-같은-리스트)
- [5. 반복문](#5-반복문)
  - [5.1 for](#51-for)
  - [5.2 range](#52-range)
  - [5.3 번호와 값을 함께, 두 리스트를 함께](#53-번호와-값을-함께-두-리스트를-함께)
  - [5.4 while](#54-while)
- [6. 조건문](#6-조건문)
- [7. 함수](#7-함수)
- [8. 모듈과 import](#8-모듈과-import)
  - [8.1 실행 순서, C와 다른 점](#81-실행-순서-c와-다른-점)
- [9. 오류 다루기](#9-오류-다루기)
- [10. 리스트 내포](#10-리스트-내포)
- [11. 문자열 포맷과 시간 재기](#11-문자열-포맷과-시간-재기)

**단계별로 쓰는 것** — 라이브러리 함수

- [12. 복소수](#12-복소수)
  - [12.1 복소수의 기본](#121-복소수의-기본)
  - [12.2 복소 지수와 삼각 함수](#122-복소-지수와-삼각-함수)
- [13. math 모듈과 실수 비교](#13-math-모듈과-실수-비교)
- [14. 비트 연산과 2의 거듭제곱](#14-비트-연산과-2의-거듭제곱)
  - [14.1 비트 연산과 이진수](#141-비트-연산과-이진수)
  - [14.2 길이와 단계 수](#142-길이와-단계-수)
- [15. 바이트와 정수](#15-바이트와-정수)
  - [15.1 하나씩 바꾸기](#151-하나씩-바꾸기)
  - [15.2 여러 개를 한꺼번에 바꾸기](#152-여러-개를-한꺼번에-바꾸기)
- [16. WAV 파일](#16-wav-파일)
- [17. 버퍼](#17-버퍼)
- [18. 자리마다 계산하기](#18-자리마다-계산하기)
- [19. 반올림과 범위 자르기](#19-반올림과-범위-자르기)
- [20. 경로와 실행 인자](#20-경로와-실행-인자)
- [21. pytest로 시험하기](#21-pytest로-시험하기)
- [22. 검사 도구 testvec](#22-검사-도구-testvec)
- [23. numpy와 그래프 (선택)](#23-numpy와-그래프-선택)
  - [23.1 numpy 기본](#231-numpy-기본)
  - [23.2 그래프 기본](#232-그래프-기본)
  - [23.3 이 프로젝트에서 쓸 numpy와 그래프](#233-이-프로젝트에서-쓸-numpy와-그래프)

찾는 내용이 무엇을 하는 것인지 알면 [하고 싶은 일로 찾기](#하고-싶은-일로-찾기)에서 찾는다.

---

## 하고 싶은 일로 찾기

| 하고 싶은 일 | 절 | 단계 |
|---|---|---|
| 변수의 자료형을 정하거나 확인한다 | [§2.1](#21-이-프로젝트에서-쓰는-자료형), [§2.2](#22-선언-없이-정해지고-다시-넣으면-바뀐다) | 전체 |
| 크기가 정해진 리스트를 만든다 (C의 배열 선언 자리) | [§2.5](#25-크기가-정해진-리스트--c의-배열-선언-자리) | 단계_3, 단계_6, 단계_8 |
| 정수, 실수, 복소수를 서로 바꾼다 | [§2.3](#23-자료형-바꾸기) | 전체 |
| 16bit 범위를 넘는 값이 어떻게 되는지 안다 | [§2.4](#24-c와-다른-곳--넘침과-나눗셈) | 단계_9 |
| 함수에 자료형을 적어 둔다 | [§2.6](#26-자료형-적어-두기-선택) | 선택 |
| WAV 파일을 열어 채널 수, 샘플 폭, 샘플링 주파수를 읽는다 | [§16](#16-wav-파일) | 단계_1 |
| WAV에서 읽은 바이트를 정수 리스트로 바꾼다 | [§15](#15-바이트와-정수) | 단계_1 |
| 정수 리스트를 바이트로 바꿔 WAV에 쓴다 | [§15](#15-바이트와-정수), [§16](#16-wav-파일) | 단계_9 |
| 조건이 맞지 않으면 오류를 낸다 | [§9](#9-오류-다루기) | 단계_1 |
| 복소수를 만들고 실수부, 허수부, 켤레, 크기를 구한다 | [§12.1](#121-복소수의-기본) | 단계_2 ~ 단계_4 |
| $e^{j\theta}$(복소 지수)를 계산한다 | [§12.2](#122-복소-지수와-삼각-함수) | 단계_3 |
| 코사인을 계산한다 | [§12.2](#122-복소-지수와-삼각-함수), [§13](#13-math-모듈과-실수-비교) | 단계_5 |
| 길이가 2의 거듭제곱인지, 단계가 몇 개인지 구한다 | [§14.2](#142-길이와-단계-수) | 단계_3 |
| 인덱스의 비트를 뒤집는다 | [§14.1](#141-비트-연산과-이진수) | 단계_3 |
| 리스트의 일부를 잘라 낸다, 뒤집는다 | [§4.2](#42-슬라이싱-일부-잘라-내기) | 단계_3, 단계_6 |
| 리스트를 복사한다 (같은 리스트를 고치는 실수 피하기) | [§4.4](#44-주의-복사가-아니라-같은-리스트) | 단계_3 |
| 버퍼 앞 16개를 버리고 뒤에 16개를 붙인다 | [§17](#17-버퍼) | 단계_6 |
| 입력을 16개씩 나누고, 모자라면 0을 채운다 | [§17](#17-버퍼) | 단계_6 |
| 올림, 몫, 나머지를 구한다 | [§3](#3-숫자와-연산), [§13](#13-math-모듈과-실수-비교) | 단계_6, 단계_8 |
| 같은 자리끼리 곱한다 | [§10](#10-리스트-내포), [§18](#18-자리마다-계산하기) | 단계_7 |
| 위치를 옮겨 더한다 | [§18](#18-자리마다-계산하기) | 단계_8 |
| 반올림하고 −32768 ~ 32767로 자른다 | [§19](#19-반올림과-범위-자르기) | 단계_9 |
| 두 실수가 같은지 비교한다 | [§13](#13-math-모듈과-실수-비교) | 확인 |
| 경로를 잇고 출력 폴더를 만든다 | [§20](#20-경로와-실행-인자) | 단계_9 |
| 다른 파일의 함수를 불러온다 | [§8](#8-모듈과-import) | 전체 |
| `main` 함수가 언제 실행되는지 안다 | [§8.1](#81-실행-순서-c와-다른-점) | 전체 |
| 시험을 만든다 | [§21](#21-pytest로-시험하기) | 전체 |
| 결과를 테스트 벡터나 원본 WAV와 비교한다 | [§22](#22-검사-도구-testvec) | 단계_3 ~ 단계_10 |
| 걸린 시간을 잰다 | [§11](#11-문자열-포맷과-시간-재기) | 선택 |
| 그래프를 그린다 | [§23](#23-numpy와-그래프-선택) | 선택 |

---

## 1. 실행, 출력, 주석, 들여쓰기

**쓰는 곳**: 전체

```python
# '#' 뒤는 주석이다. 실행되지 않는다.
name = "홍길동"
print("안녕하세요", name)
print(1 + 2)
```

```text
안녕하세요 홍길동
3
```

- Python은 **들여쓰기**로 블록을 구분한다. `for`, `if`, `def` 아래의 줄은 공백 4칸을 들여 쓴다
- 변수는 선언 없이 값을 넣으면 생긴다
- 값이 바뀌지 않는 설정값은 이름을 대문자로 쓰는 관례가 있다 (예: `MAX_SCORE = 100`)

---

## 2. 자료형

**쓰는 곳**: 전체. C와 가장 다른 곳이다.

Python에는 **자료형 선언이 없다.** `int count;`처럼 미리 적지 않고, 값을 넣으면 그 값의 자료형이 그 변수의 자료형이 된다.

### 2.1 이 프로젝트에서 쓰는 자료형

```python
count = 3             # 정수
ratio = 0.5           # 실수
z = 3 + 4j            # 복소수
ok = True             # 참, 거짓
name = "sample"       # 문자열
raw = b'\x01\x02'     # 바이트
items = [1, 2, 3]     # 리스트
pair = (1, 2)         # 튜플
table = {"a": 1}      # 사전
nothing = None        # 값 없음

for value in (count, ratio, z, ok, name, raw, items, pair, table, nothing):
    print(type(value).__name__, value)
```

```text
int 3
float 0.5
complex (3+4j)
bool True
str sample
bytes b'\x01\x02'
list [1, 2, 3]
tuple (1, 2)
dict {'a': 1}
NoneType None
```

| 자료형       | C에서 비슷한 것             | 다른 점                          | 이 프로젝트에서 쓰는 곳                  |
| --------- | --------------------- | ----------------------------- | ------------------------------ |
| `int`     | `int`, `long`         | 크기 제한이 없다. 넘치지 않는다(§2.4)      | 샘플 값, 번호, 길이, 프레임 수            |
| `float`   | `double`              | 같은 64비트 실수다                   | 윈도우 값, 계산 중의 샘플                |
| `complex` | C99의 `double complex` | 기본으로 있다. 허수 단위는 `j`           | 스펙트럼, 회전 인자                    |
| `bool`    | `bool`                | `True`, `False` (대문자로 시작)     | 조건                             |
| `str`     | `char[]`              | 글자 단위. 바꿀 수 없다                | 파일 경로, 출력                      |
| `bytes`   | `unsigned char[]`     | 바꿀 수 없다                       | WAV에서 읽은 날것의 데이터(§15)          |
| `list`    | 배열                    | 크기가 늘고 준다. 여러 자료형을 섞어 담을 수 있다 | 샘플, 버퍼, 스펙트럼, 윈도우              |
| `tuple`   | 구조체를 값으로 넘기는 것과 비슷    | 바꿀 수 없는 묶음                    | 함수가 값 여러 개를 돌려줄 때(§7)          |
| `dict`    | 없음                    | 이름으로 값을 찾는 표                  | `tv.compare_wav`가 돌려주는 결과(§22) |
| `None`    | `NULL`과 비슷            | 값이 없음을 뜻한다                    | `return`이 없는 함수의 결과            |

### 2.2 선언 없이 정해지고, 다시 넣으면 바뀐다

```python
x = 10
print(type(x).__name__)
x = "열"                      # 같은 이름에 다른 자료형을 다시 넣어도 된다
print(type(x).__name__)
print(isinstance(3, int), isinstance(3.0, int), isinstance(3.0, float))
```

```text
int
str
True False True
```

| 쓰는 것 | 뜻 |
|---|---|
| `type(값)` | 자료형을 알려 준다 |
| `isinstance(값, 자료형)` | 그 자료형인지 `True`, `False`로 알려 준다 |

### 2.3 자료형 바꾸기

```python
print(int(2.9), int(-2.9), int("42"))
print(float(3), float("1.5"))
print(complex(2), complex(2, -1))
print(list((1, 2, 3)), tuple([4, 5]))
print(2 + 0.5, 2 + 1j)           # 섞으면 넓은 쪽 자료형이 된다
```

```text
2 -2 42
3.0 1.5
(2+0j) (2-1j)
[1, 2, 3] (4, 5)
2.5 (2+1j)
```

- `int(실수)`는 0 쪽으로 버린다. 가장 가까운 정수가 필요하면 `round`를 쓴다(§19)
- 정수와 실수를 섞으면 실수, 실수와 복소수를 섞으면 복소수가 된다

### 2.4 C와 다른 곳 — 넘침과 나눗셈

```python
import sys

print(32767 + 1)                 # C의 int16_t라면 -32768이 된다
print(2 ** 70)
print(sys.float_info.max)
print(sys.float_info.mant_dig)   # 가수의 비트 수. C의 double과 같다
```

```text
32768
1180591620717411303424
1.7976931348623157e+308
53
```

```python
print(7 / 2, 7 // 2, 7 % 2)
print(-7 // 2, -7 % 2)           # C에서는 -3, -1
print(int(-7 / 2))               # 0 쪽으로 버리면 C와 같다
```

```text
3.5 3 1
-4 1
-3
```

| C와 다른 점 | 이 프로젝트에서 조심할 곳 |
|---|---|
| `int`는 넘치지 않는다. 16bit 범위를 넘어도 그대로 커진다 | WAV에 쓰기 전에 −32768 ~ 32767로 **직접 자른다**(§19). 자르지 않으면 바이트로 바꿀 때 오류가 난다(§15) |
| `/`는 정수끼리 나눠도 늘 실수다 | 번호를 구할 때는 `//`를 쓴다. 리스트의 번호에 실수를 쓰면 오류가 난다 |
| 음수의 `//`, `%`는 아래쪽으로 내린다 | 이 프로젝트의 번호와 길이는 양수여서 영향이 없다 |

### 2.5 크기가 정해진 리스트 — C의 배열 선언 자리

C에서 `int buf[5] = {0};`로 하던 것을, Python에서는 값을 곱해 만든다.

```python
zeros = [0] * 5                  # C의 int zeros[5] = {0}; 자리
spectrum = [0j] * 3              # 복소수 0으로 채운 리스트
print(zeros, spectrum)
print(len(zeros))
zeros.append(7)                  # 리스트는 크기가 늘어난다
print(len(zeros))
```

```text
[0, 0, 0, 0, 0] [0j, 0j, 0j]
5
6
```

자료형과 크기가 고정된 배열이 필요하면 `array.array`(§15.2)나 numpy 배열(§23)을 쓴다. `array.array("h")`는 C의 `short` 배열처럼 2바이트 정수만 담고, 범위를 넘으면 오류를 낸다.

```python
import array

values = array.array("h", [0, 32767])    # "h" 는 2바이트 부호 있는 정수 (C의 short)
print(values.itemsize, values.tolist())
try:
    values.append(32768)
except OverflowError as error:
    print("OverflowError:", error)
```

```text
2 [0, 32767]
OverflowError: signed short integer is greater than maximum
```

### 2.6 자료형 적어 두기 (선택)

함수의 인자와 돌려주는 값에 자료형을 **적어 둘** 수 있다. 이것을 자료형 힌트라고 한다.

```python
def average(values: list[float]) -> float:
    return sum(values) / len(values)


print(average([1.0, 2.0, 4.0]))
print(average([1, 2, 4]))        # 정수를 넣어도 막지 않는다
print(average.__annotations__)
```

```text
2.3333333333333335
2.3333333333333335
{'values': list[float], 'return': <class 'float'>}
```

| 알아 둘 것 | 내용 |
|---|---|
| 적는 곳 | 인자 이름 뒤에 `: 자료형`, 괄호 뒤에 `-> 자료형` |
| 리스트의 안쪽 자료형 | `list[float]`, `list[complex]`, `list[int]` |
| 실행할 때 | Python은 **검사하지 않는다.** 위에서 정수 리스트를 넣어도 그대로 돈다 |
| 쓰는 까닭 | 읽는 사람에게 무엇을 넣고 무엇을 받는지 알려 준다. VS Code의 Pylance는 이 표시를 보고 맞지 않는 곳에 밑줄을 긋는다 |
| 이 프로젝트에서 | 선택이다. 함수가 받는 것이 샘플(`list[int]`)인지 스펙트럼(`list[complex]`)인지 헷갈릴 때 적어 두면 좋다 |

상수도 선언하는 문법이 없다. 바꾸지 않을 값은 이름을 대문자로 적는 관례만 있다(§1). 관례일 뿐 바꾸는 것을 막지는 않는다.

---

## 3. 숫자와 연산

**쓰는 곳**: 단계_6(프레임 수를 구하는 `//`), 단계_8(`n % 16`), 단계_3(`**`)

```python
eggs = 30
per_box = 12
print(eggs // per_box)   # 몫
print(eggs % per_box)    # 나머지
print(eggs / per_box)    # 나눗셈 (결과는 실수)
print(2 ** 10)           # 거듭제곱
print(-7 // 2)           # 음수의 몫은 아래쪽으로 내려간다
print(int(2.9), int(-2.9))   # int()는 0 쪽으로 버린다
print(float(3))
```

```text
2
6
2.5
1024
-4
2 -2
3.0
```

| 연산 | 뜻 |
|---|---|
| `/` | 나눗셈. 결과는 항상 실수 |
| `//` | 몫 |
| `%` | 나머지 |
| `**` | 거듭제곱 |

---

## 4. 리스트

**쓰는 곳**: 전체. 샘플, 버퍼, 스펙트럼, 윈도우를 담는다

### 4.1 만들기와 꺼내기

```python
temps = [21.5, 23.0, 19.8, 25.1, 22.4]
print(len(temps))    # 개수
print(temps[0])      # 첫째. 번호는 0부터
print(temps[-1])     # 마지막
temps[0] = 99.9      # 값 바꾸기
print(temps[0])
```

```text
5
21.5
22.4
99.9
```

### 4.2 슬라이싱, 일부 잘라 내기

`리스트[시작:끝]`은 시작 번호부터 **끝 번호 앞까지**를 새 리스트로 만든다.

```python
temps = [21.5, 23.0, 19.8, 25.1, 22.4]
print(temps[1:3])    # 1번, 2번
print(temps[2:])     # 2번부터 끝까지
print(temps[:2])     # 처음부터 1번까지
print(temps[::2])    # 하나 건너 하나
print(temps[::-1])   # 거꾸로
```

```text
[23.0, 19.8]
[19.8, 25.1, 22.4]
[21.5, 23.0]
[21.5, 19.8, 22.4]
[22.4, 25.1, 19.8, 23.0, 21.5]
```

### 4.3 만들기, 잇기, 붙이기

```python
seats = [0] * 4          # 같은 값을 여러 개
print(seats)
print([1, 2] + [3, 4])   # 두 리스트 잇기
basket = ["사과"]
basket.append("배")      # 맨 뒤에 하나 붙이기
print(basket)
print(sum([1, 2, 3]), max([3, 9, 1]), min([3, 9, 1]))
```

```text
[0, 0, 0, 0]
[1, 2, 3, 4]
['사과', '배']
6 9 1
```

### 4.4 주의, 복사가 아니라 같은 리스트

```python
a = [1, 2, 3]
b = a            # b는 a와 같은 리스트를 가리킨다
b[0] = 100
print(a)

a = [1, 2, 3]
c = a[:]         # 슬라이싱은 새 리스트를 만든다
c[0] = 100
print(a, c)
```

```text
[100, 2, 3]
[1, 2, 3] [100, 2, 3]
```

---

## 5. 반복문

**쓰는 곳**: 전체. 샘플, bin, 프레임을 차례로 돈다

### 5.1 for

```python
prices = [1200, 800, 3500]
total = 0
for p in prices:
    total = total + p
print(total)

for i in range(3):
    print(i, prices[i])
```

```text
5500
0 1200
1 800
2 3500
```

### 5.2 range

```python
print(list(range(5)))          # 0부터 4까지
print(list(range(2, 6)))       # 2부터 5까지
print(list(range(0, 10, 4)))   # 0부터 4씩 건너뛰며 10 앞까지
```

```text
[0, 1, 2, 3, 4]
[2, 3, 4, 5]
[0, 4, 8]
```

### 5.3 번호와 값을 함께, 두 리스트를 함께

```python
names = ["사과", "배", "감"]
prices = [1200, 800, 3500]
for i, name in enumerate(names):
    print(i, name)
for name, p in zip(names, prices):
    print(name, p)
```

```text
0 사과
1 배
2 감
사과 1200
배 800
감 3500
```

### 5.4 while

```python
saved = 0
weeks = 0
while saved < 30000:
    saved = saved + 5000
    weeks = weeks + 1
print(weeks)
```

```text
6
```

---

## 6. 조건문

**쓰는 곳**: 단계_8(더할 자리가 범위 안인가)

```python
score = 83
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
print(grade)
```

```text
B
```

| 비교 | 뜻 | 논리 | 뜻 |
|---|---|---|---|
| `==` | 같다 | `and` | 둘 다 참 |
| `!=` | 다르다 | `or` | 하나라도 참 |
| `<`, `<=`, `>`, `>=` | 크기 비교 | `not` | 반대 |

---

## 7. 함수

**쓰는 곳**: 전체. 단계마다 함수를 만든다

```python
def to_fahrenheit(celsius):
    """섭씨 온도를 화씨로 바꾼다."""
    return celsius * 9 / 5 + 32


def area(width, height=1):      # height를 안 주면 1
    return width * height


def min_max(values):            # 값 두 개를 돌려준다
    return min(values), max(values)


print(to_fahrenheit(100))
print(area(3), area(3, 4), area(height=2, width=5))
lo, hi = min_max([3, 9, 1])
print(lo, hi)
```

```text
212.0
3 12 10
1 9
```

- `def` 바로 아래의 `"""..."""`는 함수 설명이다
- 함수 안에서 만든 변수는 함수 밖에서 보이지 않는다
- 리스트를 인자로 넘기면 복사되지 않는다(§4.4). 함수 안에서 고치면 바깥의 리스트도 바뀐다

---

## 8. 모듈과 import

**쓰는 곳**: 전체. 시험 파일에서 `main.py`의 함수를 불러오고, `main.py`를 직접 실행한다

`.py` 파일 하나가 모듈 하나다. 다른 파일의 함수를 쓰려면 `import`한다.

`src/temperature.py`:

```python
def to_fahrenheit(celsius):
    """섭씨 온도를 화씨로 바꾼다."""
    return celsius * 9 / 5 + 32


if __name__ == "__main__":
    print(to_fahrenheit(100))
```

같은 폴더의 다른 파일에서 쓰는 두 가지 방법:

```python
import temperature
print(temperature.to_fahrenheit(100))

from temperature import to_fahrenheit
print(to_fahrenheit(100))
```

```text
212.0
212.0
```

- `if __name__ == "__main__":` 아래는 그 파일을 **직접 실행할 때만** 돈다. 다른 파일이 `import`할 때는 돌지 않는다. 시험 삼아 돌려 볼 코드를 여기에 둔다
- Python은 실행한 파일이 있는 폴더에서 모듈을 찾는다. `src/` 안의 파일끼리는 위처럼 파일 이름만으로 `import`할 수 있다
- 표준 라이브러리(`math`, `cmath`, `wave`, `time`)와 설치한 패키지(`numpy`)는 어디서든 `import`할 수 있다
- 자기 파일 이름을 표준 라이브러리와 같게 짓지 않는다. `wave.py`, `math.py`라는 파일을 만들면 표준 라이브러리 대신 그 파일이 읽힌다

### 8.1 실행 순서, C와 다른 점

C는 `main` 함수에서 시작한다. Python은 **파일의 첫 줄부터 아래로** 차례로 실행한다. `main`이라는 이름은 특별하지 않다.

| 항목 | C | Python |
|---|---|---|
| 시작하는 곳 | `main` 함수 | 실행한 파일의 첫 줄 |
| `main`이라는 이름 | 정해져 있다 | 관례일 뿐이다. 다른 이름이어도 된다 |
| 함수 정의 | 컴파일할 때 처리된다 | `def` 줄이 **실행될 때** 함수가 만들어진다. 안의 내용은 부를 때 실행된다 |
| `main`을 부르는 것 | 시스템이 부른다 | 파일 맨 아래에서 **직접** 부른다 |

`order.py`:

```python
print("1. 파일의 첫 줄")


def main():
    print("4. main 함수 안")
    helper()


print("2. def 는 함수를 만들어 둘 뿐이다. 아직 실행되지 않았다")


def helper():
    print("5. main 보다 아래에 만든 함수")


print("3. __name__ 의 값:", __name__)

if __name__ == "__main__":
    main()
```

직접 실행했을 때:

```bash
python order.py
```

```text
1. 파일의 첫 줄
2. def 는 함수를 만들어 둘 뿐이다. 아직 실행되지 않았다
3. __name__ 의 값: __main__
4. main 함수 안
5. main 보다 아래에 만든 함수
```

다른 파일에서 불러왔을 때:

```python
import order
```

```text
1. 파일의 첫 줄
2. def 는 함수를 만들어 둘 뿐이다. 아직 실행되지 않았다
3. __name__ 의 값: order
```

| 줄 | 하는 일 |
|---|---|
| `def main():` | `main`이라는 함수를 **만든다**. 이 줄에서는 안의 내용이 실행되지 않는다 |
| `__name__` | Python이 파일마다 자동으로 넣어 주는 변수다. 그 파일을 직접 실행하면 `"__main__"`, 다른 파일이 `import`하면 파일 이름(`"order"`)이 들어 있다 |
| `if __name__ == "__main__":` | "이 파일을 직접 실행했는가"를 묻는 조건문이다 |
| `main()` | 함수를 **부른다**. 여기서 비로소 `main` 안의 내용이 실행된다 |

근거: Python 문서 "`__main__` — Top-level code environment", 위 실행 출력.

| 알아 둘 것 | 내용 | 근거 |
|---|---|---|
| 맨 아래 두 줄이 없으면 | 함수를 만들기만 하고 끝난다. 아무것도 출력되지 않는다 | 실행 확인 |
| 함수를 두는 자리 | 부르는 **시점**보다 먼저 만들어져 있으면 된다. 위 예의 `helper`는 `main`보다 아래에 있지만, `main()`을 부르는 맨 아래 줄보다는 위에 있어서 부를 수 있다 | 위 출력의 5번 줄 |
| 만들기 전에 부르면 | `NameError: name '...' is not defined`가 난다 | 실행 확인 |
| 그래서 | `main()`을 부르는 두 줄은 파일의 **맨 아래**에 둔다 | — |

---

## 9. 오류 다루기

**쓰는 곳**: 단계_1(WAV 조건이 맞지 않으면 오류를 낸다). 오류 메시지를 읽을 때

잘못된 입력을 만나면 `raise`로 오류를 낸다. 오류를 받아 처리하려면 `try`와 `except`를 쓴다.

```python
def check_age(age):
    if age < 0:
        raise ValueError("나이는 0 이상이어야 한다: " + str(age))
    return age


try:
    check_age(-3)
except ValueError as e:
    print("잘못된 값:", e)
```

```text
잘못된 값: 나이는 0 이상이어야 한다: -3
```

오류 메시지(Traceback)는 **맨 아래 줄**에 오류의 종류와 내용이 있고, 그 위로 어느 파일의 몇째 줄에서 났는지가 나온다. 아래에서 위로 읽는다.

| 자주 보는 오류 | 뜻 |
|---|---|
| `IndentationError` | 들여쓰기가 맞지 않는다 |
| `NameError` | 없는 이름을 썼다 (오타, 정의 전에 사용) |
| `IndexError` | 리스트의 범위를 벗어난 번호를 썼다 |
| `TypeError` | 맞지 않는 종류의 값을 넣었다 |
| `ModuleNotFoundError` | `import`할 모듈을 찾지 못했다 (§8) |

---

## 10. 리스트 내포

**쓰는 곳**: 단계_5(윈도우 512개 만들기), 단계_7(자리마다 곱하기), 단계_4(켤레 모으기)

반복문으로 리스트를 만드는 것을 한 줄로 쓰는 문법이다.

```python
prices = [1200, 800, 3500]
print([n * n for n in range(5)])
print([p * 2 for p in prices])
print([p for p in prices if p > 1000])
```

```text
[0, 1, 4, 9, 16]
[2400, 1600, 7000]
[1200, 3500]
```

---

## 11. 문자열 포맷과 시간 재기

**쓰는 곳**: 결과를 출력할 때, 걸린 시간을 잴 때(선택)

```python
value = 3.14159265
print(f"{value:.3f}")        # 소수 셋째 자리까지
print(f"{value:e}")          # 지수 표기
print(f"{12:5d}|")           # 5칸에 맞춰 오른쪽 정렬
print(f"평균 {value:.1f}도")
```

```text
3.142
3.141593e+00
   12|
평균 3.1도
```

```python
import time

t0 = time.perf_counter()
s = 0
for i in range(100000):
    s = s + i
t1 = time.perf_counter()
print(s)
print(t1 - t0 > 0)     # 걸린 시간(초)은 t1 - t0
```

```text
4999950000
True
```

---

## 12. 복소수

**쓰는 곳**: 단계_2 ~ 단계_4(DFT, FFT, IFFT), 단계_7, 단계_8

### 12.1 복소수의 기본

Python은 복소수를 기본으로 지원한다. 허수 단위는 `j`다.

```python
z = 3 + 4j
print(z.real, z.imag)      # 실수부, 허수부
print(abs(z))              # 크기
print(z.conjugate())       # 켤레
print(z * 1j)              # 곱셈
print(z + (1 - 2j), z / 2)
print(complex(2, -1), complex(5))   # 실수 두 개로 만들기
```

```text
3.0 4.0
5.0
(3-4j)
(-4+3j)
(4+2j) (1.5+2j)
(2-1j) (5+0j)
```

복소수용 수학 함수는 `cmath` 모듈에 있다.

```python
import cmath
import math

q = cmath.exp(1j * math.pi / 2)    # 각도 90도인 크기 1의 복소수
print(round(q.real, 12), round(q.imag, 12))
print(cmath.phase(1j))             # 각도(라디안)
print(abs(cmath.exp(1j * 0.3)))    # 크기는 1
```

```text
0.0 1.0
1.5707963267948966
1.0
```

| 쓰임 | 문법 | 근거 |
|---|---|---|
| 허수 | 숫자 뒤에 `j` (`1j`, `2.5j`) | Python 문서 "Built-in Types" |
| 실수부, 허수부 | `z.real`, `z.imag` | 같음 |
| 켤레 | `z.conjugate()` | 같음 |
| 크기 | `abs(z)` | Python 문서 `cmath` |
| 지수 함수 | `cmath.exp(x)` | 같음 |
| 각도 | `cmath.phase(x)` | 같음 |

> [!NOTE]
> `j`만 쓰면 변수 이름으로 읽힌다. 허수 단위는 반드시 `1j`처럼 숫자를 붙인다.

### 12.2 복소 지수와 삼각 함수

```python
import cmath
import math

angle = 2 * math.pi / 8                  # 한 바퀴의 8분의 1 (45도)
w = cmath.exp(-1j * angle)               # 크기 1, 각도 -45도인 복소수
print(round(w.real, 6), round(w.imag, 6))
print(round(abs(w), 6))
print(round(math.cos(angle), 6), round(math.sin(angle), 6))
w4 = w ** 4                              # 거듭제곱하면 각도가 그만큼 배가 된다 (-180도)
print(round(w4.real, 6), round(w4.imag, 6))
both = w * w.conjugate()                 # 켤레와 곱하면 크기의 제곱
print(round(both.real, 6), round(both.imag, 6))
```

```text
0.707107 -0.707107
1.0
0.707107 0.707107
-1.0 -0.0
1.0 0.0
```

계산 오차 때문에 0이어야 할 값이 아주 작은 값으로 나온다. 위에서 `-0.0`으로 보이는 것이 그것이다.

```python
import cmath
import math

print(cmath.exp(-1j * math.pi))          # 수학으로는 -1
print(math.cos(math.pi / 2))             # 수학으로는 0
```

```text
(-1-1.2246467991473532e-16j)
6.123233995736766e-17
```

복소수를 리스트에 담아 다루기:

```python
values = [0j] * 4                        # 복소수 0 네 개
values[1] = 3 + 4j
print(values)
print(sum(values))                       # 복소수도 sum 으로 더한다
print([v.real for v in values])          # 실수부만 모으기
print([v.conjugate() for v in values])   # 켤레만 모으기
print(complex(5), complex(2.5))          # 정수, 실수를 복소수로
```

```text
[0j, (3+4j), 0j, 0j]
(3+4j)
[0.0, 3.0, 0.0, 0.0]
[-0j, (3-4j), -0j, -0j]
(5+0j) (2.5+0j)
```

---

## 13. math 모듈과 실수 비교

**쓰는 곳**: 단계_5(코사인), 단계_6(올림), 확인할 때 실수 비교

```python
import math

print(math.pi)
print(math.cos(0), math.sin(math.pi / 2), math.sqrt(16))
print(math.log10(1000), math.log2(8))
print(math.floor(2.7), math.ceil(2.1))   # 내림, 올림
```

```text
3.141592653589793
1.0 1.0 4.0
3.0 3.0
2 3
```

실수는 계산 오차가 남는다. 같은지를 볼 때는 `==` 대신 `math.isclose`를 쓴다.

```python
import math

print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(math.isclose(0.1 + 0.2, 0.3))
print(math.isclose(1e-12, 0.0))                  # 0과 비교할 때는 abs_tol을 줘야 한다
print(math.isclose(1e-12, 0.0, abs_tol=1e-9))
```

```text
0.30000000000000004
False
True
False
True
```

---

## 14. 비트 연산과 2의 거듭제곱

**쓰는 곳**: 단계_3(비트 반전, 단계 수)

### 14.1 비트 연산과 이진수

```python
print(5 << 1)     # 왼쪽으로 1비트 (2배)
print(20 >> 2)    # 오른쪽으로 2비트 (4로 나눈 몫)
print(6 & 3)      # 비트 AND
print(6 | 3)      # 비트 OR
print(1 << 9)     # 2의 9제곱
print((8).bit_length())   # 값을 적는 데 필요한 비트 수
```

```text
10
5
2
7
512
4
```

정수와 이진수 문자열 사이를 오간다.

```python
print(bin(10))              # 이진수 문자열
print(format(5, "04b"))     # 4자리로 맞춘 이진수 문자열
print(int("1010", 2))       # 이진수 문자열을 정수로
print("abc"[::-1])          # 문자열도 슬라이싱으로 뒤집는다
```

```text
0b1010
0101
10
cba
```

### 14.2 길이와 단계 수

```python
n = 512
print(n & (n - 1) == 0)          # 2의 거듭제곱이면 True
print(500 & 499 == 0)            # 500 은 2의 거듭제곱이 아니다
print((500 & 499) == 0)          # 괄호를 쳐도 결과가 같다
print(n.bit_length() - 1)        # 2를 몇 번 곱하면 n 이 되는가 (2의 거듭제곱일 때)
print(list(range(0, 16, 4)))     # 0 부터 4 간격으로, 16 앞까지

sizes = []
size = 2
while size <= 16:
    sizes.append(size)
    size = size * 2
print(sizes)
```

```text
True
False
False
9
[0, 4, 8, 12]
[2, 4, 8, 16]
```

> [!NOTE]
> Python에서는 `&`가 `==`보다 먼저 계산된다. 위에서 괄호가 있든 없든 결과가 같은 것이 그 때문이다.

---

## 15. 바이트와 정수

**쓰는 곳**: 단계_1(읽은 바이트를 정수로), 단계_9(정수를 바이트로)

### 15.1 하나씩 바꾸기

파일에서 읽은 날것의 데이터는 `bytes`다. `b'...'`로 적는다.

```python
data = b'\x01\x02\x03\x04'
print(len(data))
print(data[0])                       # 하나를 꺼내면 정수
print(data[0:2])                     # 잘라 내면 bytes
print(data + b'\x05')                # 잇기
print(b"".join([b'\x01', b'\x02']))  # 리스트에 담긴 조각 잇기
```

```text
4
1
b'\x01\x02'
b'\x01\x02\x03\x04\x05'
b'\x01\x02'
```

바이트를 정수로, 정수를 바이트로 바꾼다.

```python
print(int.from_bytes(b'\x00\x10', byteorder='little'))
print(int.from_bytes(b'\x00\x10', byteorder='big'))
print(int.from_bytes(b'\xfe\xff', byteorder='little', signed=True))
print(int.from_bytes(b'\xfe\xff', byteorder='little', signed=False))
print((1024).to_bytes(2, byteorder='little', signed=True))
print((-2).to_bytes(2, byteorder='little', signed=True))
```

```text
4096
16
-2
65534
b'\x00\x04'
b'\xfe\xff'
```

| 인자 | 뜻 | 근거 |
|---|---|---|
| `byteorder='little'` | 가장 큰 자리의 바이트가 **뒤에** 온다 | Python 문서 "Built-in Types" |
| `byteorder='big'` | 가장 큰 자리의 바이트가 앞에 온다 | 같음 |
| `signed=True` | 2의 보수로 읽고 쓴다 | 같음 |

정해진 바이트 수에 담을 수 없는 값을 바꾸려 하면 오류가 난다.

```python
try:
    (40000).to_bytes(2, byteorder='little', signed=True)
except OverflowError as e:
    print("OverflowError:", e)
```

```text
OverflowError: int too big to convert
```

> [!NOTE]
> 같은 일을 하는 다른 도구로 표준 라이브러리의 `struct`, `array` 모듈과 numpy의 `frombuffer`(§23)가 있다. 여러 개를 한꺼번에 바꿀 때 편하다.

### 15.2 여러 개를 한꺼번에 바꾸기

`readframes`가 돌려준 `bytes`를 정수 리스트로 바꾸는 방법은 여러 가지다. 아래 셋은 같은 결과를 낸다.

```python
import array
import struct

raw = b'\x00\x00\xe8\x03\x18\xfc\xff\x7f'

# 방법 1: 두 바이트를 잘라 int.from_bytes (1번 샘플만)
print(int.from_bytes(raw[2:4], byteorder="little", signed=True))

# 방법 2: struct. "<" 는 little-endian, "h" 는 2바이트 부호 있는 정수, 앞의 숫자는 개수
print(struct.unpack("<4h", raw))
count = len(raw) // 2
print(list(struct.unpack("<" + str(count) + "h", raw)))

# 방법 3: array. "h" 는 2바이트 부호 있는 정수
values = array.array("h")
values.frombytes(raw)
print(values.tolist())
```

```text
1000
(0, 1000, -1000, 32767)
[0, 1000, -1000, 32767]
[0, 1000, -1000, 32767]
```

반대 방향(정수 리스트 → `bytes`)도 셋 다 같은 결과를 낸다.

```python
import array
import struct

values = [0, 1000, -1000, 32767]
print(struct.pack("<4h", *values))          # *values 는 리스트를 풀어 인자 4개로 넘긴다
print(array.array("h", values).tobytes())
print(b"".join(v.to_bytes(2, byteorder="little", signed=True) for v in values))
```

```text
b'\x00\x00\xe8\x03\x18\xfc\xff\x7f'
b'\x00\x00\xe8\x03\x18\xfc\xff\x7f'
b'\x00\x00\xe8\x03\x18\xfc\xff\x7f'
```

범위를 벗어난 값을 넣으면 오류가 난다.

```python
import struct

try:
    struct.pack("<h", 40000)
except struct.error as error:
    print("struct.error:", error)
```

```text
struct.error: short format requires -32768 <= number <= 32767
```

| 방법 | 바이트 순서 | 알아 둘 것 |
|---|---|---|
| `int.from_bytes`, `to_bytes` | `byteorder`로 직접 정한다 | 하나씩 바꾼다. 반복문이 필요하다 |
| `struct.unpack`, `pack` | 형식 글자 `<`로 직접 정한다 | 개수를 형식 글자에 적어야 한다 |
| `array.array("h")` | **PC의 순서**를 따른다. 이 PC는 little-endian이다 | `sys.byteorder`로 확인한다 |
| `numpy.frombuffer` | `dtype="<i2"`로 직접 정한다 | §23 |

```python
import sys

print(sys.byteorder)
```

```text
little
```

---

## 16. WAV 파일

**쓰는 곳**: 단계_1(WAV 읽기), 단계_9(WAV 쓰기)

`wave.open`은 `with` 문과 함께 쓴다.

| 알아 둘 것 | 내용 |
|---|---|
| `with 무엇 as 이름:` | 아래 블록이 끝나면 파일이 자동으로 닫힌다. C에서 `fclose`를 잊지 않게 해 주는 문법이다 |
| `"wb"`, `"rb"` | 쓰기, 읽기. `b`는 글자가 아닌 데이터라는 뜻이다 |
| 근거 | Python 문서 "wave — Read and write WAV files" |

샘플 4개짜리 WAV를 쓰고 다시 읽는다. 샘플 값은 0, 1000, −1000, 32767이다.

```python
import wave

raw = b'\x00\x00\xe8\x03\x18\xfc\xff\x7f'    # 샘플 4개를 2바이트씩 이어 붙인 것

with wave.open("example.wav", "wb") as wav_file:
    wav_file.setnchannels(1)        # 모노
    wav_file.setsampwidth(2)        # 샘플 하나가 2바이트 (16bit)
    wav_file.setframerate(16000)    # 16 kHz
    wav_file.writeframes(raw)

with wave.open("example.wav", "rb") as wav_file:
    print(wav_file.getnchannels())
    print(wav_file.getsampwidth())
    print(wav_file.getframerate())
    print(wav_file.getnframes())
    print(wav_file.getparams())
    data = wav_file.readframes(wav_file.getnframes())

print(type(data), len(data))
print(data == raw)
```

```text
1
2
16000
4
_wave_params(nchannels=1, sampwidth=2, framerate=16000, nframes=4, comptype='NONE', compname='not compressed')
<class 'bytes'> 8
True
```

**`with` 문**. `with 식 as 이름:`은 식이 돌려준 것(여기서는 열린 파일)을 `이름`에 담고 아래 블록을 실행한다. 블록을 빠져나가면 파일을 닫는다. 끝까지 가서 나가든, `return`으로 나가든, 오류로 나가든 닫힌다. 위의 읽기는 아래 코드와 같은 뜻이다. `finally` 아래는 오류가 나도 실행된다.

```python
import wave

wav_file = wave.open("example.wav", "rb")
try:
    data = wav_file.readframes(wav_file.getnframes())
finally:
    wav_file.close()
print(len(data))
```

```text
8
```

| 알아 둘 것 | 내용 | 근거 |
|---|---|---|
| 원리 | 블록에 들어갈 때 그 객체의 `__enter__`를, 나갈 때 `__exit__`를 부른다. `wave` 객체의 `__exit__`는 `self.close()` 한 줄이다 | 설치된 `wave.py`의 소스 (2026-09-29 `inspect.getsource`) |
| 오류가 나도 닫힌다 | 블록 안에서 일부러 오류를 내도 파일이 닫혀 있었다 | 2026-09-29 실행 |
| 블록 밖 | 파일이 닫혀 있다. 블록 밖에서 `readframes`를 부르면 `ValueError: read of closed file`이 난다. 필요한 값은 블록 안에서 변수에 담아 둔다(`src/main.py`의 `read_wav`가 그렇게 한다) | 같음 |

`readframes(n)`은 읽던 자리에서 이어서 읽는다. 끝까지 읽은 뒤에는 빈 `bytes`가 나온다.

```python
import wave

with wave.open("example.wav", "rb") as wav_file:
    first = wav_file.readframes(3)      # 앞의 3개
    second = wav_file.readframes(3)     # 남은 것은 1개뿐
    third = wav_file.readframes(3)      # 더 없다
print(len(first), len(second), len(third))
```

```text
6 2 0
```

| 알아 둘 것 | 내용 | 근거 |
|---|---|---|
| 설정 순서 | 채널 수, 샘플 폭, 샘플링 주파수를 정한 **뒤에** `writeframes`를 부른다 | 위 예시 |
| 돌려주는 것 | `readframes`는 `bytes`를 돌려준다. 정수로 바꾸는 것은 따로 한다(§15.2) | Python 문서 `wave` |
| 단위 | `wave`의 프레임은 한 시점의 샘플 묶음이다. 모노 16bit이면 프레임 하나가 2바이트다 | [07](07_WAV%20파일.md) §3 |
| 없는 파일 | 읽기로 열면 `FileNotFoundError`가 난다 | §9 |

---

## 17. 버퍼

**쓰는 곳**: 단계_6(버퍼 앞 16개를 버리고 뒤에 붙이기)

길이가 정해진 버퍼에 새 값을 넣고 오래된 값을 버리는 방법은 둘이다.

| 방법 | 내용 |
|---|---|
| 리스트 | 슬라이싱으로 앞을 잘라 내고 뒤에 이어 붙인다 (§4.2, §4.3) |
| `collections.deque` | `maxlen`을 주면 넘치는 만큼 앞에서 저절로 빠진다 |

```python
from collections import deque

buffer = deque([0] * 8, maxlen=8)    # 길이 8 로 고정
buffer.extend([1, 2])                # 뒤에 넣으면 앞의 것이 밀려 나간다
print(list(buffer))
buffer.extend([3, 4])
print(list(buffer))
print(len(buffer), buffer[0], buffer[-1])
values = list(buffer)                # 계산에 쓸 때는 리스트로 바꾼다
print(values[6:8])
```

```text
[0, 0, 0, 0, 0, 0, 1, 2]
[0, 0, 0, 0, 1, 2, 3, 4]
8 0 4
[3, 4]
```

`deque`는 슬라이싱(`buffer[2:4]`)을 할 수 없다. 리스트로 바꾼 뒤에 한다.

입력을 일정한 개수씩 나눌 때 쓰는 것:

```python
import math

print(math.ceil(16001 / 16))         # 올림. 16개씩 나누면 몇 묶음인가
print(16001 // 16, 16001 % 16)       # 몫과 나머지
print(list(range(0, 40, 16)))        # 16 간격의 시작 위치

samples = list(range(40))
part = samples[32:48]                # 끝을 넘겨 잘라도 오류가 나지 않는다
print(part, len(part))
part = part + [0] * (16 - len(part)) # 모자란 만큼 0 을 채운다
print(len(part))
```

```text
1001
1000 1
[0, 16, 32]
[32, 33, 34, 35, 36, 37, 38, 39] 8
16
```

---

## 18. 자리마다 계산하기

**쓰는 곳**: 단계_7(윈도우 곱), 단계_8(겹쳐 더하기)

```python
a = [1.0, 2.0, 3.0]
b = [0.5, 0.5, 2.0]
print([x * y for x, y in zip(a, b)])             # 같은 자리끼리 곱하기
print(max(abs(x - y) for x, y in zip(a, b)))     # 가장 큰 차이
print(sum(x * x for x in a))                     # 제곱의 합

total = [0.0] * 5
for i, x in enumerate(a):
    total[i + 1] += x                            # 위치를 하나 옮겨 더하기
print(total)
print(7 % 3, 16 % 16, 17 % 16)                   # 나머지
```

```text
[0.5, 1.0, 6.0]
1.5
14.0
[0.0, 1.0, 2.0, 3.0, 0.0]
1 0 1
```

0으로 나누면 오류가 난다. 윈도우 값으로 나누려 하면 양 끝이 0이어서 이 오류가 난다(04 단계_8의 자주 하는 실수).

```python
try:
    1 / 0
except ZeroDivisionError as error:
    print("ZeroDivisionError:", error)
```

```text
ZeroDivisionError: division by zero
```

---

## 19. 반올림과 범위 자르기

**쓰는 곳**: 단계_9(실수를 16bit 정수로)

```python
print(round(2.4), round(2.6))
print(round(0.5), round(1.5), round(2.5))   # 정확히 0.5이면 짝수 쪽으로
print(round(-1.5))
print(round(3.14159, 2))                    # 소수 둘째 자리까지
```

```text
2 3
0 2 2
-2
3.14
```

값을 정해진 범위 안으로 자를 때는 `min`과 `max`를 겹쳐 쓴다.

```python
print(max(0, min(100, 120)))   # 100보다 크면 100
print(max(0, min(100, -5)))    # 0보다 작으면 0
print(max(0, min(100, 77)))    # 범위 안이면 그대로
```

```text
100
0
77
```

---

## 20. 경로와 실행 인자

**쓰는 곳**: 단계_1, 단계_9(파일 경로, 출력 폴더)

경로를 적을 때 Windows의 `\`는 문자열 안에서 특수 문자로 읽힐 수 있다. `/`를 쓰거나 문자열 앞에 `r`을 붙인다.

```python
path_a = "data/input/memo.txt"
path_b = r"data\input\memo.txt"
print(path_a)
print(path_b)
```

```text
data/input/memo.txt
data\input\memo.txt
```

```python
import os

path = os.path.join("data", "input", "tone.wav")
print(path)
print(os.path.exists(path))
print(os.path.basename(path))
print(os.path.splitext(os.path.basename(path)))
os.makedirs(os.path.join("data", "output"), exist_ok=True)   # 폴더가 없으면 만든다
print(os.path.isdir(os.path.join("data", "output")))
```

```text
data\input\tone.wav
False
tone.wav
('tone', '.wav')
True
```

실행할 때 파일 이름 뒤에 적은 글자는 `sys.argv`로 받는다. 0번은 실행한 파일의 이름이다.

`show_args.py`:

```python
import sys

print(sys.argv)
print(len(sys.argv))
```

```bash
python show_args.py data/input/tone.wav data/output/tone.wav
```

```text
['show_args.py', 'data/input/tone.wav', 'data/output/tone.wav']
3
```

---

## 21. pytest로 시험하기

**쓰는 곳**: 전체. 단계마다 시험을 쓴다

시험 파일은 `tests/` 폴더에 `test_`로 시작하는 이름으로 만든다. 그 안의 `test_`로 시작하는 함수가 시험 하나다.

가장 작은 시험. 다른 파일을 불러오지 않는다.

```python
def test_addition():
    assert 1 + 1 == 2
```

```bash
python -m pytest -v
```

```text
tests/test_main.py::test_addition PASSED                                 [100%]

============================== 1 passed in 0.04s ==============================
```

다른 파일의 함수를 시험할 때는 그 파일에서 함수를 불러온다. 아래는 §8의 `src/temperature.py`를 시험하는 예다.

> [!WARNING]
> 아래 예시는 `src/temperature.py`가 **있어야** 돈다. 그 파일 없이 옮겨 적으면 `ModuleNotFoundError: No module named 'temperature'`가 난다(2026-09-29 확인). 이 프로젝트에서 직접 만든 함수를 시험할 때는 `from main import 함수이름`으로 쓴다.

`tests/test_temperature.py`:

```python
import pytest

from temperature import to_fahrenheit


def test_boiling_point():
    assert to_fahrenheit(100) == 212


def test_body_temperature():
    assert to_fahrenheit(36.6) == pytest.approx(97.88)
```

프로젝트 폴더에서 실행한다. `-v`는 시험 이름을 하나씩 보여 주는 옵션이다.

```bash
python -m pytest -v
```

```text
tests/test_temperature.py::test_boiling_point PASSED                     [ 50%]
tests/test_temperature.py::test_body_temperature PASSED                  [100%]

============================== 2 passed in 0.02s ==============================
```

| 문법 | 뜻 |
|---|---|
| `assert 조건` | 조건이 거짓이면 그 시험은 실패다 |
| `pytest.approx(값)` | 실수를 허용 오차 안에서 비교한다 |
| `pytest.approx(값, abs=1e-9)` | 허용 오차를 직접 준다 |

`tests/`의 파일이 `src/`의 모듈을 `import`할 수 있는 것은 프로젝트의 `pytest.ini`에 `pythonpath = src`가 적혀 있기 때문이다 → [01_프로젝트 구성과 실행 환경.md](01_프로젝트%20구성과%20실행%20환경.md) §6.

---

## 22. 검사 도구 testvec

**쓰는 곳**: 단계_3 ~ 단계_10의 확인

`src/testvec.py`는 직접 만든 함수의 결과를 미리 준비한 값과 비교한다. 자세한 것은 [06_테스트 벡터 사용법.md](06_테스트%20벡터%20사용법.md)에 있다.

| 함수 | 하는 일 |
|---|---|
| `tv.check_function(함수, 묶음)` | 묶음의 입력을 함수에 넣고 결과를 기대값과 비교한다 |
| `tv.check_window(값)` | 윈도우 512개를 비교한다 |
| `tv.compare(이름, 결과, 기대값)` | 두 리스트를 자리마다 비교한다 |
| `tv.compare_wav(원본 경로, 복원 경로)` | WAV 두 개를 비교한다. 파일 전체가 같으면 완전 복원으로 끝내고, 다르면 복원율(%)과 밀림, 크기 비, 유사도를 알려 준다 |
| `tv.compare_samples(이름, 원본, 복원)` | 리스트 두 개를 같은 방법으로 비교한다 |

뒤의 두 함수는 결과를 사전(dict)으로 돌려준다. 값은 `결과["이름"]`으로 꺼낸다.

```python
import testvec as tv

result = tv.compare_samples("예시", [10, 20, 30, 40], [10, 20, 30, 41])
print(result["percent"])
print(result["shift"])
```

```text
[복원율] 예시 : 75.0000 %
    그대로 비교       :   75.0000 %  (원본 4개 중 3개 일치)
    밀림              : 없다
    밀림을 맞춘 뒤    :   75.0000 %  (원본 4개 중 3개 일치)
    겹친 구간만 보면  :   75.0000 %  (겹친 4개 중 3개 일치)
    크기 비           :    1.0133    (복원 / 원본)
    파형 유사도       :   99.9924 %
    스펙트럼 유사도   :   99.9469 %
    판정: 거의 같다. 작은 오차가 있다
    밀림을 맞춘 뒤에도 다른 샘플 1개 (허용 차이 0)
         원본 위치  원본               복원               차이
             3  40               41               1
    처음 다른 위치 3, 마지막 다른 위치 3
75.0
0
```

파일 두 개가 완전히 같은지만 볼 때는 표준 라이브러리 `filecmp`를 쓴다. `tv.compare_wav`도 처음에 이 비교를 한다.

```python
import filecmp

with open("a.bin", "wb") as f:
    f.write(bytes([1, 2, 3, 4]))
with open("b.bin", "wb") as f:
    f.write(bytes([1, 2, 3, 4]))
with open("c.bin", "wb") as f:
    f.write(bytes([1, 2, 3, 5]))

print(filecmp.cmp("a.bin", "b.bin", shallow=False))
print(filecmp.cmp("a.bin", "c.bin", shallow=False))
```

```text
True
False
```

| 인자 | 뜻 |
|---|---|
| `shallow=False` | 내용을 끝까지 읽어 비교한다 |
| `shallow=True` (기본값) | 파일의 종류, 크기, 수정 시각이 같으면 내용을 읽지 않고 같다고 본다 |

같은지 다른지만 알려 준다. 어디가 다른지는 `tv.compare_wav`로 본다.

---

## 23. numpy와 그래프 (선택)

**쓰는 곳**: 선택 단계. 기본 구현에는 쓰지 않는다

### 23.1 numpy 기본

numpy의 배열은 같은 종류의 숫자를 모아 둔 것이다. 배열끼리의 연산은 원소마다 한꺼번에 적용된다.

```python
import numpy as np

arr = np.array([1.0, 2.0, 3.0])
print(arr * 2)
print(arr + arr)
print(arr.sum(), len(arr), arr.dtype)
print(np.zeros(3))
print(np.arange(4))
print(arr.tolist())          # 리스트로 되돌리기
```

```text
[2. 4. 6.]
[2. 4. 6.]
6.0 3 float64
[0. 0. 0.]
[0 1 2 3]
[1.0, 2.0, 3.0]
```

바이트 묶음을 정수 배열로, 정수 배열을 바이트 묶음으로 바꾼다. `'<i2'`는 little-endian 2바이트 부호 있는 정수를 뜻한다.

```python
import numpy as np

print(np.frombuffer(b'\x01\x00\x02\x00\xff\xff', dtype='<i2'))
print(np.array([1, -2, 3], dtype='<i2').tobytes())
```

```text
[ 1  2 -1]
b'\x01\x00\xfe\xff\x03\x00'
```

> [!IMPORTANT]
> `numpy.fft`는 쓰지 않는다. FFT와 IFFT는 직접 구현하는 것이 이 프로젝트의 조건이다.

### 23.2 그래프 기본

```python
import matplotlib
matplotlib.use("Agg")            # 창을 띄우지 않고 파일로만 저장
import matplotlib.pyplot as plt

months = [1, 2, 3, 4, 5, 6]
temps = [-2.4, 0.4, 5.7, 12.5, 17.8, 22.2]
plt.plot(months, temps)
plt.xlabel("month")
plt.ylabel("temperature")
plt.title("monthly temperature")
plt.savefig("temps.png")
print("saved")
```

```text
saved
```

- `matplotlib.use("Agg")` 줄을 빼고 `plt.savefig` 대신 `plt.show()`를 쓰면 창에 그림이 뜬다
- 그래프 안의 한글은 글꼴 설정 없이는 깨질 수 있다. 예시는 영문 제목을 썼다

### 23.3 이 프로젝트에서 쓸 numpy와 그래프

리스트로 하는 일을 numpy로 하면:

| 하는 일 | numpy |
|---|---|
| 0으로 채운 배열 | `np.zeros(512)` |
| 0, 1, 2, … | `np.arange(512)` |
| 자리마다 곱하기 | `a * b` |
| 복소 지수 | `np.exp(-2j * np.pi * k / n)` |
| 코사인 | `np.cos(x)` |
| 켤레, 실수부, 크기 | `np.conj(a)`, `a.real`, `np.abs(a)` |
| 가장 큰 차이 | `np.max(np.abs(a - b))` |
| 반올림 | `np.rint(a)` |
| 범위 자르기 | `np.clip(a, -32768, 32767)` |
| 16bit 정수로 | `a.astype(np.int16)` |
| 바이트와 배열 사이 | `np.frombuffer(raw, dtype="<i2")`, `a.astype("<i2").tobytes()` |
| 거의 같은지 | `np.allclose(a, b)` |
| 배열 잇기 | `np.concatenate([a, b])` |

```python
import numpy as np

k = np.arange(4)
w = np.exp(-2j * np.pi * k / 4)
print(np.round(w, 6))

a = np.array([1.4, -2.6, 40000.0, -40000.0])
print(np.rint(a))
print(np.clip(np.rint(a), -32768, 32767).astype(np.int16))
print(np.allclose([1.0, 2.0], [1.0, 2.0 + 1e-12]))
print(np.concatenate([np.zeros(2), np.array([5.0, 6.0])]))
```

```text
[ 1.+0.j  0.-1.j -1.-0.j -0.+1.j]
[ 1.e+00 -3.e+00  4.e+04 -4.e+04]
[     1     -3  32767 -32768]
True
[0. 0. 5. 6.]
```

> [!IMPORTANT]
> **쓰지 않는 함수**: `np.fft` 아래의 모든 함수(FFT, IFFT)와 `np.hanning`, `np.hamming`, `np.blackman`(윈도우). 이 프로젝트는 이것들을 직접 만든다. 만든 것이 맞는지는 §22의 `testvec`로 확인한다.

두 신호와 그 차이를 위아래로 그린다.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

original = [0, 3, 5, 3, 0, -3, -5, -3]
restored = [0, 3, 5, 3, 0, -3, -5, -2]
difference = [r - o for o, r in zip(original, restored)]

plt.subplot(2, 1, 1)                 # 위아래 두 칸 중 첫째
plt.plot(original, label="original")
plt.plot(restored, label="restored")
plt.legend()
plt.subplot(2, 1, 2)                 # 둘째
plt.plot(difference)
plt.xlabel("sample")
plt.savefig("compare.png")
print(difference)
```

```text
[0, 0, 0, 0, 0, 0, 0, 1]
```

---

## 참조한 원문

| 원문 | 쓴 곳 |
|---|---|
| Python 3.11 문서 "Built-in Types" (`https://docs.python.org/3.11/library/stdtypes.html`) | §2, §4.2, §12, §15, §19 |
| Python 3.11 문서 "cmath — Mathematical functions for complex numbers" (`https://docs.python.org/3.11/library/cmath.html`) | §12 |
| Python 3.11 문서 "wave — Read and write WAV files" (`https://docs.python.org/3.11/library/wave.html`) | §16 |
| Python 3.11 문서 "filecmp — File and Directory Comparisons" (`https://docs.python.org/3.11/library/filecmp.html`) | §22 |
| Python 3.11 문서 "`__main__` — Top-level code environment" (`https://docs.python.org/3.11/library/__main__.html`) | §8.1 |
| 예시 실행 출력 ([첨부_이력_문법 예시 실행 출력.txt](../tasks/가이드/20260928_1728_pr-guide-and-setup/첨부_이력_문법%20예시%20실행%20출력.txt)) | 전 절. `struct`, `array`, `deque`, `os.path`, `sys.argv`, numpy 예시는 문서를 인용하지 않고 실행 결과로 확인했다 |
