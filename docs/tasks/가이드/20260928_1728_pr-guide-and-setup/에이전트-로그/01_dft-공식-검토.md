---
name: dft·idft 공식 헤더 검토자
purpose: dft.py 의 dft·idft 위 공식/기호 헤더 블록이 실제 루프 코드와 일치하는지 반증 시도
type: tasks/에이전트-로그
applies_to: [fft-perfect-reconstruction]
maturity: stable
tags: [가이드, 주석 검토]
---

**TL;DR**: dft·idft 헤더의 공식(sin 부호, θ, 합산 범위, 1/N, 복소수 곱의 a b c d 대응)은 코드와 cmath 수치 검증에서 오차 0 으로 일치했다. 틀린 곳은 없고 nit 만 있다. 렌즈 밖에서 print_dft_steps 표 머리글 angle 이 도(degree)를 찍는 불일치 1건을 발견했다.

## 1. 검토 범위와 방법

- 대상: `scratchpad\hdr1\src\dft.py` 5~16행(dft 헤더), 34~48행(idft 헤더)과 각 함수 본문 루프. 읽기 전용, 편집 없음.
- 도구: 프로젝트 venv 의 python, cwd = `scratchpad\hdr1`, `sys.path` 에 `src` 추가. 파일은 만들지 않고 heredoc 표준입력으로만 실행. git 미사용, 설치 없음.
- 반증 방식: 헤더 공식을 cmath 로 그대로 계산해 `dft.dft`, `dft.idft` 출력과 비교. 부호나 c, d 를 일부러 바꾼 변형은 큰 차이가 나는지 확인해 검사가 실제로 민감함을 증명.

## 2. dft 헤더 대조 (dft.py 5~16행 vs 17~31행)

| 헤더 서술 | 코드 근거 | 판정 |
|---|---|---|
| `X[k] = Σ x[n] * (cos(θ) - j*sin(θ))` | 26행 `horizontal_len = x[n] * math.cos(angle)`, 27행 `vertical_len = -x[n] * math.sin(angle)`, 28~29행 각각 `total_re`, `total_im` 에 더함, 30행 `complex(total_re, total_im)` | 일치. 실수부 = Σ x cos, 허수부 = -Σ x sin |
| `θ = 2πkn / N` | 25행 `angle = (2 * math.pi * k * n) / N` | 일치 (곱의 순서 2, π, k, n 도 같음) |
| `합산 범위: n = 0 ~ N-1` | 24행 `for n in range(N)` | 일치 |
| 기호 N | 19행 `N = len(x)` | 참 |
| 기호 n, k | 21행 k 바깥, 24행 n 안쪽 | 참 |
| 기호 x[n] 입력 샘플값, X[k] 크기와 위상 정보를 담은 복소수 | 30행 반환 원소가 complex | 참 |
| 기호 j² = -1 | 코드에 `j` 변수 없음(complex 컨테이너만 사용) | 문제 없음. 수식 기호로만 쓰임 |
| 형식 | 공식 줄, 빈 `#` 줄, 기호 줄 순서. 함수 def 바로 위 | 일치 |
| 기호 사용 여부 | N, n, k, x[n], X[k], j 모두 공식에서 사용 | 일치 |

수치 확인 (길이 8 난수 입력, seed 1):

```
dft formula vs code max diff: 0.0
dft with +sin variant vs code max diff (should be large): 1.0125296994041442
type X[k]: complex len: 8
numpy fft diff: 1.9860273225978185e-15
N = 1 dft diff 0.0 / N = 2 0.0 / N = 5 0.0 / N = 16 0.0
int input ok: (-2.0000000000000004+1.9999999999999996j)
complex input dft vs formula diff: 2.2887833992611187e-16
```

해석: 공식은 코드와 완전히 같고, 부호를 +sin 으로 바꾸면 차이가 약 1.01 로 커지므로 `-j*sin` 이 실제 부호임이 검증됐다. 복소수 입력을 넣어도 수식 값은 같다(오차 2e-16).

## 3. idft 헤더 대조 (dft.py 34~48행 vs 49~63행)

| 헤더 서술 | 코드 근거 | 판정 |
|---|---|---|
| `x[n] = (1 / N) * Σ X[k] * (cos(θ) + j*sin(θ))` | 58행 `arrow_re = math.cos(angle)`, 59행 `arrow_im = math.sin(angle)` (부호 +), 62행 `complex(total_re / N, total_im / N)` | 일치 |
| `θ = 2πkn / N` | 57행 `angle = (2 * math.pi * k * n) / N` | 일치 |
| `합산 범위: k = 0 ~ N-1` | 56행 `for k in range(N)` (안쪽), 53행 n 바깥 | 일치 |
| `복소수 곱: (a + j*b) * (c + j*d) = (ac - bd) + j*(ad + bc)` | 60행 `X[k].real * arrow_re - X[k].imag * arrow_im` = a·c - b·d, 61행 `X[k].real * arrow_im + X[k].imag * arrow_re` = a·d + b·c | 일치. a = X[k].real, b = X[k].imag, c = arrow_re = cos, d = arrow_im = sin. 항 순서(ad + bc)도 같음 |
| 항등식 자체 | `(0.3-0.7j)*(0.5+0.2j)` = (0.29-0.29j), 풀어 쓴 식도 같은 값 | 참 |
| 기호 a, b = X[k] 의 실수부와 허수부 | 위 대응 | 참 |
| 기호 c, d = cos(θ) 와 sin(θ) | 위 대응 | 참 |
| 기호 x[n] 되돌린 샘플값 (복소수) | 62행 반환 원소가 complex, 허수부 최대 0.52 (임의 복소수 입력) | 참 |
| 기호 X[k], N, n, k, j | N = len(X) (51행), 나머지 일치 | 참 |
| 기호 사용 여부 | N, n, k, X[k], x[n], j, a, b, c, d 모두 공식에서 사용 | 일치 |

수치 확인 (길이 8 난수 복소수 입력):

```
idft formula vs code max diff: 0.0
type x[n]: complex imag max: 0.5232646420270229
identity (c=cos,d=sin) vs code: 0.0
identity (c=sin,d=cos) vs code (should be large): 0.7569128559980035
identity itself: (0.29-0.29j) (0.29-0.29j)
roundtrip max real diff: 8.049116928532385e-16 max imag: 2.0122792321330962e-16
numpy ifft diff: 6.112531465858672e-16
N=5 idft diff 5.551115123125783e-17
```

해석: 공식은 코드와 완전히 같다. c 와 d 를 바꾸면 차이가 약 0.76 으로 커지므로 `c = cos, d = sin` 대응이 유일하게 맞다.

## 4. 발견 사항

### 4.1 렌즈 안 (dft·idft 헤더): 틀린 곳 없음, nit 만 있음

- 틀림(wrong) 0건, 오해 소지(misleading) 0건.
- nit 1. 두 헤더 모두 `θ` 가 기호 블록에 없다. 정의는 공식 둘째 줄(`θ = 2πkn / N`)에 있어 규칙 위반으로 단정하기는 어렵고 취향 수준이다. 다른 헤더(`B` → "코드의 bit_count", `W[k]` → "코드의 table[k]")는 코드 이름을 기호 줄에 적는 관례가 있으므로 맞추려면 `θ : 각도 (코드의 angle, 라디안)` 을 추가한다.
- nit 2. dft 기호 `x[n] : n번째 입력 샘플값` 은 실수 입력을 전제한다. 코드 주석 22~23행의 "실수부 합", "허수부 합" 은 x[n] 이 실수일 때만 그렇다(복소수 입력이면 두 합이 complex 가 되나 합친 값은 수식과 같아 계산은 맞다). 전제를 적으려면 `x[n] : n번째 입력 샘플값 (실수)`.
- nit 3. idft 본문의 인라인 주석 50행 "X[k] 에 화살표를 곱해" 와 58~59행 "화살표의 가로/세로" 에서 "화살표" 는 헤더 어디에도 정의가 없다. 헤더의 c, d 줄에 코드 이름을 붙이면 연결된다: `c, d : cos(θ) 와 sin(θ) (코드의 arrow_re, arrow_im)`.
- nit 4. 서식. 57행 `... / N     # 칸 k, 샘플 n 의 각도 (라디안)` 은 `#` 앞 공백이 5칸이라 나머지 줄(2칸)과 다르고, 60~61행은 `X[k].imag  * arrow_im`, `X[k].imag  * arrow_re` 로 `.imag` 뒤 공백이 두 칸이다. 동작과 주석 정확성에는 영향이 없다.

### 4.2 렌즈 밖에서 눈에 띈 것 (print_dft_steps 등)

- 오해 소지(misleading). `print_dft_steps` 표 머리글 92행의 `angle` 열에는 도(degree) 값이 찍힌다. 같은 함수 94행의 변수 `angle` 은 라디안(주석 "(라디안)")이고, 101행에서 `degree` 를 따로 만들어 출력(102행 `{degree:5.0f}`)한다. 실행 결과 k=1 일 때 n=1 행은 `45`, n=2 행은 `90` 이 찍혔다(라디안이라면 0.7854, 1.5708). 머리글 "angle" 을 보면 코드의 라디안 변수로 오해하기 쉽다. 제안: 머리글을 `deg` 로 바꾼다. 열 폭 5 가 유지되도록 `"  n      x[n]    deg  horizontal_len  vertical_len    total_re    total_im"`.
- nit. 1행 `# 느린 DFT, 역 DFT 와 겹침 없는 복원` 과 main.py 2행 `import dft  # 느린 DFT 와 겹침 없는 복원` 은 새로 추가된 계산 과정 출력(`print_dft_steps`)을 언급하지 않는다. 제안 예: `# 느린 DFT, 역 DFT, 겹침 없는 복원, DFT 계산 과정 출력`.
- 보고하지 않고 넘긴 것: 111행 `n 을 {step} 칸 간격으로` 의 "칸" 은 위쪽 주석의 "칸 k"(주파수 bin) 와 뜻이 다르지만 문맥상 읽힌다. 정확성 문제가 아니므로 제외.

### 4.3 print_dft_steps 간단 확인 (렌즈 밖, 참고)

- 머리글 열 폭과 데이터 서식(`{n:3d}`, `{x[n]:8.4f}`, `{degree:5.0f}`, `{...:14.4f}`, `{...:12.4f}`, `{...:10.4f}`)은 정렬이 맞았다.
- k=1, x=[1..8] 의 출력 `X[1] = (-4, 9.6569)` 은 `np.fft.fft` 결과 `(-4+9.65685424949238j)` 와, k=3 의 `X[3] = (-4, 1.6569)` 도 `(-4+1.6568542494923806j)` 와 같다. 건너뛰기 합은 1 칸 간격 줄에서 `X[k]` 와 같아진다.

## 5. 검증 완료 목록

- dft 헤더 전체(공식 3줄, 기호 6줄, 형식)
- idft 헤더 전체(공식 4줄, 기호 10줄, 형식), 특히 복소수 곱 항등식과 62행의 1/N

## 6. 제안 교체 문구 모음

- dft 기호에 추가: `#     θ    : 각도 (코드의 angle, 라디안)`
- idft 기호에 추가: `#     θ    : 각도 (코드의 angle, 라디안)`
- idft 기호 c, d 줄: `#     c, d : cos(θ) 와 sin(θ) (코드의 arrow_re, arrow_im)`
- dft 기호 x[n] 줄(선택): `#     x[n] : n번째 입력 샘플값 (실수)`
- print_dft_steps 92행 머리글: `"  n      x[n]    deg  horizontal_len  vertical_len    total_re    total_im"`
